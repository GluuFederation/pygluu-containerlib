"""
pygluu.containerlib.config.base_config
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This module contains base class for config adapter.
"""

from typing import (
    Any,
    NoReturn,
)


class BaseConfig:
    """Base class for config adapter. Must be sub-classed per
    implementation details.
    """

    type = "config"  # noqa: A003

    def get(self, key: str, default: Any = None) -> NoReturn:
        """Get specific config.

        Subclass **MUST** implement this method.
        """
        raise NotImplementedError

    def set(self, key: str, value: Any) -> NoReturn:  # noqa: A003
        """Set specific config.

        Subclass **MUST** implement this method.
        """
        raise NotImplementedError

    def all(self) -> NoReturn:  # noqa: A003
        """Get all config.

        Subclass **MUST** implement this method.
        """
        raise NotImplementedError
