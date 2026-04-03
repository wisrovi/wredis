Deprecation Policy
==================

This document outlines the deprecation policy for WRedis. It applies to all
releases starting from version 1.0.0 and governs how features, APIs, and
behaviors are marked as deprecated and eventually removed.

Version Numbering Scheme
------------------------

WRedis follows `Semantic Versioning 2.0.0 <https://semver.org/>`_ (SemVer).
Version numbers take the form ``MAJOR.MINOR.PATCH``:

- **MAJOR**: Incompatible API changes.
- **MINOR**: Backward-compatible functionality additions.
- **PATCH**: Backward-compatible bug fixes.

Pre-release versions use the suffixes ``alpha``, ``beta``, and ``rc``
(release candidate). Pre-release versions are not covered by this policy.

LTS Support Timeline
--------------------

WRedis 1.0.0 is designated as a Long-Term Support (LTS) release. The LTS
support timeline is as follows:

.. list-table::
   :header-rows: 1
   :widths: 30 30 40

   * - Phase
     - Duration
     - Description
   * - Active Support
     - 18 months from release
     - Bug fixes, security patches, minor feature additions, and
       compatibility updates.
   * - Maintenance Support
     - 18 months after Active Support ends
     - Critical security fixes and high-severity bug fixes only. No new
       features.
   * - End of Life (EOL)
     - 36 months from release
     - No further updates. Users are expected to have migrated to a
       supported major version.

The minimum LTS support window for any major release is **36 months**
(3 years) from the initial release date.

Deprecation Process
-------------------

All deprecations follow a three-phase process designed to give users
adequate time to migrate.

Phase 1: Deprecation Warning
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When a feature, API, or behavior is marked for deprecation:

- A ``DeprecationWarning`` is emitted at runtime whenever the deprecated
  element is used.
- The deprecation is documented in the :doc:`changelog`.
- The feature remains fully functional.
- The deprecation warning must persist for a minimum of **two minor
  versions** before the feature is eligible for removal.

Example::

   import warnings
   warnings.warn(
       "WRedis.connect() is deprecated since v1.2.0 and will be removed "
       "in v2.0.0. Use WRedis.from_url() instead.",
       DeprecationWarning,
       stacklevel=2,
   )

Phase 2: Removal
~~~~~~~~~~~~~~~~

Deprecated features are removed in the **next major version**. Removal
means:

- The code is deleted from the codebase.
- Attempting to use the removed feature raises an ``AttributeError`` or
  equivalent exception.
- The removal is documented in the changelog with a migration reference.

Phase 3: Migration Path
~~~~~~~~~~~~~~~~~~~~~~~

For every deprecation, a migration path **must** be provided:

- The deprecation warning message must include the recommended replacement.
- The :doc:`migration-guide` must contain detailed migration instructions.
- When possible, automated migration scripts or compatibility shims are
  provided during the deprecation window.

What Triggers a Deprecation
---------------------------

A feature may be deprecated for any of the following reasons:

- **API simplification**: A cleaner or more intuitive API replaces an
  existing one.
- **Performance improvement**: A new implementation offers significant
  performance gains over the existing approach.
- **Upstream changes**: Changes in the underlying ``redis-py`` library
  or Redis server require adaptation.
- **Design inconsistency**: An API does not align with the established
  patterns of the library.
- **Redundancy**: Two APIs serve the same purpose and consolidation is
  beneficial.
- **Security concern**: A feature introduces unnecessary risk or violates
  current security best practices.

What Does NOT Get Deprecated
----------------------------

The following are **never** subject to deprecation or removal within a
major version series:

- **Security fixes**: Patches for vulnerabilities are always applied and
  never deprecated.
- **Bug fixes**: Corrections to incorrect behavior are never deprecated.
- **Backward-compatible additions**: New features that do not alter
  existing behavior are never deprecated.
- **Public type signatures**: Return types and parameter types of public
  APIs are not changed in a backward-incompatible way within a major
  version.

Communication Channels
----------------------

Deprecation notices are communicated through the following channels:

- **Changelog**: Every deprecation and removal is recorded in the
  :doc:`changelog` under the relevant version entry.
- **Release notes**: GitHub Releases include a summary of deprecations
  and required migration steps.
- **Runtime warnings**: ``DeprecationWarning`` is emitted at runtime for
  deprecated features.
- **Documentation**: The :doc:`migration-guide` is updated with migration
  instructions for every deprecation.
- **GitHub Issues**: A tracking issue is created for each deprecation,
  labeled ``deprecation``.
- **GitHub Discussions**: Major deprecations are announced in the
  project's Discussions tab for community visibility.

Past Deprecations
-----------------

The following are hypothetical examples illustrating how deprecations
would appear in WRedis 1.x:

WRedis.connect() (Deprecated in v1.2.0, Removal in v2.0.0)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The ``WRedis.connect(host, port, db)`` method was deprecated in favor of
the more flexible ``WRedis.from_url(url)`` factory method, which supports
additional connection parameters and aligns with ``redis-py`` conventions.

Migration::

   # Before (deprecated)
   redis = WRedis()
   redis.connect("localhost", 6379, db=0)

   # After (recommended)
   redis = WRedis.from_url("redis://localhost:6379/0")

RedisClient.execute_command() (Deprecated in v1.3.0, Removal in v2.0.0)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The ``execute_command()`` method was deprecated in favor of
``execute_raw()`` to avoid naming confusion with the underlying
``redis-py`` client and to clarify that the method sends raw Redis
protocol commands.

Migration::

   # Before (deprecated)
   result = client.execute_command("GET", "mykey")

   # After (recommended)
   result = client.execute_raw("GET", "mykey")

sync_mode parameter (Deprecated in v1.4.0, Removal in v2.0.0)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The ``sync_mode`` parameter on ``WRedis.__init__()`` was deprecated as the
library moved to a fully async-first design. Users requiring synchronous
operation should use the ``WRedis.sync`` property, which returns a
synchronous client wrapper.

Migration::

   # Before (deprecated)
   redis = WRedis(sync_mode=True)

   # After (recommended)
   redis = WRedis().sync

Python Version Support Policy
-----------------------------

WRedis supports all Python versions that are actively maintained by the
Python core team, as listed on the
`Python releases page <https://devguide.python.org/versions/>`_.

Current support matrix for WRedis 1.x:

.. list-table::
   :header-rows: 1
   :widths: 25 25 50

   * - Python Version
     - Status
     - Notes
   * - 3.10
     - Supported
     - Minimum supported version.
   * - 3.11
     - Supported
     - Full support.
   * - 3.12
     - Supported
     - Full support.
   * - 3.13
     - Supported
     - Full support.

When a Python version reaches end-of-life:

1. WRedis will continue to work on that version but will no longer run
   CI tests against it.
2. A deprecation warning will be issued in the next minor version.
3. Support will be dropped in the next major version.

New Python versions are added to the support matrix in the minor release
following their stable release by the Python core team.

Redis Version Compatibility Policy
----------------------------------

WRedis tracks compatibility with Redis server versions and the
``redis-py`` client library.

Redis Server Compatibility
~~~~~~~~~~~~~~~~~~~~~~~~~~

WRedis 1.x is tested and compatible with the following Redis server
versions:

.. list-table::
   :header-rows: 1
   :widths: 25 25 50

   * - Redis Version
     - Status
     - Notes
   * - 6.2
     - Supported
     - Minimum supported version.
   * - 7.0
     - Supported
     - Full support.
   * - 7.2
     - Supported
     - Full support.
   * - 8.0
     - Supported
     - Full support.

When a Redis server version reaches end-of-life (as determined by the
Redis project), WRedis will:

1. Continue to function but will no longer test against that version.
2. May drop explicit support in a future major release if the
   underlying ``redis-py`` library does so.

redis-py Dependency
~~~~~~~~~~~~~~~~~~~

WRedis requires ``redis>=5.0.0``. The minimum version is updated when:

- A new ``redis-py`` release introduces features that WRedis depends on.
- A security vulnerability is fixed in a newer ``redis-py`` release.
- The current minimum ``redis-py`` version reaches end-of-life.

Emergency Security Exception Process
------------------------------------

In the event of a critical security vulnerability, the standard
deprecation process may be bypassed under the following conditions:

1. **Severity**: The vulnerability is rated CVSS 7.0 or higher, or
   poses an immediate risk to user data or system integrity.
2. **No viable workaround**: There is no backward-compatible fix that
   adequately mitigates the risk.
3. **Maintainer consensus**: At least two core maintainers agree that
   immediate action is required.

When an emergency security exception is invoked:

- The breaking change is released as a **patch version** if possible, or
  a **minor version** if the change is substantial.
- A detailed advisory is published on GitHub Security Advisories.
- The changelog entry is marked with a ``[SECURITY]`` tag.
- Affected users are notified through GitHub Discussions and any
  available announcement channels.
- A migration guide is published concurrently with the release.

Emergency security releases are exempt from the two-minor-version
deprecation window. However, every effort is made to preserve backward
compatibility even in security-critical situations.

Reporting Security Issues
~~~~~~~~~~~~~~~~~~~~~~~~~

Security vulnerabilities should be reported privately through the
project's `SECURITY.md <https://github.com/wisrovi/wredis/blob/main/SECURITY.md>`_
process. Do not file security issues as public GitHub Issues.

Contact
-------

For questions about this policy, deprecations, or migration assistance:

- **GitHub Issues**: https://github.com/wisrovi/wredis/issues
- **GitHub Discussions**: https://github.com/wisrovi/wredis/discussions
- **Email**: wisrovi.rodriguez@gmail.com
