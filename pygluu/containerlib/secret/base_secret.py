# -*- coding: utf-8 -*-


class BaseSecret(object):
    """Base class for secret adapter. Must be sub-classed per
    implementation details.
    """
    type = "secret"

    def get(self, key, default=None):
        """Get specific secret.

        Subclass __MUST__ implement this method.
        """
        raise NotImplementedError

    def set(self, key, value):
        """Set specific secret.

        Subclass __MUST__ implement this method.
        """
        raise NotImplementedError

    def all(self):
        """Get all secrets as ``dict`` type.

        Subclass __MUST__ implement this method.
        """
        raise NotImplementedError
