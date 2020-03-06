# -*- coding: utf-8 -*-
import os
from collections import namedtuple

from .config import (
    ConsulConfig,
    KubernetesConfig,
)
from .secret import (
    KubernetesSecret,
    VaultSecret,
)
from .utils import (
    decode_text,
    encode_text,
)

#: Object as a placeholder of config and secret manager
_Manager = namedtuple("Manager", "config secret")


def to_str(val):
    if isinstance(val, bytes):
        val = val.decode()
    return val


class ConfigManager(object):
    def __init__(self):
        _adapter = os.environ.get(
            "GLUU_CONFIG_ADAPTER",
            "consul",
        )
        if _adapter == "consul":
            self.adapter = ConsulConfig()
        elif _adapter == "kubernetes":
            self.adapter = KubernetesConfig()
        else:
            self.adapter = None

    def get(self, key, default=None):
        return to_str(self.adapter.get(key, default))

    def set(self, key, value):
        return self.adapter.set(key, value)

    def all(self):
        return {k: to_str(v) for k, v in self.adapter.all().items()}


class SecretManager(object):
    def __init__(self):
        _adapter = os.environ.get(
            "GLUU_SECRET_ADAPTER",
            "vault",
        )
        if _adapter == "vault":
            self.adapter = VaultSecret()
        elif _adapter == "kubernetes":
            self.adapter = KubernetesSecret()
        else:
            self.adapter = None

    def get(self, key, default=None):
        return self.adapter.get(key, default)

    def set(self, key, value):
        return self.adapter.set(key, value)

    def all(self):
        return self.adapter.all()

    def to_file(self, key, dest, decode=False, binary_mode=False):
        """Pull secret and write to a file.
        """
        value = self.adapter.get(key)
        if decode:
            salt = self.adapter.get("encoded_salt")
            value = decode_text(value, salt)

        mode = "w"
        # if binary_mode:
        #     mode = "wb"

        with open(dest, mode) as f:
            f.write(value)

    def from_file(self, key, src, encode=False, binary_mode=False):
        mode = "r"
        # if binary_mode:
        #     mode = "rb"

        with open(src, mode) as f:
            value = f.read()

        if encode:
            salt = self.adapter.get("encoded_salt")
            value = encode_text(value, salt)
        self.adapter.set(key, value)


def get_manager():
    """Convenient function to get manager instances.
    """
    config_mgr = ConfigManager()
    secret_mgr = SecretManager()
    return _Manager(config=config_mgr, secret=secret_mgr)
