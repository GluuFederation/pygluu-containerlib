# Changelog

Here you can see an overview of changes between each release.

## Version 2.4.3

Released on December 11th, 2020.

* Added support to execute command in Pod's main container (https://github.com/GluuFederation/pygluu-containerlib/issues/19).
* Added support for Couchbase prefix (https://github.com/GluuFederation/pygluu-containerlib/issues/20).

## Version 2.4.2

Released on November 12th, 2020.

* Fixed remote execution in Kubernetes (https://github.com/GluuFederation/pygluu-containerlib/issues/18).

## Version 2.4.1

Released on November 3rd, 2020.

* Added feature to suppress Couchbase cert verification through environment variable (enabled by default).
* Changed the scope of pod list API (https://github.com/GluuFederation/pygluu-containerlib/issues/17).

## Version 2.4.0

Released on October 29th, 2020.

* Added support for Couchbase cluster certificate verification (disabled by default).
* Added support for generating safe N1QL query.
* Removed `pyDes` wrapper in favor of `cryptography` (https://github.com/GluuFederation/pygluu-containerlib/issues/16).

## Version 2.3.0

Released on September 22nd, 2020.

* Added support for Couchbase superuser access (https://github.com/GluuFederation/pygluu-containerlib/issues/15).

## Version 2.2.0

Released on August 30th, 2020.

* Added validators for persistence type and ldap mapping (https://github.com/GluuFederation/pygluu-containerlib/issues/14).

## Version 2.1.2

Released on August 13th, 2020.

* Fixed incorrect RClone config due to special chars and whitespaces in user and/or password value. Reference: https://github.com/GluuFederation/pygluu-containerlib/issues/13.

## Version 2.1.1

Released on August 9th, 2020.

* Fix `rclone.conf` where username is always hardcoded. Reference: https://github.com/GluuFederation/pygluu-containerlib/issues/12.

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
