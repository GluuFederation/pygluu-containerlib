import os

import six

from .couchbase import get_couchbase_mappings


def render_hybrid_properties(dest):
    persistence_type = os.environ.get("GLUU_PERSISTENCE_TYPE", "couchbase")
    ldap_mapping = os.environ.get("GLUU_PERSISTENCE_LDAP_MAPPING", "default")

    _couchbase_mappings = get_couchbase_mappings(persistence_type, ldap_mapping)

    if ldap_mapping == "default":
        default_storage = "ldap"
    else:
        default_storage = "couchbase"

    couchbase_mappings = [
        mapping["mapping"] for name, mapping in six.iteritems(_couchbase_mappings)
        if name != ldap_mapping
    ]

    out = "\n".join([
        "storages: ldap, couchbase",
        "storage.default: {}".format(default_storage),
        "storage.ldap.mapping: {}".format(ldap_mapping),
        "storage.couchbase.mapping: {}".format(
            ", ".join(filter(None, couchbase_mappings))
        ),
    ]).replace("user", "people, groups")

    with open(dest, "w") as fw:
        fw.write(out)
