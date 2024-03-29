Persistence
~~~~~~~~~~~

.. module:: pygluu.containerlib.persistence

.. autofunction:: render_salt

.. autofunction:: render_gluu_properties

LDAP
====

.. module:: pygluu.containerlib.persistence.ldap

.. autofunction:: render_ldap_properties

.. autofunction:: sync_ldap_truststore

.. autoclass:: LdapClient
    :members:
    :private-members:

Couchbase
=========

.. module:: pygluu.containerlib.persistence.couchbase

.. autofunction:: render_couchbase_properties

.. autofunction:: get_couchbase_user

.. autofunction:: get_couchbase_password

.. autodata:: get_encoded_couchbase_password

.. autofunction:: get_couchbase_superuser

.. autofunction:: get_couchbase_superuser_password

.. autodata:: get_encoded_couchbase_superuser_password

.. autofunction:: get_couchbase_mappings

.. autofunction:: get_couchbase_conn_timeout

.. autofunction:: get_couchbase_conn_max_wait

.. autofunction:: get_couchbase_scan_consistency

.. autofunction:: sync_couchbase_truststore

.. autoclass:: BaseClient
    :members:
    :private-members:

.. autoclass:: RestClient
    :members:
    :private-members:

.. autoclass:: N1qlClient
    :members:
    :private-members:

.. autoclass:: CouchbaseClient
    :members:
    :private-members:

SQL
===

.. module:: pygluu.containerlib.persistence.sql

.. autoclass:: SQLClient
    :members:
    :private-members:

Spanner
=======

.. module:: pygluu.containerlib.persistence.spanner

.. autoclass:: SpannerClient
    :members:
    :private-members:

Hybrid
======

.. module:: pygluu.containerlib.persistence.hybrid

.. autofunction:: render_hybrid_properties
