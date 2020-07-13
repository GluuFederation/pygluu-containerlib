"""
pygluu.containerlib.persistence.hybrid
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This module contains various helpers related to hybrid (LDAP + Couchbase) persistence.
"""

import os

from .couchbase import get_couchbase_mappings
from ..constants import COUCHBASE_MAPPINGS


def render_hybrid_properties(dest: str) -> None:
    persistence_type = os.environ.get("GLUU_PERSISTENCE_TYPE", "couchbase")
    ldap_mapping = os.environ.get("GLUU_PERSISTENCE_LDAP_MAPPING", "default")

    if ldap_mapping == "default":
        default_storage = "ldap"
    else:
        default_storage = "couchbase"

    _couchbase_mappings = get_couchbase_mappings(persistence_type, ldap_mapping)

    couchbase_mappings = ", ".join(filter(None, [
        mapping["mapping"]
        for name, mapping in _couchbase_mappings.items()
        if name != ldap_mapping
    ]))
    ldap_mappings = COUCHBASE_MAPPINGS.get(ldap_mapping, {}).get("mapping") or "default"

    out = "\n".join([
        "storages: ldap, couchbase",
        f"storage.default: {default_storage}",
        f"storage.ldap.mapping: {ldap_mappings}",
        f"storage.couchbase.mapping: {couchbase_mappings}",
    ])

    with open(dest, "w") as fw:
        fw.write(out)
