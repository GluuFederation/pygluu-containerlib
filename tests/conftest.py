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
    config.kubeconfig_file = "tests/kubeconfig"
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
    secret.kubeconfig_file = "tests/kubeconfig"
    yield secret


@pytest.fixture
def gmanager(gconsul_config, gvault_secret):
    from pygluu.containerlib.manager import get_manager

    def get_config(key, default=None):
        ctx = {
            "ldap_binddn": "cn=Directory Manager",
            "couchbase_server_user": "admin",
        }
        return ctx.get(key) or default

    def get_secret(key, default=None):
        ctx = {
            "encoded_ox_ldap_pw": "YgH8NDxhxmA=",
            "encoded_ldapTrustStorePass": "YgH8NDxhxmA=",
            "ldap_pkcs12_base64": "YgH8NDxhxmA=",
            "encoded_salt": "7MEDWVFAG3DmakHRyjMqp5EE",
            "couchbase_truststore_pw": "dN6xQg8kJkdt",
        }
        return ctx.get(key) or default

    gmanager = get_manager()

    gconsul_config.get = get_config
    gmanager.config.adapter = gconsul_config

    gvault_secret.get = get_secret
    gmanager.secret.adapter = gvault_secret

    yield gmanager


@pytest.fixture
def gmeta():
    from pygluu.containerlib.meta.base_meta import BaseMeta

    class GMeta(BaseMeta):
        pass
    yield GMeta()


@pytest.fixture
def gk8s_meta():
    from pygluu.containerlib.meta import KubernetesMeta

    meta = KubernetesMeta()
    meta.kubeconfig_file = "tests/kubeconfig"
    yield meta
