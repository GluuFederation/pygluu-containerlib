# -*- coding: utf-8 -*-
import logging
import os

import hvac

from .base_secret import BaseSecret
from ..utils import as_boolean

logger = logging.getLogger(__name__)


class VaultSecret(BaseSecret):
    def __init__(self):
        self.settings = {
            k: v for k, v in os.environ.items()
            if k.isupper() and k.startswith("GLUU_SECRET_VAULT_")
        }
        self.settings.setdefault(
            "GLUU_SECRET_VAULT_HOST",
            "localhost",
        )
        self.settings.setdefault(
            "GLUU_SECRET_VAULT_PORT",
            8200,
        )
        self.settings.setdefault(
            "GLUU_SECRET_VAULT_SCHEME",
            "http",
        )
        self.settings.setdefault(
            "GLUU_SECRET_VAULT_VERIFY",
            False,
        )
        self.settings.setdefault(
            "GLUU_SECRET_VAULT_ROLE_ID_FILE",
            "/etc/certs/vault_role_id",
        ),
        self.settings.setdefault(
            "GLUU_SECRET_VAULT_SECRET_ID_FILE",
            "/etc/certs/vault_secret_id",
        )
        self.settings.setdefault(
            "GLUU_SECRET_VAULT_CERT_FILE",
            "/etc/certs/vault_client.crt",
        )
        self.settings.setdefault(
            "GLUU_SECRET_VAULT_KEY_FILE",
            "/etc/certs/vault_client.key",
        )
        self.settings.setdefault(
            "GLUU_SECRET_VAULT_CACERT_FILE",
            "/etc/certs/vault_ca.crt",
        )

        cert = None
        verify = False

        if self.settings["GLUU_SECRET_VAULT_SCHEME"] == "https":
            verify = as_boolean(self.settings["GLUU_SECRET_VAULT_VERIFY"])

            # verify using CA cert (if any)
            if all([verify,
                    os.path.isfile(self.settings["GLUU_SECRET_VAULT_CACERT_FILE"])]):
                verify = self.settings["GLUU_SECRET_VAULT_CACERT_FILE"]

            if all([os.path.isfile(self.settings["GLUU_SECRET_VAULT_CERT_FILE"]),
                    os.path.isfile(self.settings["GLUU_SECRET_VAULT_KEY_FILE"])]):
                cert = (self.settings["GLUU_SECRET_VAULT_CERT_FILE"],
                        self.settings["GLUU_SECRET_VAULT_KEY_FILE"])

        self._request_warning(self.settings["GLUU_SECRET_VAULT_SCHEME"], verify)

        self.client = hvac.Client(
            url="{}://{}:{}".format(
                self.settings["GLUU_SECRET_VAULT_SCHEME"],
                self.settings["GLUU_SECRET_VAULT_HOST"],
                self.settings["GLUU_SECRET_VAULT_PORT"],
            ),
            cert=cert,
            verify=verify,
        )
        self.prefix = "secret/gluu"

    @property
    def role_id(self):
        try:
            with open(self.settings["GLUU_SECRET_VAULT_ROLE_ID_FILE"]) as f:
                role_id = f.read()
        except IOError:
            role_id = ""
        return role_id

    @property
    def secret_id(self):
        try:
            with open(self.settings["GLUU_SECRET_VAULT_SECRET_ID_FILE"]) as f:
                secret_id = f.read()
        except IOError:
            secret_id = ""
        return secret_id

    def _authenticate(self):
        if self.client.is_authenticated():
            return

        creds = self.client.auth_approle(self.role_id, self.secret_id, use_token=False)
        self.client.token = creds["auth"]["client_token"]

    def get(self, key, default=None):
        self._authenticate()
        sc = self.client.read("{}/{}".format(self.prefix, key))
        if not sc:
            return default
        return sc["data"]["value"]

    def set(self, key, value):
        self._authenticate()
        val = {"value": value}

        # hvac.v1.Client.write checks for status code 200,
        # but Vault HTTP API returns 204 if request succeeded;
        # hence we're using lower level of `hvac.v1.Client` API to set key-val
        response = self.client._adapter.post('/v1/{0}/{1}'.format(self.prefix, key), json=val)
        return response.status_code == 204

    def all(self):
        self._authenticate()
        result = self.client.list(self.prefix)
        return {key: self.get(key) for key in result["data"]["keys"]}

    def _request_warning(self, scheme, verify):
        if scheme == "https" and verify is False:
            import urllib3
            urllib3.disable_warnings()
            logger.warn(
                "All requests to Vault will be unverified. "
                "Please adjust GLUU_SECRET_VAULT_SCHEME and "
                "GLUU_SECRET_VAULT_VERIFY environment variables."
            )
