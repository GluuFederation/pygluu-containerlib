import os

from ..utils import encode_text
from ..utils import cert_to_truststore

GLUU_COUCHBASE_TRUSTSTORE_PASSWORD = "newsecret"


def get_couchbase_user(manager):
    return os.environ.get("GLUU_COUCHBASE_USER") or manager.config.get("couchbase_server_user")


def get_encoded_couchbase_password(manager):
    password_file = os.environ.get("GLUU_COUCHBASE_PASSWORD_FILE", "/etc/gluu/conf/couchbase_password")

    if not os.path.isfile(password_file):
        return manager.secret.get("encoded_couchbase_server_pw")

    with open(password_file) as f:
        plain = f.read()
        return encode_text(plain, manager.secret.get("encoded_salt"))


def get_couchbase_mappings(persistence_type, ldap_mapping):
    mappings = {
        "default": {
            "bucket": "gluu",
            "mapping": "",
        },
        "user": {
            "bucket": "gluu_user",
            "mapping": "people, groups, authorizations"
        },
        "cache": {
            "bucket": "gluu_cache",
            "mapping": "cache",
        },
        "site": {
            "bucket": "gluu_site",
            "mapping": "cache-refresh",
        },
        "token": {
            "bucket": "gluu_token",
            "mapping": "tokens",
        },
    }

    if persistence_type == "hybrid":
        mappings = {
            name: mapping for name, mapping in mappings.iteritems()
            if name != ldap_mapping
        }

    return mappings


def render_couchbase_properties(manager, src, dest):
    persistence_type = os.environ.get("GLUU_PERSISTENCE_TYPE", "couchbase")
    ldap_mapping = os.environ.get("GLUU_PERSISTENCE_LDAP_MAPPING", "default")
    hostname = os.environ.get("GLUU_COUCHBASE_URL", "localhost")

    _couchbase_mappings = get_couchbase_mappings(persistence_type, ldap_mapping)
    couchbase_buckets = []
    couchbase_mappings = []

    for _, mapping in _couchbase_mappings.iteritems():
        couchbase_buckets.append(mapping["bucket"])

        if not mapping["mapping"]:
            continue

        couchbase_mappings.append("bucket.{0}.mapping: {1}".format(
            mapping["bucket"], mapping["mapping"],
        ))

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
                ),
            }
            fw.write(rendered_txt)


def sync_couchbase_cert(manager):
    cert_file = os.environ.get("GLUU_COUCHBASE_CERT_FILE", "/etc/certs/couchbase.crt")
    if not os.path.isfile(cert_file):
        manager.secret.to_file("couchbase_chain_cert", cert_file)


def sync_couchbase_truststore(manager):
    cert_file = os.environ.get("GLUU_COUCHBASE_CERT_FILE", "/etc/certs/couchbase.crt")
    cert_to_truststore(
        "gluu_couchbase",
        cert_file,
        manager.config.get("couchbaseTrustStoreFn"),
        GLUU_COUCHBASE_TRUSTSTORE_PASSWORD,
    )
