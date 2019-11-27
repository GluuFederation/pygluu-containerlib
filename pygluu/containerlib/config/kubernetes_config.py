# -*- coding: utf-8 -*-
import os

import kubernetes.client
import kubernetes.config

from .base_config import BaseConfig
from ..utils import (
    as_boolean,
    safe_value,
)


class KubernetesConfig(BaseConfig):
    def __init__(self):
        self.settings = {
            k: v for k, v in os.environ.items()
            if k.isupper() and k.startswith("GLUU_CONFIG_KUBERNETES_")
        }
        self.settings.setdefault(
            "GLUU_CONFIG_KUBERNETES_NAMESPACE",
            "default",
        )

        self.settings.setdefault(
            "GLUU_CONFIG_KUBERNETES_CONFIGMAP",
            "gluu",
        )

        self.settings.setdefault(
            "GLUU_CONFIG_KUBERNETES_USE_KUBE_CONFIG",
            False
        )

        if as_boolean(self.settings["GLUU_CONFIG_KUBERNETES_USE_KUBE_CONFIG"]):
            kubernetes.config.load_kube_config()
        else:
            kubernetes.config.load_incluster_config()

        self.client = kubernetes.client.CoreV1Api()
        self.name_exists = False

    def get(self, key, default=None):
        result = self.all()
        return result.get(key, default)

    def _prepare_configmap(self):
        # create a configmap name if not exist
        if not self.name_exists:
            try:
                self.client.read_namespaced_config_map(
                    self.settings["GLUU_CONFIG_KUBERNETES_CONFIGMAP"],
                    self.settings["GLUU_CONFIG_KUBERNETES_NAMESPACE"])
                self.name_exists = True
            except kubernetes.client.rest.ApiException as exc:
                if exc.status == 404:
                    # create the configmaps name
                    body = {
                        "kind": "ConfigMap",
                        "apiVersion": "v1",
                        "metadata": {
                            "name": self.settings["GLUU_CONFIG_KUBERNETES_CONFIGMAP"],
                        },
                        "data": {},
                    }
                    created = self.client.create_namespaced_config_map(
                        self.settings["GLUU_CONFIG_KUBERNETES_NAMESPACE"],
                        body)
                    if created:
                        self.name_exists = True
                else:
                    raise

    def set(self, key, value):
        self._prepare_configmap()
        body = {
            "kind": "ConfigMap",
            "apiVersion": "v1",
            "metadata": {
                "name": self.settings["GLUU_CONFIG_KUBERNETES_CONFIGMAP"],
            },
            "data": {
                key: safe_value(value),
            }
        }
        return self.client.patch_namespaced_config_map(
            self.settings["GLUU_CONFIG_KUBERNETES_CONFIGMAP"],
            self.settings["GLUU_CONFIG_KUBERNETES_NAMESPACE"],
            body=body)

    def all(self):
        self._prepare_configmap()
        result = self.client.read_namespaced_config_map(
            self.settings["GLUU_CONFIG_KUBERNETES_CONFIGMAP"],
            self.settings["GLUU_CONFIG_KUBERNETES_NAMESPACE"])
        return result.data or {}
