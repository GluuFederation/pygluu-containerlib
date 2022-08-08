"""This module contains base class for config adapter."""

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

    def all(self) -> NoReturn:
        """Get all config.

        Subclass **MUST** implement this method.
        """
        raise NotImplementedError
