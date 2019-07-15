# -*- coding: utf-8 -*-


class BaseConfig(object):
    """Base class for config adapter. Must be sub-classed per
    implementation details.
    """
    type = "config"

    def get(self, key, default=None):
        """Get specific config.

        Subclass __MUST__ implement this method.
        """
        raise NotImplementedError

    def set(self, key, value):
        """Set specific config.

        Subclass __MUST__ implement this method.
        """
        raise NotImplementedError

    def all(self):
        """Get all config as ``dict`` type.

        Subclass __MUST__ implement this method.
        """
        raise NotImplementedError
