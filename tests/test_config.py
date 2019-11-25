# -*- coding: utf-8 -*-
import pytest


def test_base_config_get(dummy_config):
    with pytest.raises(NotImplementedError) as exc:
        dummy_config.get("foo")
    assert "" in str(exc.value)


def test_base_config_set(dummy_config):
    with pytest.raises(NotImplementedError) as exc:
        dummy_config.set("foo", "bar")
    assert "" in str(exc.value)


def test_base_config_all(dummy_config):
    with pytest.raises(NotImplementedError) as exc:
        dummy_config.all()
    assert "" in str(exc.value)
