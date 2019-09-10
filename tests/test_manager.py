import pytest


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
