Wait
~~~~

.. module:: pygluu.containerlib.wait

Helpers
=======

Most of the time, users may only need to run ``wait_for`` function to add readiness check. If somehow this function is not sufficient, low-level functions ``wait_for_*`` are available.

High-level Helpers
------------------

.. autofunction:: wait_for

Low-level Helpers
-----------------

.. autofunction:: wait_for_config

.. autofunction:: wait_for_secret

.. autofunction:: wait_for_ldap

.. autofunction:: wait_for_ldap_conn

.. autofunction:: wait_for_couchbase

.. autofunction:: wait_for_couchbase_conn

.. autofunction:: wait_for_oxauth

.. autofunction:: wait_for_oxtrust

.. autofunction:: wait_for_oxd

.. autofunction:: get_wait_max_time

.. autofunction:: get_wait_interval

Exceptions
==========

.. autoexception:: WaitError
