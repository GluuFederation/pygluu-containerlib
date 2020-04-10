import os
from collections import namedtuple
from typing import NamedTuple

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
_Manager = namedtuple("Manager", ["config", "secret"])


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
        return self.adapter.get(key, default)

    def set(self, key, value):
        return self.adapter.set(key, value)

    def all(self):
        return {k: v for k, v in self.adapter.all().items()}


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

    def to_file(self, key: str, dest: str, decode: bool = False, binary_mode: bool = False) -> None:
        """Pull secret and write to a file.
        """
        value = self.adapter.get(key)
        if decode:
            salt = self.adapter.get("encoded_salt")
            value = decode_text(value, salt)

        mode = "w"
        # TODO: is this needed?
        # if binary_mode:
        #     mode = "wb"
        with open(dest, mode) as f:
            # write as str
            f.write(value)

    def from_file(self, key: str, src: str, encode: bool = False, binary_mode: bool = False) -> None:
        mode = "r"
        # TODO: is this needed?
        # if binary_mode:
        #     mode = "rb"
        with open(src, mode) as f:
            value = f.read()

        if encode:
            salt = self.adapter.get("encoded_salt")
            value = encode_text(value, salt)
        self.adapter.set(key, value)


def get_manager() -> NamedTuple:
    """Convenient function to get manager instances.
    """
    config_mgr = ConfigManager()
    secret_mgr = SecretManager()
    return _Manager(config=config_mgr, secret=secret_mgr)
