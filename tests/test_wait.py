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
    (10, 10),
    (0, 1),
    ("not_integer", 5),
])
def test_get_wait_interval(value, expected):
    from pygluu.containerlib.wait import get_wait_interval

    os.environ["GLUU_WAIT_SLEEP_DURATION"] = str(value)
    assert get_wait_interval() == expected
    os.environ.pop("GLUU_WAIT_SLEEP_DURATION", None)
