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
