import base64
import contextlib
from typing import AnyStr


try:
    # try with faster implementation
    from cryptography.hazmat.primitives.ciphers import Cipher
    from cryptography.hazmat.primitives.ciphers import algorithms
    from cryptography.hazmat.primitives.ciphers import modes
    from cryptography.hazmat.primitives import padding
    from cryptography.hazmat.backends import default_backend

    class CryptographyHelper:
        @classmethod
        def encode_text(cls, text: AnyStr, key: AnyStr) -> bytes:
            with contextlib.suppress(AttributeError):
                # ``key`` must be a ``bytes``
                key = key.encode()

            with contextlib.suppress(AttributeError):
                # ``text`` must be a ``bytes``
                text = text.encode()

            cipher = Cipher(
                algorithms.TripleDES(key), modes.ECB(), backend=default_backend(),
            )
            encryptor = cipher.encryptor()

            padder = padding.PKCS7(algorithms.TripleDES.block_size).padder()
            padded_data = padder.update(text) + padder.finalize()

            encrypted_text = encryptor.update(padded_data) + encryptor.finalize()
            return base64.b64encode(encrypted_text)

        @classmethod
        def decode_text(cls, encoded_text: AnyStr, key: AnyStr) -> bytes:
            encoded_text = base64.b64decode(encoded_text)

            with contextlib.suppress(AttributeError):
                # ``key`` must be a ``bytes``
                key = key.encode()

            cipher = Cipher(
                algorithms.TripleDES(key), modes.ECB(), backend=default_backend(),
            )
            decryptor = cipher.decryptor()

            unpadder = padding.PKCS7(algorithms.TripleDES.block_size).unpadder()
            padded_data = decryptor.update(encoded_text) + decryptor.finalize()

            # decrypt the encrypted text
            return unpadder.update(padded_data) + unpadder.finalize()

except ImportError:  # pragma: no cover
    # fallback to default implementation
    import warnings
    import pyDes

    class PydesHelper:
        @classmethod
        def encode_text(cls, text: AnyStr, key: AnyStr) -> bytes:
            warnings.warn(
                "Using slow implementation based on pyDes. "
                "Please install cryptography package and "
                "use CryptographyHelper.encode_text instead."
            )
            cipher = pyDes.triple_des(key, pyDes.ECB, padmode=pyDes.PAD_PKCS5)
            encrypted_text = cipher.encrypt(text)
            return base64.b64encode(encrypted_text)

        @classmethod
        def decode_text(cls, encoded_text: AnyStr, key: AnyStr) -> bytes:
            warnings.warn(
                "Using slow implementation based on pyDes. "
                "Please install cryptography package and "
                "use CryptographyHelper.decode_text instead."
            )
            text = base64.b64decode(encoded_text)
            cipher = pyDes.triple_des(key, pyDes.ECB, padmode=pyDes.PAD_PKCS5)
            return cipher.decrypt(text)
