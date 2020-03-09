import os


def render_ldap_properties(manager, src: str, dest: str) -> None:
    ldap_url = os.environ.get("GLUU_LDAP_URL", "localhost:1636")
    ldap_hostname, ldaps_port = ldap_url.split(":")

    with open(src) as f:
        txt = f.read()

    with open(dest, "w") as f:
        rendered_txt = txt % {
            "ldap_binddn": manager.config.get("ldap_binddn").decode(),
            "encoded_ox_ldap_pw": manager.secret.get("encoded_ox_ldap_pw").decode(),
            "ldap_hostname": ldap_hostname,
            "ldaps_port": ldaps_port,
            "ldapTrustStoreFn": manager.config.get("ldapTrustStoreFn").decode(),
            "encoded_ldapTrustStorePass": manager.secret.get("encoded_ldapTrustStorePass").decode(),
        }
        f.write(rendered_txt)


def sync_ldap_truststore(manager, dest: str = "") -> None:
    dest = dest or manager.config.get("ldapTrustStoreFn")
    manager.secret.to_file(
        "ldap_pkcs12_base64",
        dest,
        decode=True,
        binary_mode=True,
    )
