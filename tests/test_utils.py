from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

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
    (None, False),
])
def test_as_boolean(val, expected):
    from pygluu.containerlib.utils import as_boolean
    assert as_boolean(val) == expected


@pytest.mark.parametrize("value, expected", [
    ("a", "a"),
    (1, "1"),
    (b"b", b"b"),
    (True, "true"),
    (False, "false"),
    (None, "null"),
    ([], "[]"),
])
def test_safe_value(value, expected):
    from pygluu.containerlib.utils import safe_value
    assert safe_value(value) == expected


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
    assert len(join_quad_str(2)) == 9


@pytest.mark.parametrize("val, expected", [
    ("@1234", "1234"),
    ("!1234", "1234"),
    (".1234", "1234")
])
def test_safe_inum_str(val, expected):
    from pygluu.containerlib.utils import safe_inum_str
    assert safe_inum_str(val) == expected


@pytest.mark.parametrize("cmd", ["echo foobar"])
def test_exec_cmd(cmd):
    from pygluu.containerlib.utils import exec_cmd

    out, err, code = exec_cmd(cmd)
    assert out == b"foobar"
    assert err == b""
    assert code == 0


@pytest.mark.parametrize("txt, ctx, expected", [
    ("%id", {}, "%id"),
    ("%(id)s", {"id": 1}, "1"),
])
def test_safe_render(txt, ctx, expected):
    from pygluu.containerlib.utils import safe_render
    assert safe_render(txt, ctx) == expected


@pytest.mark.parametrize("text, num_spaces, expected", [
    ("ab\n\tcd", 0, "ab\ncd"),
    ("ab\n\tcd", 1, " ab\n cd"),
])
def test_reindent(text, num_spaces, expected):
    from pygluu.containerlib.utils import reindent
    assert reindent(text, num_spaces) == expected


@pytest.mark.parametrize("text, num_spaces, expected", [
    ("abcd", 0, "YWJjZA=="),
    ("abcd", 1, " YWJjZA=="),
])
def test_generate_base64_contents(text, num_spaces, expected):
    from pygluu.containerlib.utils import generate_base64_contents
    assert generate_base64_contents(text, num_spaces) == expected


def test_encode_text():
    from pygluu.containerlib.utils import encode_text

    text = "abcd"
    key = "a" * 16
    expected = "YgH8NDxhxmA="
    assert encode_text(text, key) == expected


def test_decode_text():
    from pygluu.containerlib.utils import decode_text

    text = "YgH8NDxhxmA="
    key = "a" * 16
    expected = "abcd"
    assert decode_text(text, key) == expected
