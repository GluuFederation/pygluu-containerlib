import base64
import contextlib
import logging
from typing import AnyStr

logger = logging.getLogger(__name__)

try:
    # try with faster implementation
    from cryptography.hazmat.primitives.ciphers import Cipher
    from cryptography.hazmat.primitives.ciphers import algorithms
    from cryptography.hazmat.primitives.ciphers import modes
    from cryptography.hazmat.primitives import padding
    from cryptography.hazmat.backends import default_backend

    def encode_text(text: AnyStr, key: AnyStr) -> bytes:
        with contextlib.suppress(AttributeError):
            # ``key`` must be a ``bytes``
            key = key.encode()

        with contextlib.suppress(AttributeError):
            # ``text`` must be a ``bytes``
            text = text.encode()

        cipher = Cipher(
            algorithms.TripleDES(key),
            modes.ECB(),
            backend=default_backend(),
        )
        encryptor = cipher.encryptor()

        padder = padding.PKCS7(algorithms.TripleDES.block_size).padder()
        padded_data = padder.update(text) + padder.finalize()

        encrypted_text = encryptor.update(padded_data) + encryptor.finalize()
        return base64.b64encode(encrypted_text)

    def decode_text(encoded_text: AnyStr, key: AnyStr) -> bytes:
        encoded_text = base64.b64decode(encoded_text)

        with contextlib.suppress(AttributeError):
            # ``key`` must be a ``bytes``
            key = key.encode()

        cipher = Cipher(
            algorithms.TripleDES(key),
            modes.ECB(),
            backend=default_backend(),
        )
        decryptor = cipher.decryptor()

        unpadder = padding.PKCS7(algorithms.TripleDES.block_size).unpadder()
        padded_data = decryptor.update(encoded_text) + decryptor.finalize()

        # decrypt the encrypted text
        return unpadder.update(padded_data) + unpadder.finalize()

except ImportError:
    # fallback to default implementation
    import pyDes

    logger.warning(
        "Using slow pyDes-based encode_text and decode_text functions. "
        "Please consider to install 'cryptography' package first "
        "for faster implementation"
    )

    def encode_text(text: AnyStr, key: AnyStr) -> bytes:
        cipher = pyDes.triple_des(key, pyDes.ECB, padmode=pyDes.PAD_PKCS5)
        encrypted_text = cipher.encrypt(text)
        return base64.b64encode(encrypted_text)

    def decode_text(encoded_text: AnyStr, key: AnyStr) -> bytes:
        text = base64.b64decode(encoded_text)
        cipher = pyDes.triple_des(key, pyDes.ECB, padmode=pyDes.PAD_PKCS5)
        return cipher.decrypt(text)
