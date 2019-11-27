# -*- coding: utf-8 -*-
import os

from .couchbase import (  # noqa
    render_couchbase_properties,
    sync_couchbase_cert,
    sync_couchbase_truststore,
)
from .hybrid import render_hybrid_properties  # noqa
from .ldap import (  # noqa
    render_ldap_properties,
    sync_ldap_truststore,
)


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
