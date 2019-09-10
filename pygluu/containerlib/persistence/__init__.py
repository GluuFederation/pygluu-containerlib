import os

from .couchbase import render_couchbase_properties  # noqa
from .couchbase import sync_couchbase_cert  # noqa
from .couchbase import sync_couchbase_truststore  # noqa
from .hybrid import render_hybrid_properties  # noqa
from .ldap import render_ldap_properties  # noqa
from .ldap import sync_ldap_truststore  # noqa


def render_salt(manager, src, dest):
    encode_salt = manager.secret.get("encoded_salt")

    with open(src) as f:
        txt = f.read()

    with open(dest, "w") as f:
        rendered_txt = txt % {"encode_salt": encode_salt}
        f.write(rendered_txt)


def render_gluu_properties(src, dest):
    with open(src) as f:
        txt = f.read()

    with open(dest, "w") as f:
        rendered_txt = txt % {
            "gluuOptPythonFolder": "/opt/gluu/python",
            "certFolder": "/etc/certs",
            "persistence_type": os.environ.get("GLUU_PERSISTENCE_TYPE", "ldap"),
        }
        f.write(rendered_txt)
