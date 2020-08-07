# Changelog

Here you can see an overview of changes between each release.

## Version 2.1.0

Released on August 7th, 2020.

* Added new LDAP mapping `session`.
* Added new Couchbase bucket mapping `gluu_session`.
* Added lazy-loaded Couchbase REST and N1QL API clients.

## Version 2.0.1

Released on July 30th, 2020.

* Fixed uploading/downloading files with certain extensions using RClone wrapper. Reference: https://github.com/GluuFederation/pygluu-containerlib/issues/11.

## Version 2.0.0

Released on July 18th, 2020.

* Support for Python 3.6 and above.
* Dropped support for Python 2.
* Added meta clients to interact with Docker and Kubernetes API.
* Added support for cryptography library as a drop-in replacement for pyDes.
* Deprecated pyDes-based encode/decode text utilities (preserved as backward-compat only).
* Added RClone client to interact with Jackrabbit WebDAV.
* Added support for Gluu Server v4.2.
* Added internal docs based on sphinx.

## Version 1.1.0

Released on May 11th, 2020.

* Removed unused Couchbase config and/or secret.
* Added environment variables for Couchbase connection timeout, connection max wait, and scan consistency.

## Version 1.0.0

Released on November 20th, 2019.

* Support for Python 2.
* Partial support for Python 3 through `six` helpers.
* Helpers to interact with config backends (supports Consul and k8s configmaps).
* Helpers to interact with secret backends (supports Vault and k8s secrets).
* Helpers to interact with persistence backends (LDAP and Couchbase server).
* Various common helpers to deal with text, encoding/decoding, etc.
