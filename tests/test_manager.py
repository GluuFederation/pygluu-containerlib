import os

import pytest


class FakeAdapter(object):
    def get(self, k, default=None):
        return "GET"

    def set(self, k, v):
        return "SET"

    def all(self):
        return {}


@pytest.mark.parametrize("adapter, adapter_cls", [
    ("consul", "ConsulConfig"),
    ("kubernetes", "KubernetesConfig"),
    ("random", "NoneType"),
])
def test_config_manager(adapter, adapter_cls):
    from pygluu.containerlib.manager import ConfigManager

    os.environ["GLUU_CONFIG_ADAPTER"] = adapter
    manager = ConfigManager()

    assert manager.adapter.__class__.__name__ == adapter_cls
    os.environ.pop("GLUU_CONFIG_ADAPTER", None)


@pytest.mark.parametrize("adapter, adapter_cls", [
    ("vault", "VaultSecret"),
    ("kubernetes", "KubernetesSecret"),
    ("random", "NoneType"),
])
def test_secret_manager(adapter, adapter_cls):
    from pygluu.containerlib.manager import SecretManager

    os.environ["GLUU_SECRET_ADAPTER"] = adapter
    manager = SecretManager()

    assert manager.adapter.__class__.__name__ == adapter_cls
    os.environ.pop("GLUU_SECRET_ADAPTER", None)


def test_config_manager_methods():
    from pygluu.containerlib.manager import ConfigManager

    fake_adapter = FakeAdapter()
    manager = ConfigManager()
    manager.adapter = fake_adapter

    assert manager.get("foo") == fake_adapter.get("foo")
    assert manager.set("foo", "bar") == fake_adapter.set("foo", "bar")
    assert manager.all() == fake_adapter.all()


def test_secret_manager_methods():
    from pygluu.containerlib.manager import SecretManager

    fake_adapter = FakeAdapter()
    manager = SecretManager()
    manager.adapter = fake_adapter

    assert manager.get("foo") == fake_adapter.get("foo")
    assert manager.set("foo", "bar") == fake_adapter.set("foo", "bar")
    assert manager.all() == fake_adapter.all()


@pytest.mark.parametrize("value, expected, decode, binary_mode", [
    ("abcd", "abcd", False, False),
    ("YgH8NDxhxmA=", "abcd", True, False),
])
def test_manager_secret_to_file(tmpdir, monkeypatch, value, expected,
                                decode, binary_mode):
    from pygluu.containerlib.manager import get_manager

    def maybe_salt(*args, **kwargs):
        if args[1] == "encoded_salt":
            return "a" * 16
        return value

    monkeypatch.setattr(
        "pygluu.containerlib.secret.VaultSecret.get",
        maybe_salt,
    )

    manager = get_manager()
    dst = tmpdir.mkdir("pygluu").join("secret.txt")
    manager.secret.to_file("secret_key", str(dst), decode, binary_mode)
    assert dst.read() == expected


@pytest.mark.parametrize("value, expected, encode, binary_mode", [
    ("abcd", "abcd", False, False),
    ("abcd", "YgH8NDxhxmA=", True, False),
])
def test_manager_secret_from_file(tmpdir, monkeypatch, value, expected,
                                  encode, binary_mode):
    from pygluu.containerlib.manager import get_manager

    def maybe_salt(*args, **kwargs):
        if args[1] == "encoded_salt":
            return "a" * 16
        return expected

    monkeypatch.setattr(
        "pygluu.containerlib.secret.VaultSecret.get",
        maybe_salt,
    )

    monkeypatch.setattr(
        "pygluu.containerlib.secret.VaultSecret.set",
        lambda instance, key, value: True,
    )

    manager = get_manager()
    dst = tmpdir.mkdir("pygluu").join("secret.txt")
    dst.write(value)

    manager.secret.from_file("secret_key", str(dst), encode, binary_mode)
    assert manager.secret.get("secret_key") == expected
