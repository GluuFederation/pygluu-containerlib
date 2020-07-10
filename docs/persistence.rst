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

Couchbase
=========

.. module:: pygluu.containerlib.persistence.couchbase

.. autofunction:: render_couchbase_properties

.. autofunction:: get_couchbase_user

.. autofunction:: get_couchbase_password

.. autofunction:: get_couchbase_mappings

.. autofunction:: get_couchbase_conn_timeout

.. autofunction:: get_couchbase_conn_max_wait

.. autofunction:: get_couchbase_scan_consistency

.. autofunction:: sync_couchbase_cert

.. autofunction:: sync_couchbase_truststore

.. autoclass:: RestClient
    :members:
    :private-members:
    :undoc-members:

.. autoclass:: N1qlClient
    :members:
    :private-members:
    :undoc-members:

.. autoclass:: CouchbaseClient
    :members:
    :private-members:
    :undoc-members:

Hybrid
======

.. module:: pygluu.containerlib.persistence.hybrid

.. autofunction:: render_hybrid_properties
