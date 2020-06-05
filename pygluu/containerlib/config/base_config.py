from typing import (
    Any,
    NoReturn,
    Optional,
)


class BaseConfig(object):
    """Base class for config adapter. Must be sub-classed per
    implementation details.
    """

    type = "config"

    def get(self, key: str, default: Optional[Any] = None) -> NoReturn:
        """Get specific config.

        Subclass __MUST__ implement this method.
        """
        raise NotImplementedError

    def set(self, key: str, value: Any) -> NoReturn:
        """Set specific config.

        Subclass __MUST__ implement this method.
        """
        raise NotImplementedError

    def all(self) -> NoReturn:
        """Get all config as ``dict`` type.

        Subclass __MUST__ implement this method.
        """
        raise NotImplementedError
