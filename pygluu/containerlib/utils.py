# -*- coding: utf-8 -*-
import base64
import codecs
import json
import random
import re
import shlex
import ssl
import string
import subprocess
import uuid
from typing import Any
from typing import AnyStr
from typing import Tuple

import pyDes

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


def get_quad() -> str:
    return "{}".format(uuid.uuid4())[:4].upper()


def join_quad_str(num: int) -> str:
    return ".".join([get_quad() for _ in range(num)])


def safe_inum_str(val: str) -> str:
    return val.replace("@", "").replace("!", "").replace(".", "")


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


def encode_text(text, key):
    text = codecs.encode(text)
    key = codecs.encode(key)
    cipher = pyDes.triple_des(key, pyDes.ECB, padmode=pyDes.PAD_PKCS5)
    encrypted_text = cipher.encrypt(text)
    return base64.b64encode(encrypted_text).decode()


def decode_text(encoded_text, key):
    text = base64.b64decode(encoded_text)
    key = codecs.encode(key)

    cipher = pyDes.triple_des(key, pyDes.ECB, padmode=pyDes.PAD_PKCS5)
    decoded_text = cipher.decrypt(text)

    decoded_text = decoded_text.decode()
    return decoded_text


def safe_render(text, ctx):
    text = re.sub(r"%([^\(])", r"%%\1", text)
    # There was a % at the end?
    text = re.sub(r"%$", r"%%", text)
    return text % ctx


def reindent(text, num_spaces=1):
    text = [
        "{0}{1}".format(num_spaces * " ", line.lstrip())
        for line in text.splitlines()
    ]
    text = "\n".join(text)
    return text


def generate_base64_contents(text, num_spaces=1):
    text = codecs.encode(text)
    text = base64.b64encode(text)
    return reindent(text.decode(), num_spaces)


def cert_to_truststore(alias, cert_file, keystore_file, store_pass):
    cmd = "keytool -importcert -trustcacerts -alias {0} " \
          "-file {1} -keystore {2} -storepass {3} " \
          "-noprompt".format(alias, cert_file, keystore_file, store_pass)
    return exec_cmd(cmd)


def get_server_certificate(host, port, filepath, server_hostname=""):
    server_hostname = server_hostname or host

    conn = ssl.create_connection((host, port))
    context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
    sock = context.wrap_socket(conn, server_hostname=server_hostname)
    cert = ssl.DER_cert_to_PEM_cert(sock.getpeercert(True))

    with open(filepath, "w") as f:
        f.write(cert)
    return cert
