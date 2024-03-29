"""This module contains helpers to validate things."""

from typing import NoReturn

from pygluu.containerlib.constants import (
    PERSISTENCE_TYPES,
    PERSISTENCE_LDAP_MAPPINGS,
)
from pygluu.containerlib.constants import PERSISTENCE_SQL_DIALECTS


def validate_persistence_type(type_: str) -> NoReturn:
    r"""Validate persistence type.

    Supported types:
    - ``couchbase``
    - ``hybrid``
    - ``ldap``
    - ``spanner``
    - ``sql``

    :param type\_: Persistence type.
    """
    if type_ not in PERSISTENCE_TYPES:
        types = ", ".join(PERSISTENCE_TYPES)

        raise ValueError(
            f"Unsupported persistence type {type_}; "
            f"please choose one of {types}"
        )


def validate_persistence_ldap_mapping(type_: str, ldap_mapping: str) -> NoReturn:
    """Validate persistence mapping for ldap."""
    if type_ == "hybrid" and ldap_mapping not in PERSISTENCE_LDAP_MAPPINGS:
        mappings = ", ".join(PERSISTENCE_LDAP_MAPPINGS)

        raise ValueError(
            f"Unsupported persistence ldap mapping {ldap_mapping}; "
            f"please choose one of {mappings}"
        )


def validate_persistence_sql_dialect(dialect: str) -> NoReturn:
    """Validate SQL dialect.

    :param dialect: Dialect of SQL.
    """
    if dialect not in PERSISTENCE_SQL_DIALECTS:
        dialects = ", ".join(PERSISTENCE_SQL_DIALECTS)
        raise ValueError(
            f"Unsupported persistence sql dialects; "
            f"please choose one of {dialects}"
        )
