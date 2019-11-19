# -*- coding: utf-8 -*-
import base64
import os

import kubernetes.client
import kubernetes.config

from .base_secret import BaseSecret
from ..utils import as_boolean


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

        if as_boolean(self.settings["GLUU_SECRET_KUBERNETES_USE_KUBE_CONFIG"]):
            kubernetes.config.load_kube_config()
        else:
            kubernetes.config.load_incluster_config()
        self.client = kubernetes.client.CoreV1Api()
        self.name_exists = False

    def get(self, key, default=None):
        result = self.all()
        if key in result:
            return base64.b64decode(result[key])
        return default

    def _prepare_secret(self):
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

    def set(self, key, value):
        self._prepare_secret()
        body = {
            "kind": "Secret",
            "apiVersion": "v1",
            "metadata": {
                "name": self.settings["GLUU_SECRET_KUBERNETES_SECRET"],
            },
            "data": {
                key: base64.b64encode(value),
            }
        }
        return self.client.patch_namespaced_secret(
            self.settings["GLUU_SECRET_KUBERNETES_SECRET"],
            self.settings["GLUU_SECRET_KUBERNETES_NAMESPACE"],
            body=body)

    def all(self):
        self._prepare_secret()
        result = self.client.read_namespaced_secret(
            self.settings["GLUU_SECRET_KUBERNETES_SECRET"],
            self.settings["GLUU_SECRET_KUBERNETES_NAMESPACE"])
        return result.data or {}
