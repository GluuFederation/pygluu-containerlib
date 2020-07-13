"""
pygluu.containerlib.persistence.couchbase
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This module contains various helpers related to Couchbase persistence.
"""

import logging
import os
from functools import partial
from typing import Dict

import requests

from ..utils import (
    encode_text,
    cert_to_truststore,
)
from ..constants import COUCHBASE_MAPPINGS

GLUU_COUCHBASE_TRUSTSTORE_PASSWORD = "newsecret"

logger = logging.getLogger(__name__)


def get_couchbase_user(manager=None) -> str:
    return os.environ.get("GLUU_COUCHBASE_USER", "admin")


def get_couchbase_password(manager, plaintext: bool = True) -> str:
    password_file = os.environ.get(
        "GLUU_COUCHBASE_PASSWORD_FILE", "/etc/gluu/conf/couchbase_password"
    )

    with open(password_file) as f:
        password = f.read().strip()
        if not plaintext:
            password = encode_text(password, manager.secret.get("encoded_salt")).decode()
        return password


get_encoded_couchbase_password = partial(get_couchbase_password, plaintext=False)


def get_couchbase_mappings(persistence_type: str, ldap_mapping: str) -> Dict[str, str]:
    if persistence_type == "hybrid":
        return {
            name: mapping
            for name, mapping in COUCHBASE_MAPPINGS.items()
            if name != ldap_mapping
        }
    return COUCHBASE_MAPPINGS


def get_couchbase_conn_timeout() -> int:
    default = 10000

    try:
        val = int(os.environ.get("GLUU_COUCHBASE_CONN_TIMEOUT", default))
    except ValueError:
        val = default
    return val


def get_couchbase_conn_max_wait() -> int:
    default = 20000

    try:
        val = int(os.environ.get("GLUU_COUCHBASE_CONN_MAX_WAIT", default))
    except ValueError:
        val = default
    return val


def get_couchbase_scan_consistency() -> str:
    opts = ("not_bounded", "request_plus", "statement_plus")
    default = "not_bounded"
    opt = os.environ.get("GLUU_COUCHBASE_SCAN_CONSISTENCY", default)
    if opt not in opts:
        opt = default
    return opt


def render_couchbase_properties(manager, src: str, dest: str) -> None:
    persistence_type = os.environ.get("GLUU_PERSISTENCE_TYPE", "couchbase")
    ldap_mapping = os.environ.get("GLUU_PERSISTENCE_LDAP_MAPPING", "default")
    hostname = os.environ.get("GLUU_COUCHBASE_URL", "localhost")

    _couchbase_mappings = get_couchbase_mappings(persistence_type, ldap_mapping)
    couchbase_buckets = []
    couchbase_mappings = []

    for _, mapping in _couchbase_mappings.items():
        couchbase_buckets.append(mapping["bucket"])

        if not mapping["mapping"]:
            continue

        couchbase_mappings.append(
            "bucket.{0}.mapping: {1}".format(mapping["bucket"], mapping["mapping"],)
        )

    # always have `gluu` as default bucket
    if "gluu" not in couchbase_buckets:
        couchbase_buckets.insert(0, "gluu")

    with open(src) as fr:
        txt = fr.read()

        with open(dest, "w") as fw:
            rendered_txt = txt % {
                "hostname": hostname,
                "couchbase_server_user": get_couchbase_user(manager),
                "encoded_couchbase_server_pw": get_encoded_couchbase_password(manager),
                "couchbase_buckets": ", ".join(couchbase_buckets),
                "default_bucket": "gluu",
                "couchbase_mappings": "\n".join(couchbase_mappings),
                "encryption_method": "SSHA-256",
                "ssl_enabled": "true",
                "couchbaseTrustStoreFn": manager.config.get("couchbaseTrustStoreFn"),
                "encoded_couchbaseTrustStorePass": encode_text(
                    GLUU_COUCHBASE_TRUSTSTORE_PASSWORD,
                    manager.secret.get("encoded_salt"),
                ).decode(),
                "couchbase_conn_timeout": get_couchbase_conn_timeout(),
                "couchbase_conn_max_wait": get_couchbase_conn_max_wait(),
                "couchbase_scan_consistency": get_couchbase_scan_consistency(),
            }
            fw.write(rendered_txt)


def sync_couchbase_cert(manager=None) -> str:
    cert_file = os.environ.get("GLUU_COUCHBASE_CERT_FILE", "/etc/certs/couchbase.crt")
    with open(cert_file) as f:
        return f.read()


def sync_couchbase_truststore(manager, dest: str = "") -> None:
    cert_file = os.environ.get("GLUU_COUCHBASE_CERT_FILE", "/etc/certs/couchbase.crt")
    dest = dest or manager.config.get("couchbaseTrustStoreFn")
    cert_to_truststore(
        "gluu_couchbase", cert_file, dest, GLUU_COUCHBASE_TRUSTSTORE_PASSWORD,
    )


class BaseClient(object):
    def __init__(self, hosts, user, password):
        self._hosts = hosts
        self.host = None
        self.user = user
        self.password = password

    def resolve_host(self):
        hosts = filter(None, map(lambda host: host.strip(), self._hosts.split(",")))

        for _host in hosts:
            try:
                resp = self.healthcheck(_host)
                if resp.ok:
                    self.host = _host
                    return self.host

                logger.warning(
                    "Unable to connect to {}:{}; reason={}".format(
                        _host, self.port, resp.reason
                    )
                )
            except Exception as exc:
                logger.warning(
                    "Unable to connect to {}:{}; reason={}".format(
                        _host, self.port, exc
                    )
                )

    def healthcheck(self, host):
        raise NotImplementedError

    def exec_api(self, path, **kwargs):
        raise NotImplementedError


class N1qlClient(BaseClient):
    port = 18093

    def healthcheck(self, host):
        import urllib3

        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        return requests.post(
            "https://{0}:{1}/query/service".format(host, self.port),
            data={"statement": "SELECT status FROM system:indexes LIMIT 1"},
            auth=(self.user, self.password),
            verify=False,
            timeout=10,
        )

    def exec_api(self, path, **kwargs):
        data = kwargs.get("data", {})
        verify = kwargs.get("verify", False)

        resp = requests.post(
            "https://{0}:{1}/{2}".format(self.host, self.port, path),
            data=data,
            auth=(self.user, self.password),
            verify=verify,
        )
        return resp


class RestClient(BaseClient):
    port = 18091

    def healthcheck(self, host):
        import urllib3

        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        return requests.get(
            "https://{0}:{1}/pools/".format(host, self.port),
            auth=(self.user, self.password),
            verify=False,
            timeout=10,
        )

    def exec_api(self, path, **kwargs):
        data = kwargs.get("data", {})
        verify = kwargs.get("verify", False)
        method = kwargs.get("method")

        callbacks = {
            "GET": requests.get,
            "POST": partial(requests.post, data=data),
            "PUT": partial(requests.put, data=data),
        }

        req = callbacks.get(method)
        assert callable(req), "Unsupported method {}".format(method)

        resp = req(
            "https://{0}:{1}/{2}".format(self.host, self.port, path),
            auth=(self.user, self.password),
            verify=verify,
        )
        return resp


class CouchbaseClient:
    def __init__(self, hosts, user, password):
        self.rest_client = RestClient(hosts, user, password)
        self.rest_client.resolve_host()
        assert (
            self.rest_client.host
        ), "Unable to resolve host for data service from {} list".format(hosts)

        self.n1ql_client = N1qlClient(hosts, user, password)
        self.n1ql_client.resolve_host()
        assert (
            self.n1ql_client.host
        ), "Unable to resolve host for query service from {} list".format(hosts)

    def get_buckets(self):
        return self.rest_client.exec_api("pools/default/buckets", method="GET",)

    def add_bucket(self, name, memsize=100, type_="couchbase"):
        return self.rest_client.exec_api(
            "pools/default/buckets",
            data={
                "name": name,
                "bucketType": type_,
                "ramQuotaMB": memsize,
                "authType": "sasl",
            },
            method="POST",
        )

    def get_system_info(self):
        sys_info = {}
        resp = self.rest_client.exec_api("pools/default", method="GET",)

        if resp.ok:
            sys_info = resp.json()
        return sys_info

    def exec_query(self, query):
        data = {"statement": query}
        return self.n1ql_client.exec_api("query/service", data=data)

    def create_user(self, username, password, fullname, roles):
        data = {
            "name": fullname,
            "password": password,
            "roles": roles,
        }
        return self.rest_client.exec_api(
            "settings/rbac/users/local/{}".format(username), data=data, method="PUT",
        )
