import os

import pytest


@pytest.mark.parametrize("value, expected", [
    (10, 10),
    (0, 1),
    ("not_integer", 60 * 5),
])
def test_get_wait_max_time(value, expected):
    from pygluu.containerlib.wait import get_wait_max_time

    os.environ["GLUU_WAIT_MAX_TIME"] = str(value)
    assert get_wait_max_time() == expected
    os.environ.pop("GLUU_WAIT_MAX_TIME", None)


@pytest.mark.parametrize("value, expected", [
    (5, 5),
    (0, 1),
    ("not_integer", 10),
])
def test_get_wait_interval(value, expected):
    from pygluu.containerlib.wait import get_wait_interval

    os.environ["GLUU_WAIT_SLEEP_DURATION"] = str(value)
    assert get_wait_interval() == expected
    os.environ.pop("GLUU_WAIT_SLEEP_DURATION", None)


def test_on_backoff(caplog):
    from pygluu.containerlib.wait import on_backoff

    details = {"kwargs": {"label": "Service"}, "wait": 10.0}
    on_backoff(details)
    assert "is not ready" in caplog.records[0].message


def test_on_succes(caplog):
    import logging
    from pygluu.containerlib.wait import on_success

    with caplog.at_level(logging.INFO):
        details = {"kwargs": {"label": "Service"}}
        on_success(details)
        assert "is ready" in caplog.records[0].message


def test_on_giveup(caplog):
    from pygluu.containerlib.wait import on_giveup

    details = {"kwargs": {"label": "Service"}, "elapsed": 10.0}
    on_giveup(details)
    assert "is not ready after" in caplog.records[0].message
