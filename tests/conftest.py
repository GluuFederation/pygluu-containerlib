from collections import namedtuple

import pytest


@pytest.fixture()
def gconfig():
    from pygluu.containerlib.config.base_config import BaseConfig

    class GConfig(BaseConfig):
        pass
    yield GConfig()


@pytest.fixture()
def gconsul_config():
    from pygluu.containerlib.config import ConsulConfig

    config = ConsulConfig()
    config.prefix = "testing/config/"
    yield config


@pytest.fixture()
def gk8s_config():
    from pygluu.containerlib.config import KubernetesConfig

    config = KubernetesConfig()
    config.settings["GLUU_CONFIG_KUBERNETES_USE_KUBE_CONFIG"] = True
    config.settings["GLUU_CONFIG_KUBERNETES_NAMESPACE"] = "testing"
    config.settings["GLUU_CONFIG_KUBERNETES_CONFIGMAP"] = "testing"
    yield config


@pytest.fixture
def gsecret():
    from pygluu.containerlib.secret.base_secret import BaseSecret

    class GSecret(BaseSecret):
        pass
    yield GSecret()


@pytest.fixture()
def gvault_secret():
    from pygluu.containerlib.secret import VaultSecret

    secret = VaultSecret()
    secret.prefix = "secret/testing"
    yield secret


@pytest.fixture()
def gk8s_secret():
    from pygluu.containerlib.secret import KubernetesSecret

    secret = KubernetesSecret()
    secret.settings["GLUU_SECRET_KUBERNETES_USE_KUBE_CONFIG"] = True
    secret.settings["GLUU_SECRET_KUBERNETES_NAMESPACE"] = "testing"
    secret.settings["GLUU_SECRET_KUBERNETES_SECRET"] = "testing"
    yield secret


@pytest.fixture
def gmanager():
    GManager = namedtuple("GManager", ["config", "secret"])

    class GConfigManager(object):
        ctx = {
            "ldap_binddn": "cn=Directory Manager",
            # "ldapTrustStoreFn": "/etc/certs/opendj.pkcs12",
            "couchbase_server_user": "admin",
            # "couchbaseTrustStoreFn": "/etc/certs/coucbase.pkcs12",
        }

        def get(self, key, default=None):
            return self.ctx.get(key) or default

        def set(self, key, value):
            self.ctx[key] = value
            return True

    class GSecretManager(object):
        ctx = {
            "encoded_ox_ldap_pw": "Zm9vYmFyCg==",
            "encoded_ldapTrustStorePass": "Zm9vYmFyCg==",
            "ldap_pkcs12_base64": "Zm9vYmFyCg==",
            "encoded_salt": "7MEDWVFAG3DmakHRyjMqp5EE",
        }

        def get(self, key, default=None):
            return self.ctx[key].encode() or default

        def to_file(self, key, dest, decode=False, binary_mode=False):
            with open(dest, "w") as f:
                val = self.get(key)
                f.write(val.decode())

    return GManager(config=GConfigManager(),
                    secret=GSecretManager())
