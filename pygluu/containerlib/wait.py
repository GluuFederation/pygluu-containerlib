# -*- coding: utf-8 -*-
import logging
import os
import sys

import backoff
import ldap3
import requests

from .exceptions import WaitError
from .utils import decode_text
from .utils import as_boolean
from .persistence.couchbase import get_couchbase_user
from .persistence.couchbase import get_couchbase_password

logger = logging.getLogger(__name__)


def get_wait_max_time():
    default = 60 * 5
    try:
        max_time = int(os.environ.get("GLUU_WAIT_MAX_TIME", default))
    except ValueError:
        max_time = default
    return max(1, max_time)


def get_wait_interval():
    default = 5
    try:
        interval = int(os.environ.get("GLUU_WAIT_SLEEP_DURATION", default))
    except ValueError:
        interval = default
    return max(1, interval)


def on_backoff(details):
    details["error"] = sys.exc_info()[1]
    details["kwargs"]["label"] = details["kwargs"].pop("label", "Service")
    logger.warn("{kwargs[label]} is not ready; reason={error}; "
                "retrying in {wait:0.1f} seconds".format(**details))


def on_success(details):
    details["kwargs"]["label"] = details["kwargs"].pop("label", "Service")
    logger.info("{kwargs[label]} is ready".format(**details))


def on_giveup(details):
    details["kwargs"]["label"] = details["kwargs"].pop("label", "Service")
    logger.error("{kwargs[label]} is not ready after "
                 "{elapsed:0.1f} seconds".format(**details))


retry_on_exception = backoff.on_exception(
    backoff.constant,
    Exception,
    max_time=get_wait_max_time,
    on_backoff=on_backoff,
    on_success=on_success,
    on_giveup=on_giveup,
    jitter=None,
    interval=get_wait_interval,
)


@retry_on_exception
def wait_for_config(manager, **kwargs):
    conn_only = as_boolean(kwargs.get("conn_only", False))
    hostname = manager.config.get("hostname")

    if not conn_only and not hostname:
        raise WaitError("Config 'hostname' is not available")


@retry_on_exception
def wait_for_secret(manager, **kwargs):
    conn_only = as_boolean(kwargs.get("conn_only", False))
    ssl_cert = manager.secret.get("ssl_cert")

    if not conn_only and not ssl_cert:
        raise WaitError("Secret 'ssl_cert' is not available")


@retry_on_exception
def wait_for_ldap(manager, **kwargs):
    host = os.environ.get("GLUU_LDAP_URL", "localhost:1636")
    user = manager.config.get("ldap_binddn")
    password = decode_text(manager.secret.get("encoded_ox_ldap_pw"),
                           manager.secret.get("encoded_salt"))

    persistence_type = os.environ.get("GLUU_PERSISTENCE_TYPE", "ldap")
    ldap_mapping = os.environ.get("GLUU_PERSISTENCE_LDAP_MAPPING", "default")
    ldap_server = ldap3.Server(host, 1636, use_ssl=True)

    default_search = ("o=gluu", "(objectClass=gluuConfiguration)")
    if persistence_type == "hybrid":
        search_mapping = {
            "default": default_search,
            "user": ("o=gluu", "(objectClass=gluuGroup)"),
            "site": ("o=site", "(ou=people)"),
            "cache": default_search,
            "token": default_search,
        }
        search = search_mapping[ldap_mapping]
    else:
        search = default_search

    with ldap3.Connection(ldap_server, user, password) as conn:
        conn.search(
            search_base=search[0],
            search_filter=search[1],
            search_scope=ldap3.BASE,
            attributes=['objectClass'],
            size_limit=1,
        )

        if not conn.entries:
            raise WaitError("LDAP is not fully initialized")


@retry_on_exception
def wait_for_ldap_conn(manager, **kwargs):
    host = os.environ.get("GLUU_LDAP_URL", "localhost:1636")
    user = manager.config.get("ldap_binddn")
    password = decode_text(manager.secret.get("encoded_ox_ldap_pw"),
                           manager.secret.get("encoded_salt"))

    ldap_server = ldap3.Server(host, 1636, use_ssl=True)
    search = ("", "(objectClass=*)")

    with ldap3.Connection(ldap_server, user, password) as conn:
        conn.search(
            search_base=search[0],
            search_filter=search[1],
            search_scope=ldap3.BASE,
            attributes=["1.1"],
            size_limit=1,
        )
        if not conn.entries:
            raise WaitError("LDAP is unreachable")


@retry_on_exception
def wait_for_couchbase(manager, **kwargs):
    host = os.environ.get("GLUU_COUCHBASE_URL", "localhost")
    user = get_couchbase_user(manager)
    password = get_couchbase_password(manager)

    persistence_type = os.environ.get("GLUU_PERSISTENCE_TYPE", "couchbase")
    ldap_mapping = os.environ.get("GLUU_PERSISTENCE_LDAP_MAPPING", "default")

    # only `gluu` and `gluu_user` buckets that may have initial data;
    # these data also affected by LDAP mapping selection;
    # by default we will choose the `gluu` bucket
    bucket, key = "gluu", "configuration"

    # if `hybrid` is selected and default mapping is stored in LDAP,
    # the `gluu` bucket won't have data, hence we check the `gluu_user` instead
    if persistence_type == "hybrid" and ldap_mapping == "default":
        bucket, key = "gluu_user", "groups_60B7"

    query = "SELECT objectClass FROM {0} USE KEYS '{1}'".format(bucket, key)

    req = requests.post(
        "https://{0}:18093/query/service".format(host),
        data={"statement": query},
        auth=(user, password),
        verify=False,
    )

    if not req.ok:
        err = req.text or req.reason
        raise WaitError(err)

    # request is OK, but result is not found
    data = req.json()
    if not data["results"]:
        raise WaitError(data["errors"][0]["msg"])


@retry_on_exception
def wait_for_couchbase_conn(manager, **kwargs):
    host = os.environ.get("GLUU_COUCHBASE_URL", "localhost")
    user = get_couchbase_user(manager)
    password = get_couchbase_password(manager)

    req = requests.get(
        "https://{0}:18091/pools/".format(host),
        auth=(user, password),
        verify=False,
    )

    if not req.ok:
        err = req.text or req.reason
        raise WaitError(err)


@retry_on_exception
def wait_for_oxauth(manager, **kwargs):
    addr = os.environ.get("GLUU_OXAUTH_BACKEND", "localhost:8081")
    url = "http://" + addr + "/oxauth/.well-known/openid-configuration"
    req = requests.get(url)

    if not req.ok:
        err = req.text or req.reason
        raise WaitError(err)


@retry_on_exception
def wait_for_oxtrust(manager, **kwargs):
    addr = os.environ.get("GLUU_OXTRUST_BACKEND", "localhost:8082")
    url = "http://{}/identity/restv1/scim-configuration".format(addr)
    req = requests.get(url)

    if not req.ok:
        err = req.text or req.reason
        raise WaitError(err)


def wait_for(manager, deps=None):
    deps = deps or []
    callbacks = {
        "config": {
            "func": wait_for_config,
            "kwargs": {"label": "Config"},
        },
        "config_conn": {
            "func": wait_for_config,
            "kwargs": {"label": "Config", "conn_only": True},
        },
        "ldap": {
            "func": wait_for_ldap,
            "kwargs": {"label": "LDAP"},
        },
        "ldap_conn": {
            "func": wait_for_ldap_conn,
            "kwargs": {"label": "LDAP"},
        },
        "couchbase": {
            "func": wait_for_couchbase,
            "kwargs": {"label": "Couchbase"},
        },
        "couchbase_conn": {
            "func": wait_for_couchbase_conn,
            "kwargs": {"label": "Couchbase"},
        },
        "secret": {
            "func": wait_for_secret,
            "kwargs": {"label": "Secret"},
        },
        "secret_conn": {
            "func": wait_for_secret,
            "kwargs": {"label": "Secret", "conn_only": True},
        },
        "oxauth": {
            "func": wait_for_oxauth,
            "kwargs": {"label": "oxAuth"},
        },
        "oxtrust": {
            "func": wait_for_oxtrust,
            "kwargs": {"label": "oxTrust"},
        },
    }

    for dep in deps:
        callback = callbacks.get(dep)
        if not callback:
            logger.warn("Unsupported callback for {} dependency".format(dep))
            continue
        callback["func"](manager, **callback["kwargs"])
