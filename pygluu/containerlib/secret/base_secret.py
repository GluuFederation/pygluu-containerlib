"""
pygluu.containerlib.secret.base_secret
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This module contains base class for secret adapter.
"""

from typing import (
    Any,
    NoReturn,
)


class BaseSecret(object):
    """Base class for secret adapter. Must be sub-classed per
    implementation details.
    """

    type = "secret"  # noqa: A003

    def get(self, key: str, default: Any = None) -> NoReturn:
        """Get specific secret.

        Subclass **MUST** implement this method.
        """
        raise NotImplementedError

    def set(self, key: str, value: Any) -> NoReturn:  # noqa: A003
        """Set specific secret.

        Subclass **MUST** implement this method.
        """
        raise NotImplementedError

    def all(self) -> NoReturn:  # noqa: A003
        """Get all secrets.

        Subclass **MUST** implement this method.
        """
        raise NotImplementedError
