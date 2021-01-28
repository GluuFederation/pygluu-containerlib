# Changelog

Here you can see an overview of changes between each release.

## Version 1.2.0

Released on January 28th, 2021.

* Added support to disable truststore file for Couchbase connection.

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
