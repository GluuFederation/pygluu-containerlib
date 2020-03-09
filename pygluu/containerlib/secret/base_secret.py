from typing import (
    Any,
    NoReturn,
    Optional,
)


class BaseSecret(object):
    """Base class for secret adapter. Must be sub-classed per
    implementation details.
    """
    type = "secret"

    def get(self, key: str, default: Optional[Any] = None) -> NoReturn:
        """Get specific secret.

        Subclass __MUST__ implement this method.
        """
        raise NotImplementedError

    def set(self, key: str, value: Any) -> NoReturn:
        """Set specific secret.

        Subclass __MUST__ implement this method.
        """
        raise NotImplementedError

    def all(self) -> NoReturn:
        """Get all secrets as ``dict`` type.

        Subclass __MUST__ implement this method.
        """
        raise NotImplementedError
