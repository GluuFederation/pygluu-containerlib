import pytest


@pytest.mark.parametrize("val,expected", [
    ("t", True),  # truthy
    ("T", True),
    ("true", True),
    ("True", True),
    ("TRUE", True),
    ("1", True),
    (1, True),
    (True, True),
    ("f", False),  # falsy
    ("F", False),
    ("false", False),
    ("False", False),
    ("FALSE", False),
    ("0", False),
    (0, False),
    (False, False),
    ("random", False),  # misc
])
def test_as_boolean(val, expected):
    from pygluu.containerlib.utils import as_boolean
    assert as_boolean(val) == expected


@pytest.mark.parametrize("size", [12, 10])
def test_get_random_chars(size):
    from pygluu.containerlib.utils import get_random_chars
    assert len(get_random_chars(size)) == size


@pytest.mark.parametrize("size", [12, 10])
def test_get_sys_random_chars(size):
    from pygluu.containerlib.utils import get_sys_random_chars
    assert len(get_sys_random_chars(size)) == size


def test_get_quad():
    from pygluu.containerlib.utils import get_quad
    assert len(get_quad()) == 4


def test_join_quad_str():
    from pygluu.containerlib.utils import join_quad_str
    # should have dot char
    assert join_quad_str(2).find(".") != 0


@pytest.mark.parametrize("val, expected", [
    ("@1234", "1234"),
    ("!1234", "1234"),
    (".1234", "1234")
])
def test_safe_inum_str(val, expected):
    from pygluu.containerlib.utils import safe_inum_str
    assert safe_inum_str(val) == expected
