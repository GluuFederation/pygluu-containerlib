import base64
import os
from typing import (
    Any,
)

import kubernetes.client
import kubernetes.config

from .base_secret import BaseSecret
from ..utils import (
    as_boolean,
    safe_value,
)


class KubernetesSecret(BaseSecret):
    def __init__(self):
        self.settings = {
            k: v for k, v in os.environ.items()
            if k.isupper() and k.startswith("GLUU_SECRET_KUBERNETES_")
        }
        self.settings.setdefault(
            "GLUU_SECRET_KUBERNETES_NAMESPACE",
            "default",
        )
        self.settings.setdefault(
            "GLUU_SECRET_KUBERNETES_SECRET",
            "gluu",
        )
        self.settings.setdefault(
            "GLUU_SECRET_KUBERNETES_USE_KUBE_CONFIG",
            False
        )

        self._client = None
        self.name_exists = False

    @property
    def client(self):
        if not self._client:
            if as_boolean(self.settings["GLUU_SECRET_KUBERNETES_USE_KUBE_CONFIG"]):
                kubernetes.config.load_kube_config()
            else:
                kubernetes.config.load_incluster_config()
            self._client = kubernetes.client.CoreV1Api()
        return self._client

    def get(self, key, default=None):
        result = self.all()
        return result.get(key) or default

    def _prepare_secret(self) -> None:
        # create a secret name if not exist
        if not self.name_exists:
            try:
                self.client.read_namespaced_secret(
                    self.settings["GLUU_SECRET_KUBERNETES_SECRET"],
                    self.settings["GLUU_SECRET_KUBERNETES_NAMESPACE"])
                self.name_exists = True
            except kubernetes.client.rest.ApiException as exc:
                if exc.status == 404:
                    # create the secrets name
                    body = {
                        "kind": "Secret",
                        "apiVersion": "v1",
                        "metadata": {
                            "name": self.settings["GLUU_SECRET_KUBERNETES_SECRET"],
                        },
                        "data": {},
                    }
                    created = self.client.create_namespaced_secret(
                        self.settings["GLUU_SECRET_KUBERNETES_NAMESPACE"],
                        body)
                    if created:
                        self.name_exists = True
                else:
                    raise

    def set(self, key: str, value: Any) -> bool:
        self._prepare_secret()
        body = {
            "kind": "Secret",
            "apiVersion": "v1",
            "metadata": {
                "name": self.settings["GLUU_SECRET_KUBERNETES_SECRET"],
            },
            "data": {
                key: base64.b64encode(safe_value(value).encode()).decode(),
            }
        }
        ret = self.client.patch_namespaced_secret(
            self.settings["GLUU_SECRET_KUBERNETES_SECRET"],
            self.settings["GLUU_SECRET_KUBERNETES_NAMESPACE"],
            body=body,
        )
        return bool(ret)

    def all(self):
        self._prepare_secret()
        result = self.client.read_namespaced_secret(
            self.settings["GLUU_SECRET_KUBERNETES_SECRET"],
            self.settings["GLUU_SECRET_KUBERNETES_NAMESPACE"])

        data = result.data or {}
        return {
            k: base64.b64decode(v).decode() for k, v in data.items()
        }
