import os
import shutil

import pytest


def test_render_salt(tmpdir, fake_manager):
    from pygluu.containerlib.persistence import render_salt

    tmp = tmpdir.mkdir("pygluu")
    src = tmp.join("salt.tmpl")
    src.write("encodeSalt = %(encode_salt)s")
    dest = tmp.join("salt")
    render_salt(fake_manager, str(src), str(dest))
    assert dest.read() == f"encodeSalt = {fake_manager.secret.get('encoded_salt')}"


def test_render_gluu_properties(tmpdir):
    from pygluu.containerlib.persistence import render_gluu_properties

    persistence_type = "ldap"
    os.environ["GLUU_PERSISTENCE_TYPE"] = persistence_type

    tmp = tmpdir.mkdir("pygluu")
    src = tmp.join("gluu.properties.tmpl")
    src.write("""
persistence.type=%(persistence_type)s
certsDir=%(certFolder)s
pythonModulesDir=%(gluuOptPythonFolder)s/libs
""".strip())
    dest = tmp.join("gluu.properties")

    expected = f"""
persistence.type={persistence_type}
certsDir=/etc/certs
pythonModulesDir=/opt/gluu/python/libs
""".strip()

    render_gluu_properties(str(src), str(dest))
    assert dest.read() == expected
    os.environ["GLUU_PERSISTENCE_TYPE"] = ""

# ====
# LDAP
# ====


def test_render_ldap_properties(tmpdir, fake_manager):
    from pygluu.containerlib.persistence.ldap import render_ldap_properties

    tmpl = """
bindDN: %(ldap_binddn)s
bindPassword: %(encoded_ox_ldap_pw)s
servers: %(ldap_hostname)s:%(ldaps_port)s
ssl.trustStoreFile: %(ldapTrustStoreFn)s
ssl.trustStorePin: %(encoded_ldapTrustStorePass)s
""".strip()

    host, port = "localhost", 1636
    expected = f"""
bindDN: {fake_manager.config.get("ldap_binddn")}
bindPassword: {fake_manager.secret.get("encoded_ox_ldap_pw")}
servers: {host}:{port}
ssl.trustStoreFile: {fake_manager.config.get("ldapTrustStoreFn")}
ssl.trustStorePin: {fake_manager.secret.get("encoded_ldapTrustStorePass")}
""".strip()

    tmp = tmpdir.mkdir("pygluu")
    src = tmp.join("gluu-ldap.properties.tmpl")
    src.write(tmpl)
    dest = tmp.join("gluu-ldap.properties")

    render_ldap_properties(fake_manager, str(src), str(dest))
    assert dest.read() == expected


def test_sync_ldap_truststore(tmpdir, fake_manager):
    from pygluu.containerlib.persistence.ldap import sync_ldap_truststore

    dest = tmpdir.mkdir("pygluu").join("opendj.pkcs12")
    sync_ldap_truststore(fake_manager, str(dest))
    assert dest.read() == fake_manager.secret.get("ldap_pkcs12_base64")

# =========
# Couchbase
# =========


def test_get_couchbase_user(fake_manager):
    from pygluu.containerlib.persistence.couchbase import get_couchbase_user

    os.environ["GLUU_COUCHBASE_USER"] = "root"
    assert get_couchbase_user(fake_manager) == "root"
    os.environ.pop("GLUU_COUCHBASE_USER", None)


def test_get_couchbase_password(tmpdir, fake_manager):
    from pygluu.containerlib.persistence.couchbase import get_couchbase_password

    passwd_file = tmpdir.mkdir("pygluu").join("couchbase_password")
    passwd_file.write("secret")

    os.environ["GLUU_COUCHBASE_PASSWORD_FILE"] = str(passwd_file)
    assert get_couchbase_password(fake_manager) == "secret"
    os.environ.pop("GLUU_COUCHBASE_PASSWORD_FILE", None)


def test_get_encoded_couchbase_password(tmpdir, fake_manager):
    from pygluu.containerlib.persistence.couchbase import get_encoded_couchbase_password

    passwd_file = tmpdir.mkdir("pygluu").join("couchbase_password")
    passwd_file.write("secret")

    os.environ["GLUU_COUCHBASE_PASSWORD_FILE"] = str(passwd_file)
    assert get_encoded_couchbase_password(fake_manager) != "secret"
    os.environ.pop("GLUU_COUCHBASE_PASSWORD_FILE", None)


@pytest.mark.skipif(
    shutil.which("keytool") is None,
    reason="requires keytool executable"
)
def test_sync_couchbase_truststore(tmpdir, fake_manager):
    from pygluu.containerlib.persistence.couchbase import sync_couchbase_truststore

    tmp = tmpdir.mkdir("pygluu")
    keystore_file = tmp.join("couchbase.jks")
    cert_file = tmp.join("couchbase.crt")

    # dummy cert
    cert_file.write("""-----BEGIN CERTIFICATE-----
MIIEGDCCAgCgAwIBAgIRANslKJCe/whYi01rkUOAxh0wDQYJKoZIhvcNAQELBQAw
DTELMAkGA1UEAxMCQ0EwHhcNMTkxMTI1MDQwOTQ4WhcNMjEwNTI1MDQwOTE4WjAP
MQ0wCwYDVQQDEwRnbHV1MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA
05TqppxdpSP9vzQP42YFPM79K3TdOFmsCJLMnKRkeR994MGra6JQ75/+vYmKXJaU
Bo3/VieU2pGaAsXI7MqNfXQcKSwAoGU03xqoBUS8INIYX+Cr7q8jFp1q2VLqpNlt
zWZQsee2TUIsa7MzJ5UK7QnaqK4uadl9XHlkRdXC5APecJoRJK4K1UZ59TyiMisz
Dqf+DrmCaJpIPph4Ro9TZMdoE9CX2mFz6Q+ItaSXvyNqUabip7iIwFf3Mu1pal98
AogsfKcfvu+ki93slrJ6jiDIi5B+D0gbA4E03ncgdfQ8Vs55BZbI0N5uEypfI0ky
LQ6201p4bRRXX4LKooObCwIDAQABo3EwbzAOBgNVHQ8BAf8EBAMCA7gwHQYDVR0l
BBYwFAYIKwYBBQUHAwEGCCsGAQUFBwMCMB0GA1UdDgQWBBROCOakMthTjAwM7MTP
RnkvLRHMOjAfBgNVHSMEGDAWgBTeSnpdqVZhjCRnCKJFfwiGwnVCvTANBgkqhkiG
9w0BAQsFAAOCAgEAjBOt4xgsiW3BN/ZZ6DehrdmRZRrezwhBWwUrnY9ajmwv0Trs
4sd8EP7RuJsGS5gdUy/qzogSEhUyMz4+iRy/OW9bdzOFe+WDU6Xh9Be/C2Dv9osa
5dsG+Q9/EM9Z2LqKB5/uJJi5xgXdYwRXATDsBdNI8LxQQz0RdCZIJlpqsDEd1qbH
8YX/4cnknuL/7NsqLvn5iZvQcYFA/mfsN8zN52StuRONf1RKdQ3rwT7KehGi7aUa
IWwLEnzLmeZFLUWBl6h2uUMOUe1J8Di176K3SP5pCeb8+gQd5b2ra/IutN7lpISD
7YSStLNCCT33sjbximvX0ur/VipQQO1B/dz9Ua1kPPKV/blTXCiKNf+PpepaFBIp
jIb/dBIq9pLPBWtGz4tCNQIORDBpQjfPpSNH3lEjTyWUOttJYkss6LHAnnQ8COyk
IsbroXkmDKy86qHKlUc7L4REBykLDL7Olm4yQC8Zg46PaG5ymfYVuHd+tC7IZj8H
FRnpMhUJ4+bn+h0kxS4agwb2uCSO4Ge7edViq6ZFZnnfOG6zsz3VJRV71Zw2CQAL
0MxrbeozSHyNrbT2uAGyV85pNJmwZVlBfyKywMWsG3HcoKAhxg//IqNv0pi48Ey9
2xLnWTK3GxoBMh3mpjub+jf6OYDwmh0eBxm+PRMVAe3QB1eG/GGKgEwaTrc=
-----END CERTIFICATE-----""")

    os.environ["GLUU_COUCHBASE_CERT_FILE"] = str(cert_file)
    fake_manager.config.set("couchbaseTrustStoreFn", str(keystore_file))
    sync_couchbase_truststore(fake_manager)
    assert os.path.exists(str(keystore_file))
    os.environ.pop("GLUU_COUCHBASE_CERT_FILE", None)


# ======
# Hybrid
# ======


def test_render_hybrid_properties(tmpdir):
    from pygluu.containerlib.persistence.hybrid import render_hybrid_properties

    os.environ["GLUU_PERSISTENCE_TYPE"] = "hybrid"

    expected = """
storages: ldap, couchbase
storage.default: ldap
storage.ldap.mapping: default
storage.couchbase.mapping: people, groups, authorizations, cache, cache-refresh, tokens
""".strip()

    dest = tmpdir.mkdir("pygluu").join("gluu-hybrid.properties")
    render_hybrid_properties(str(dest))
    assert dest.read() == expected
    os.environ.pop("GLUU_PERSISTENCE_TYPE", None)


def test_render_hybrid_properties_couchbase(tmpdir):
    from pygluu.containerlib.persistence.hybrid import render_hybrid_properties

    os.environ["GLUU_PERSISTENCE_TYPE"] = "hybrid"
    os.environ["GLUU_PERSISTENCE_LDAP_MAPPING"] = "user"

    expected = """
storages: ldap, couchbase
storage.default: couchbase
storage.ldap.mapping: people, groups
storage.couchbase.mapping: cache, cache-refresh, tokens
""".strip()

    dest = tmpdir.mkdir("pygluu").join("gluu-hybrid.properties")
    render_hybrid_properties(str(dest))
    assert dest.read() == expected

    os.environ.pop("GLUU_PERSISTENCE_TYPE", None)
    os.environ.pop("GLUU_PERSISTENCE_LDAP_MAPPING", None)
