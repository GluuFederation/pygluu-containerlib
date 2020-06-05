import os
from collections import namedtuple
from typing import (
    AnyStr,
    NamedTuple,
)

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
        _adapter = os.environ.get("GLUU_CONFIG_ADAPTER", "consul",)
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
        _adapter = os.environ.get("GLUU_SECRET_ADAPTER", "vault",)
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

    def to_file(
        self, key: str, dest: str, decode: bool = False, binary_mode: bool = False
    ) -> AnyStr:
        """Pull secret and write to a file.
        """
        mode = "w"
        if binary_mode:
            mode = "wb"
            # always decodes the bytes
            decode = True

        value = self.adapter.get(key)
        if decode:
            salt = self.adapter.get("encoded_salt")
            try:
                value = decode_text(value, salt).decode()
            except UnicodeDecodeError:
                # likely bytes from a binary
                value = decode_text(value, salt).decode("ISO-8859-1")

        with open(dest, mode) as f:
            if binary_mode:
                # convert to bytes
                value = value.encode("ISO-8859-1")
            f.write(value)

    def from_file(
        self, key: str, src: str, encode: bool = False, binary_mode: bool = False
    ) -> None:
        mode = "r"
        if binary_mode:
            mode = "rb"
            encode = True

        with open(src, mode) as f:
            try:
                value = f.read()
            except UnicodeDecodeError:
                raise ValueError(f"Looks like you're trying to read binary file {src}")

        if encode:
            salt = self.adapter.get("encoded_salt")
            value = encode_text(value, salt).decode()
        self.adapter.set(key, value)


def get_manager() -> NamedTuple:
    """Convenient function to get manager instances.
    """
    config_mgr = ConfigManager()
    secret_mgr = SecretManager()
    return _Manager(config=config_mgr, secret=secret_mgr)
