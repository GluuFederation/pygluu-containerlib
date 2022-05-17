from pygluu.containerlib.schema.generator import SchemaGenerator


def generate_ldap_schema(src: str, type_: str) -> str:
    """
    Generate the LDAP schema definitions from the JSON data.

    :param src: JSON string contains the source schema.
    :param type_: The schema type to be generated.
    """
    gen = SchemaGenerator(src)

    if type_ == "ldif":
        schema_str = gen.generate_ldif()
    else:
        schema_str = gen.generate_plaintext()
    return schema_str
