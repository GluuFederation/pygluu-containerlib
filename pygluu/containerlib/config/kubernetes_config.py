"""This module contains config adapter class to interact with Kubernetes ConfigMap."""

from __future__ import annotations

import os
from typing import Any

import kubernetes.client
import kubernetes.config

from pygluu.containerlib.config.base_config import BaseConfig
from pygluu.containerlib.utils import (
    as_boolean,
    safe_value,
)


class KubernetesConfig(BaseConfig):
    """This class interacts with Kubernetes ConfigMap backend.

    The following environment variables are used to instantiate the client:

    - ``GLUU_CONFIG_KUBERNETES_NAMESPACE``
    - ``GLUU_CONFIG_KUBERNETES_CONFIGMAP``
    - ``GLUU_CONFIG_KUBERNETES_USE_KUBE_CONFIG``
    """

    def __init__(self):
        self.settings = {
            k: v
            for k, v in os.environ.items()
            if k.isupper() and k.startswith("GLUU_CONFIG_KUBERNETES_")
        }
        self.settings.setdefault(
            "GLUU_CONFIG_KUBERNETES_NAMESPACE", "default",
        )

        self.settings.setdefault(
            "GLUU_CONFIG_KUBERNETES_CONFIGMAP", "gluu",
        )

        self.settings.setdefault("GLUU_CONFIG_KUBERNETES_USE_KUBE_CONFIG", False)

        self._client = None
        self.name_exists = False
        self.kubeconfig_file = os.path.expanduser("~/.kube/config")

    def get(self, key: str, default: Any = "") -> Any:
        """Get value based on given key.

        :param key: Key name.
        :param default: Default value if key is not exist.
        :returns: Value based on given key or default one.
        """
        result = self.get_all()
        return result.get(key, default)

    @property
    def client(self):
        """Lazy-loaded client to interact with Kubernetes API."""
        if not self._client:
            if as_boolean(self.settings["GLUU_CONFIG_KUBERNETES_USE_KUBE_CONFIG"]):
                kubernetes.config.load_kube_config(self.kubeconfig_file)
            else:
                kubernetes.config.load_incluster_config()
            self._client = kubernetes.client.CoreV1Api()
        return self._client

    def _prepare_configmap(self) -> None:
        """Create a configmap name if not exist."""
        if not self.name_exists:
            try:
                self.client.read_namespaced_config_map(
                    self.settings["GLUU_CONFIG_KUBERNETES_CONFIGMAP"],
                    self.settings["GLUU_CONFIG_KUBERNETES_NAMESPACE"],
                )
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
                        self.settings["GLUU_CONFIG_KUBERNETES_NAMESPACE"], body
                    )
                    if created:
                        self.name_exists = True
                else:
                    raise

    def set(self, key: str, value: Any) -> bool:
        """Set key with given value.

        :param key: Key name.
        :param value: Value of the key.
        :returns: A ``bool`` to mark whether config is set or not.
        """
        self._prepare_configmap()
        body = {
            "kind": "ConfigMap",
            "apiVersion": "v1",
            "metadata": {"name": self.settings["GLUU_CONFIG_KUBERNETES_CONFIGMAP"]},
            "data": {key: safe_value(value)},
        }
        ret = self.client.patch_namespaced_config_map(
            self.settings["GLUU_CONFIG_KUBERNETES_CONFIGMAP"],
            self.settings["GLUU_CONFIG_KUBERNETES_NAMESPACE"],
            body=body,
        )
        return bool(ret)

    def all(self) -> dict[str, Any]:  # pragma: no cover
        return self.get_all()

    def get_all(self) -> dict[str, Any]:
        """Get all key-value pairs.

        :returns: A ``dict`` of key-value pairs (if any).
        """
        self._prepare_configmap()
        result = self.client.read_namespaced_config_map(
            self.settings["GLUU_CONFIG_KUBERNETES_CONFIGMAP"],
            self.settings["GLUU_CONFIG_KUBERNETES_NAMESPACE"],
        )
        return result.data or {}

    def set_all(self, data: dict[str, Any]) -> bool:
        """Set all key-value pairs.
        Returns:
            A boolean indicating operation is succeed or not.
        """
        self._prepare_configmap()
        body = {
            "kind": "ConfigMap",
            "apiVersion": "v1",
            "metadata": {"name": self.settings["GLUU_CONFIG_KUBERNETES_CONFIGMAP"]},
            "data": {key: safe_value(value) for key, value in data.items()},
        }
        ret = self.client.patch_namespaced_config_map(
            self.settings["GLUU_CONFIG_KUBERNETES_CONFIGMAP"],
            self.settings["GLUU_CONFIG_KUBERNETES_NAMESPACE"],
            body=body,
        )
        return bool(ret)
