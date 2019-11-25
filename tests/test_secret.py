# -*- coding: utf-8 -*-
import pytest


def test_base_secret_get(dummy_secret):
    with pytest.raises(NotImplementedError) as exc:
        dummy_secret.get("foo")
    assert "" in str(exc.value)


def test_base_secret_set(dummy_secret):
    with pytest.raises(NotImplementedError) as exc:
        dummy_secret.set("foo", "bar")
    assert "" in str(exc.value)


def test_base_secret_all(dummy_secret):
    with pytest.raises(NotImplementedError) as exc:
        dummy_secret.all()
    assert "" in str(exc.value)
