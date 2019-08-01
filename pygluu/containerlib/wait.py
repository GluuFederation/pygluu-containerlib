# -*- coding: utf-8 -*-
import logging
import os
import sys
import time

import ldap3
import requests

from .utils import decode_text
from .utils import as_boolean

logger = logging.getLogger(__name__)


def wait_for_config(manager, max_wait_time, sleep_duration, **kwargs):
    conn_only = as_boolean(kwargs.get("conn_only", False))

    for i in range(0, max_wait_time, sleep_duration):
        try:
            reason = "config 'hostname' is not available"
            hostname = manager.config.get("hostname")

            if conn_only:
                # we don't care about the result, we only need to
                # test the connection
                connected = True
            else:
                connected = bool(hostname)

            if connected:
                logger.info("Config backend is ready.")
                return
        except Exception as exc:
            reason = exc

        logger.warn("Config backend is not ready; reason={}; "
                    "retrying in {} seconds.".format(reason, sleep_duration))
        time.sleep(sleep_duration)

    logger.error("Config backend is not ready after {} seconds.".format(max_wait_time))
    sys.exit(1)


def wait_for_secret(manager, max_wait_time, sleep_duration, **kwargs):
    conn_only = as_boolean(kwargs.get("conn_only", False))

    for i in range(0, max_wait_time, sleep_duration):
        try:
            reason = "secret 'ssl_cert' is not available"
            ssl_cert = manager.secret.get("ssl_cert")

            if conn_only:
                # we don't care about the result, we only need to
                # test the connection
                connected = True
            else:
                connected = bool(ssl_cert)

            if connected:
                logger.info("Secret backend is ready.")
                return
        except Exception as exc:
            reason = exc

        logger.warn("Secret backend is not ready; reason={}; "
                    "retrying in {} seconds.".format(reason, sleep_duration))
        time.sleep(sleep_duration)

    logger.error("Secret backend is not ready after {} seconds.".format(max_wait_time))
    sys.exit(1)


def wait_for_ldap(manager, max_wait_time, sleep_duration, **kwargs):
    persistence_type = os.environ.get("GLUU_PERSISTENCE_TYPE", "ldap")
    ldap_url = os.environ.get("GLUU_LDAP_URL", "localhost:1636")
    ldap_mapping = os.environ.get("GLUU_PERSISTENCE_LDAP_MAPPING", "default")

    ldap_bind_dn = manager.config.get("ldap_binddn")
    ldap_password = decode_text(manager.secret.get("encoded_ox_ldap_pw"),
                                manager.secret.get("encoded_salt"))

    ldap_server = ldap3.Server(ldap_url, 1636, use_ssl=True)

    # check the entries few times, to ensure OpenDJ is running after importing
    # initial data;
    successive_entries_check = 0

    default_search = ("o=gluu", "(objectClass=gluuConfiguration)")
    if persistence_type == "hybrid":
        search_mapping = {
            "default": default_search,
            "user": ("o=gluu", "(objectClass=gluuGroup)"),
            "site": ("o=site", "(ou=people)"),
            "cache": default_search,
            "statistic": ("o=metric", "(ou=statistic)"),
            "authorization": default_search,
            "tokens": default_search,
            "clients": ("o=gluu", "(objectClass=oxAuthClient)"),
        }
        search = search_mapping[ldap_mapping]
    else:
        search = default_search

    for i in range(0, max_wait_time, sleep_duration):
        try:
            if successive_entries_check >= 3:
                logger.info("LDAP is ready")
                return

            reason = "LDAP is not fully initialized yet"
            with ldap3.Connection(
                    ldap_server,
                    ldap_bind_dn,
                    ldap_password) as ldap_connection:

                ldap_connection.search(
                    search_base=search[0],
                    search_filter=search[1],
                    search_scope=ldap3.SUBTREE,
                    attributes=['objectClass'],
                    size_limit=1,
                )

                if ldap_connection.entries:
                    successive_entries_check += 1
        except Exception as exc:
            reason = exc

        logger.warn("LDAP backend is not ready; reason={}; "
                    "retrying in {} seconds.".format(reason, sleep_duration))
        time.sleep(sleep_duration)

    logger.error("LDAP not ready, after " + str(max_wait_time) + " seconds.")
    sys.exit(1)


def _check_couchbase_document(host, user, password, max_wait_time, sleep_duration):
    persistence_type = os.environ.get("GLUU_PERSISTENCE_TYPE", "ldap")
    ldap_mapping = os.environ.get("GLUU_PERSISTENCE_LDAP_MAPPING", "default")

    # only `gluu` and `gluu_user` buckets that may have initial data
    # these data also affected by LDAP mapping selection;
    # by default we will choose the `gluu` bucket
    bucket, key = "gluu", "_"

    # if `hybrid` is selected and default mapping is stored in LDAP,
    # the `gluu` bucket won't have data, hence we check the `gluu_user`
    # instead
    if persistence_type == "hybrid" and ldap_mapping == "default":
        bucket, key = "gluu_user", "groups_60B7"
    query = "SELECT objectClass FROM {0} USE KEYS '{1}'".format(bucket, key)

    # check the entries few times to ensure Couchbase document is actually ready
    successive_entries_check = 0

    for i in range(0, max_wait_time, sleep_duration):
        try:
            if successive_entries_check >= 3:
                logger.info("Couchbase is ready")
                return

            reason = "Couchbase is not fully initialized yet"
            req = requests.post(
                "https://{0}:18093/query/service".format(host),
                data={"statement": query},
                auth=(user, password),
                verify=False,
            )
            if req.ok and req.json()["results"]:
                successive_entries_check += 1
        except Exception as exc:
            reason = exc

        logger.warn("Couchbase backend is not ready; reason={}; "
                    "retrying in {} seconds.".format(reason, sleep_duration))
        time.sleep(sleep_duration)

    logger.error("Couchbase backend is not ready after {} seconds.".format(max_wait_time))
    sys.exit(1)


def _check_couchbase_connection(host, user, password, max_wait_time, sleep_duration):
    for i in range(0, max_wait_time, sleep_duration):
        try:
            reason = "Couchbase is not initialized yet"
            req = requests.get(
                "https://{0}:18091/pools/".format(host),
                auth=(user, password),
                verify=False,
            )
            if req.ok:
                logger.info("Couchbase is ready")
                return
        except Exception as exc:
            reason = exc

        logger.warn("Couchbase backend is not ready; reason={}; "
                    "retrying in {} seconds.".format(reason, sleep_duration))
        time.sleep(sleep_duration)

    logger.error("Couchbase backend is not ready after {} seconds.".format(max_wait_time))
    sys.exit(1)


def wait_for_couchbase(manager, max_wait_time, sleep_duration, **kwargs):
    conn_only = as_boolean(kwargs.get("conn_only", False))
    host = os.environ.get("GLUU_COUCHBASE_URL", "localhost")
    user = manager.config.get("couchbase_server_user")
    password = decode_text(manager.secret.get("encoded_couchbase_server_pw"),
                           manager.secret.get("encoded_salt"))

    if conn_only:
        callback = _check_couchbase_connection
    else:
        callback = _check_couchbase_document
    callback(host, user, password, max_wait_time, sleep_duration)


def wait_for_oxauth(manager, max_wait_time, sleep_duration, **kwargs):
    addr = os.environ.get("GLUU_OXAUTH_BACKEND", "localhost:8081")
    url = "http://" + addr + "/oxauth/.well-known/openid-configuration"

    for i in range(0, max_wait_time, sleep_duration):
        try:
            r = requests.get(url)
            if r.ok:
                logger.info("oxAuth is ready")
                return
            else:
                logger.warn(
                    "oxAuth is not ready; retrying in {} seconds".format(sleep_duration)
                )
        except Exception as exc:
            logger.warn(
                "oxAuth is not ready; reason={}; "
                "retrying in {} seconds".format(exc.message, sleep_duration)
            )
        time.sleep(sleep_duration)

    logger.error("oxAuth is not ready, after {} seconds.".format(max_wait_time))
    sys.exit(1)


def wait_for_oxtrust(manager, max_wait_time, sleep_duration, **kwargs):
    addr = os.environ.get("GLUU_OXTRUST_BACKEND", "localhost:8082")
    url = "http://{}/identity/restv1/scim-configuration".format(addr)

    for i in range(0, max_wait_time, sleep_duration):
        try:
            r = requests.get(url)
            if r.ok:
                logger.info("oxTrust is ready")
                return
            else:
                logger.warn(
                    "oxTrust is not ready; retrying in {} seconds".format(sleep_duration)
                )
        except Exception as exc:
            logger.warn(
                "oxTrust is not ready; error={}; "
                "retrying in {} seconds".format(exc.message, sleep_duration)
            )
        time.sleep(sleep_duration)

    logger.error("oxTrust is not ready, after {} seconds.".format(max_wait_time))
    sys.exit(1)


def wait_for(manager, deps=None, conn_only=None):
    deps = deps or []
    conn_only = conn_only or []
    callbacks = {
        "config": wait_for_config,
        "couchbase": wait_for_couchbase,
        "ldap": wait_for_ldap,
        "secret": wait_for_secret,
        "oxauth": wait_for_oxauth,
        "oxtrust": wait_for_oxtrust,
    }

    try:
        max_wait_time = int(os.environ.get("GLUU_WAIT_MAX_TIME", 300))
    except ValueError:
        max_wait_time = 300

    try:
        sleep_duration = int(os.environ.get("GLUU_WAIT_SLEEP_DURATION", 5))
    except ValueError:
        sleep_duration = 5

    for dep in deps:
        callback = callbacks.get(dep)
        if not callable(callback):
            logger.warn("unable to find callback for {} dependency".format(dep))
            continue

        kwargs = {}
        if dep in conn_only:
            kwargs["conn_only"] = True

        callback(manager, max_wait_time, sleep_duration, **kwargs)
