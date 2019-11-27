# -*- coding: utf-8 -*-
from collections import namedtuple

import pytest


@pytest.fixture
def dummy_config():
    from pygluu.containerlib.config.base_config import BaseConfig

    class DummyConfig(BaseConfig):
        pass
    return DummyConfig()


@pytest.fixture
def dummy_secret():
    from pygluu.containerlib.secret.base_secret import BaseSecret

    class DummySecret(BaseSecret):
        pass
    return DummySecret()


@pytest.fixture
def fake_manager():
    _FakeManager = namedtuple("FakeManager", ["config", "secret"])

    class FakeConfigManager(object):
        def get(self, key):
            ctx = {
                "ldap_binddn": "cn=Directory Manager",
                "ldapTrustStoreFn": "/etc/certs/opendj.pkcs12",
                "couchbase_server_user": "admin",
            }
            return ctx[key]

    class FakeSecretManager(object):
        def get(self, key):
            ctx = {
                "encoded_ox_ldap_pw": "Zm9vYmFyCg==",
                "encoded_ldapTrustStorePass": "Zm9vYmFyCg==",
                "ldap_pkcs12_base64": "Zm9vYmFyCg==",
                "encoded_salt": "Zm9vYmFyCg==",
            }
            return ctx[key]

        def to_file(self, key, dest, decode=False, binary_mode=False):
            with open(dest, "w") as f:
                val = self.get(key)
                f.write(val)

    return _FakeManager(config=FakeConfigManager(),
                        secret=FakeSecretManager())
