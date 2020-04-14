import logging
import os
from typing import (
    Any,
    Dict,
    Optional,
)

import hvac

from .base_secret import BaseSecret
from ..utils import (
    as_boolean,
    safe_value,
)

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

        cert, verify = self._verify_cert(
            self.settings["GLUU_SECRET_VAULT_SCHEME"],
            self.settings["GLUU_SECRET_VAULT_VERIFY"],
            self.settings["GLUU_SECRET_VAULT_CACERT_FILE"],
            self.settings["GLUU_SECRET_VAULT_CERT_FILE"],
            self.settings["GLUU_SECRET_VAULT_KEY_FILE"],
        )

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
        except FileNotFoundError:
            role_id = ""
        return role_id

    @property
    def secret_id(self):
        try:
            with open(self.settings["GLUU_SECRET_VAULT_SECRET_ID_FILE"]) as f:
                secret_id = f.read()
        except FileNotFoundError:
            secret_id = ""
        return secret_id

    def _authenticate(self) -> None:
        if self.client.is_authenticated():
            return

        creds = self.client.auth_approle(self.role_id, self.secret_id, use_token=False)
        self.client.token = creds["auth"]["client_token"]

    def get(self, key: str, default: Optional[Any] = None) -> str:
        self._authenticate()
        sc = self.client.read("{}/{}".format(self.prefix, key))
        if not sc:
            return default
        return sc["data"]["value"]

    def set(self, key: str, value: Any) -> bool:
        self._authenticate()
        val = {"value": safe_value(value)}

        # hvac.v1.Client.write checks for status code 200,
        # but Vault HTTP API returns 205 if request succeeded;
        # hence we're using lower level of `hvac.v1.Client` API to set key-val
        response = self.client._adapter.post('/v1/{0}/{1}'.format(self.prefix, key), json=val)
        return response.status_code == 204

    def all(self) -> Dict[str, bytes]:
        self._authenticate()
        result = self.client.list(self.prefix)
        if not result:
            return {}
        return {key: self.get(key) for key in result["data"]["keys"]}

    def _request_warning(self, scheme: str, verify: bool) -> None:
        if scheme == "https" and verify is False:
            import urllib3
            urllib3.disable_warnings()
            logger.warning(
                "All requests to Vault will be unverified. "
                "Please adjust GLUU_SECRET_VAULT_SCHEME and "
                "GLUU_SECRET_VAULT_VERIFY environment variables."
            )

    def _verify_cert(self, scheme, verify, cacert_file, cert_file, key_file):
        cert = None

        if scheme == "https":
            verify = as_boolean(verify)

            # verify using CA cert (if any)
            if all([verify, os.path.isfile(cacert_file)]):
                verify = cacert_file

            if all([os.path.isfile(cert_file),
                    os.path.isfile(key_file)]):
                cert = (cert_file, key_file)
        return cert, verify
