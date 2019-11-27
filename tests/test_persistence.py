import os


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
    os.environ["GLUU_COUCHBASE_USER"] = ""


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
    os.environ["GLUU_PERSISTENCE_TYPE"] = ""


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

    os.environ["GLUU_PERSISTENCE_TYPE"] = ""
    os.environ["GLUU_PERSISTENCE_LDAP_MAPPING"] = ""
