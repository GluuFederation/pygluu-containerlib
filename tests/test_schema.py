import pytest


# source schema (JSON string)
SOURCE_SCHEMA_EXAMPLE = """{
    "schemaFile": "77-customAttributes.ldif",
    "attributeTypes": [
        {
        "desc": "Stores the unique identifier (bcid) for a user on BioID`s biometric service",

            "equality": "caseIgnoreMatch",
            "names": [
                "oxBiometricDevices"
            ],
            "multivalued": true,
            "oid": "oxAttribute",
            "substr": "caseIgnoreSubstringsMatch",
            "syntax": "1.3.6.1.4.1.1466.115.121.1.15",
            "x_origin": "Gluu created attribute"
        },
        {
        "desc": "Stores the unique identifier for a user (userid) on DUO`s 2fa service",

            "equality": "caseIgnoreMatch",
            "names": [
                "oxDuoDevices"
            ],
            "multivalued": true,
            "oid": "oxAttribute",
            "substr": "caseIgnoreSubstringsMatch",
            "syntax": "1.3.6.1.4.1.1466.115.121.1.15",
            "x_origin": "Gluu created attribute"
        }
    ],
    "objectClasses": [
        {
            "kind": "AUXILIARY",
            "may": [
                "telephoneNumber",
                "mobile",
                "carLicense",
                "facsimileTelephoneNumber"
            ],
            "names": [
                "gluuCustomPerson"
            ],
            "oid": "oxObjectClass",
            "sup": [
                "top"
            ],
            "x_origin": "Gluu - Custom person objectclass",
            "sql": {"ignore": true}
        }
    ],
    "oidMacros": {
        "oxAttribute": "oxPublished:3",
        "oxMatchRules": "oxPublished:2",
        "oxObjectClass": "oxPublished:4",
        "oxOrgOID": "1.3.6.1.4.1.48720",
        "oxPublished": "oxOrgOID:1",
        "oxReserved": "oxOrgOID:0",
        "oxSyntax": "oxPublished:1"
    }
}"""

#: generated schema in LDIF format
DST_SCHEMA_EXAMPLE_LDIF = """dn: cn=schema
objectClass: top
objectClass: ldapSubentry
objectClass: subschema
cn: schema
attributeTypes: ( 1.3.6.1.4.1.48720.1.3.1 NAME 'oxBiometricDevices'
  DESC 'Stores the unique identifier (bcid) for a user on BioID`s biometric service'
  EQUALITY caseIgnoreMatch
  SUBSTR caseIgnoreSubstringsMatch
  SYNTAX 1.3.6.1.4.1.1466.115.121.1.15
  X-ORIGIN 'Gluu created attribute' )
attributeTypes: ( 1.3.6.1.4.1.48720.1.3.2 NAME 'oxDuoDevices'
  DESC 'Stores the unique identifier for a user (userid) on DUO`s 2fa service'
  EQUALITY caseIgnoreMatch
  SUBSTR caseIgnoreSubstringsMatch
  SYNTAX 1.3.6.1.4.1.1466.115.121.1.15
  X-ORIGIN 'Gluu created attribute' )
objectClasses: ( 1.3.6.1.4.1.48720.1.4.1 NAME 'gluuCustomPerson'
  SUP ( top )
  AUXILIARY
  MAY ( telephoneNumber $ mobile $ carLicense $ facsimileTelephoneNumber )
  X-ORIGIN 'Gluu - Custom person objectclass' )

"""

# generated schema in plaintext format
DST_SCHEMA_EXAMPLE_PLAINTEXT = """objectIdentifier oxOrgOID        1.3.6.1.4.1.48720
objectIdentifier oxReserved      oxOrgOID:0
objectIdentifier oxPublished     oxOrgOID:1
objectIdentifier oxSyntax        oxPublished:1
objectIdentifier oxMatchRules    oxPublished:2
objectIdentifier oxAttribute     oxPublished:3
objectIdentifier oxObjectClass   oxPublished:4

attributetype ( oxAttribute NAME 'oxBiometricDevices'
\tDESC 'Stores the unique identifier (bcid) for a user on BioID`s biometric service'
\tEQUALITY caseIgnoreMatch
\tSUBSTR caseIgnoreSubstringsMatch
\tSYNTAX 1.3.6.1.4.1.1466.115.121.1.15
\tX-ORIGIN 'Gluu created attribute' )

attributetype ( oxAttribute NAME 'oxDuoDevices'
\tDESC 'Stores the unique identifier for a user (userid) on DUO`s 2fa service'
\tEQUALITY caseIgnoreMatch
\tSUBSTR caseIgnoreSubstringsMatch
\tSYNTAX 1.3.6.1.4.1.1466.115.121.1.15
\tX-ORIGIN 'Gluu created attribute' )

objectclass ( oxObjectClass NAME 'gluuCustomPerson'
\tSUP ( top )
\tAUXILIARY
\tMAY ( telephoneNumber $ mobile $ carLicense $ facsimileTelephoneNumber )
\tX-ORIGIN 'Gluu - Custom person objectclass' )"""


@pytest.mark.parametrize("schema_type, output", [
    ("ldif", DST_SCHEMA_EXAMPLE_LDIF),
    ("", DST_SCHEMA_EXAMPLE_PLAINTEXT),
])
def test_generate_ldap_schema(schema_type, output):
    from pygluu.containerlib.schema import generate_ldap_schema
    assert generate_ldap_schema(SOURCE_SCHEMA_EXAMPLE, schema_type) == output  # nosec: B101
