"""This module contains base class for config adapter."""

from __future__ import annotations

from typing import (
    Any,
    NoReturn,
)


class BaseConfig:
    """Base class for config adapter.

    Must be sub-classed per implementation details.
    """

    type = "config"

    def get(self, key: str, default: Any = "") -> NoReturn:
        """Get specific config.

        Subclass **MUST** implement this method.

        :param key: Key name.
        :param default: Default value if key is not exist.
        """
        raise NotImplementedError

    def set(self, key: str, value: Any) -> NoReturn:
        """Set specific config.

        Subclass **MUST** implement this method.

        :param key: Key name.
        :param value: Value of the key.
        """
        raise NotImplementedError

    def all(self):
        # this method is deprecated
        return self.get_all()

    def get_all(self) -> NoReturn:
        """Get all key-value pairs.

        Subclass **MUST** implement this method.
        """
        raise NotImplementedError

    def set_all(self, data: dict[str, Any]) -> NoReturn:
        """Set all key-value pairs.

        Subclass **MUST** implement this method.

        :param data: Key-value pairs.
        """
        raise NotImplementedError
