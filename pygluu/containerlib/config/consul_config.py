# -*- coding: utf-8 -*-
import logging
import os

from consul import Consul

from .base_config import BaseConfig
from ..utils import (
    as_boolean,
    safe_value,
)

logger = logging.getLogger(__name__)


class ConsulConfig(BaseConfig):
    def __init__(self):
        self.settings = {
            k: v for k, v in os.environ.items()
            if k.isupper() and k.startswith("GLUU_CONFIG_CONSUL_")
        }

        self.settings.setdefault(
            "GLUU_CONFIG_CONSUL_HOST",
            "localhost",
        )

        self.settings.setdefault(
            "GLUU_CONFIG_CONSUL_PORT",
            8500,
        )

        self.settings.setdefault(
            "GLUU_CONFIG_CONSUL_CONSISTENCY",
            "stale",
        )

        self.settings.setdefault(
            "GLUU_CONFIG_CONSUL_SCHEME",
            "http",
        )

        self.settings.setdefault(
            "GLUU_CONFIG_CONSUL_VERIFY",
            False,
        )

        self.settings.setdefault(
            "GLUU_CONFIG_CONSUL_CACERT_FILE",
            "/etc/certs/consul_ca.crt",
        )

        self.settings.setdefault(
            "GLUU_CONFIG_CONSUL_CERT_FILE",
            "/etc/certs/consul_client.crt",
        )

        self.settings.setdefault(
            "GLUU_CONFIG_CONSUL_KEY_FILE",
            "/etc/certs/consul_client.key",
        )

        self.settings.setdefault(
            "GLUU_CONFIG_CONSUL_TOKEN_FILE",
            "/etc/certs/consul_token",
        )

        self.prefix = "gluu/config/"
        token = None
        cert = None
        verify = False

        if os.path.isfile(self.settings["GLUU_CONFIG_CONSUL_TOKEN_FILE"]):
            with open(self.settings["GLUU_CONFIG_CONSUL_TOKEN_FILE"]) as fr:
                token = fr.read().strip()

        if self.settings["GLUU_CONFIG_CONSUL_SCHEME"] == "https":
            verify = as_boolean(self.settings["GLUU_CONFIG_CONSUL_VERIFY"])

            # verify using CA cert (if any)
            if all([verify,
                    os.path.isfile(self.settings["GLUU_CONFIG_CONSUL_CACERT_FILE"])]):
                verify = self.settings["GLUU_CONFIG_CONSUL_CACERT_FILE"]

            if all([os.path.isfile(self.settings["GLUU_CONFIG_CONSUL_CERT_FILE"]),
                    os.path.isfile(self.settings["GLUU_CONFIG_CONSUL_KEY_FILE"])]):
                cert = (self.settings["GLUU_CONFIG_CONSUL_CERT_FILE"],
                        self.settings["GLUU_CONFIG_CONSUL_KEY_FILE"])

        self._request_warning(self.settings["GLUU_CONFIG_CONSUL_SCHEME"], verify)

        self.client = Consul(
            host=self.settings["GLUU_CONFIG_CONSUL_HOST"],
            port=self.settings["GLUU_CONFIG_CONSUL_PORT"],
            token=token,
            scheme=self.settings["GLUU_CONFIG_CONSUL_SCHEME"],
            consistency=self.settings["GLUU_CONFIG_CONSUL_CONSISTENCY"],
            verify=verify,
            cert=cert,
        )

    def _merge_path(self, key):
        """Add prefix to the key.
        """
        return "".join([self.prefix, key])

    def _unmerge_path(self, key):
        """Remove prefix from the key.
        """
        return key[len(self.prefix):]

    def get(self, key, default=None):
        _, result = self.client.kv.get(self._merge_path(key))
        if not result:
            return default
        return result["Value"]

    def set(self, key, value):
        return self.client.kv.put(self._merge_path(key),
                                  safe_value(value))

    def find(self, key):
        _, resultset = self.client.kv.get(self._merge_path(key),
                                          recurse=True)

        if not resultset:
            return {}

        return {
            self._unmerge_path(item["Key"]): item["Value"]
            for item in resultset
        }

    def all(self):
        return self.find("")

    def _request_warning(self, scheme, verify):
        if scheme == "https" and verify is False:
            import urllib3
            urllib3.disable_warnings()
            logger.warn(
                "All requests to Consul will be unverified. "
                "Please adjust GLUU_CONFIG_CONSUL_SCHEME and "
                "GLUU_CONFIG_CONSUL_VERIFY environment variables."
            )
