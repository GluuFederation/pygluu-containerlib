import base64
import json
import random
import re
import shlex
import socket
import ssl
import string
import subprocess
# import uuid
from typing import (
    Any,
    AnyStr,
    Tuple,
)

import pyDes
from ldap3.utils import hashed

# Default charset
_DEFAULT_CHARS = "".join([string.ascii_letters, string.digits])


def as_boolean(val: Any) -> bool:
    """Converts value as boolean.
    """
    default = False
    truthy = set(('t', 'T', 'true', 'True', 'TRUE', '1', 1, True))
    falsy = set(('f', 'F', 'false', 'False', 'FALSE', '0', 0, False))

    if val in truthy:
        return True
    if val in falsy:
        return False
    return default


def safe_value(value: Any) -> AnyStr:
    if not isinstance(value, (str, bytes)):
        value = json.dumps(value)
    return value


def get_random_chars(size: int = 12, chars: str = _DEFAULT_CHARS) -> str:
    """Generates random characters.
    """
    return "".join(random.choices(chars, k=size))


def get_sys_random_chars(size: int = 12, chars: str = _DEFAULT_CHARS) -> str:
    """Generates random characters based on OS.
    """
    return "".join(random.SystemRandom().choices(chars, k=size))


# def get_quad() -> str:
#     uid = uuid.uuid4()
#     return uid.hex[:4].upper()


# def join_quad_str(num: int) -> str:
#     return ".".join([get_quad() for _ in range(num)])


# def safe_inum_str(val: str) -> str:
#     return val.replace("@", "").replace("!", "").replace(".", "")


def exec_cmd(cmd: str) -> Tuple[bytes, bytes, int]:
    args = shlex.split(cmd)
    popen = subprocess.Popen(
        args,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    stdout, stderr = popen.communicate()
    retcode = popen.returncode
    return stdout.strip(), stderr.strip(), retcode


def encode_text(text: AnyStr, key: AnyStr) -> bytes:
    cipher = pyDes.triple_des(key, pyDes.ECB, padmode=pyDes.PAD_PKCS5)
    encrypted_text = cipher.encrypt(text)
    return base64.b64encode(encrypted_text)


def decode_text(encoded_text: AnyStr, key: AnyStr) -> bytes:
    text = base64.b64decode(encoded_text)
    cipher = pyDes.triple_des(key, pyDes.ECB, padmode=pyDes.PAD_PKCS5)
    return cipher.decrypt(text)


def safe_render(text: str, ctx: dict) -> str:
    text = re.sub(r"%([^\(])", r"%%\1", text)
    # There was a % at the end?
    text = re.sub(r"%$", r"%%", text)
    return text % ctx


def reindent(text: str, num_spaces: int = 1) -> str:
    text = [
        "{0}{1}".format(num_spaces * " ", line.lstrip())
        for line in text.splitlines()
    ]
    text = "\n".join(text)
    return text


def generate_base64_contents(text: AnyStr, num_spaces: int = 1) -> bytes:
    text = base64.b64encode(str_to_bytes(text))
    return reindent(text.decode(), num_spaces).encode()


def cert_to_truststore(alias: str, cert_file: str, keystore_file: str,
                       store_pass: str) -> Tuple[bytes, bytes, int]:
    cmd = "keytool -importcert -trustcacerts -alias {0} " \
          "-file {1} -keystore {2} -storepass {3} " \
          "-noprompt".format(alias, cert_file, keystore_file, store_pass)
    return exec_cmd(cmd)


def get_server_certificate(host: str, port: int, filepath: str,
                           server_hostname: str = "") -> str:
    """Gets PEM-formatted certificate of a given address.
    """
    server_hostname = server_hostname or host

    with socket.create_connection((host, port)) as conn:
        context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)

        with context.wrap_socket(conn, server_hostname=server_hostname) as sock:
            der = sock.getpeercert(True)
            cert = ssl.DER_cert_to_PEM_cert(der)

            with open(filepath, "w") as f:
                f.write(cert)
            return cert


def ldap_encode(password):
    return hashed.hashed(hashed.HASHED_SALTED_SHA, password)


def str_to_bytes(val):
    if isinstance(val, str):
        val = val.encode()
    return val


# def bytes_to_str(val):
#     if isinstance(val, bytes):
#         val = val.decode()
#     return val
