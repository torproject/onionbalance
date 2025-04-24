# Onionbalance ChangeLog

## v0.2.4 - 2025-04-24

* Packaging:
    * Updated and improved Debian packaging
      ([tpo/onion-services/onionbalance#46][]).

* Documentation:
    * Refactor ([tpo/onion-services/onionbalance#37][]):
        * Updated and moved some of the old v2 docs to the "main" docs.
        * Updated and moved the v3 docs to the "main" docs.
        * Removed the old v2 docs.
        * Added an [API](api.md) page.
    * Updated [tutorial page](tutorial.md).
    * New [security page](security.md), thanks to Pascal Tippe
      ([tpo/onion-services/onionbalance#25][]).
    * New [troubleshooting page](troubleshooting.md).

[tpo/onion-services/onionbalance#46]: https://gitlab.torproject.org/tpo/onion-services/onionbalance/-/issues/46
[tpo/onion-services/onionbalance#37]: https://gitlab.torproject.org/tpo/onion-services/onionbalance/-/issues/37
[tpo/onion-services/onionbalance#25]: https://gitlab.torproject.org/tpo/onion-services/onionbalance/-/issues/25

## v0.2.3 - 2024-12-11

* Maintenance:
    * Fix used-before-assignment ([tpo/onion-services/onionbalance!4][]).
    * Fix import on functional tests ([tpo/onion-services/onionbalance!5][]).
    * Drop dependency on future (thanks to Lumir Balhar) ([tpo/onion-services/onionbalance!6][]).
    * The v2 codebase was finally removed (thanks to Federico Ceratto)
      ([tpo/onion-services/onionbalance#8][]).
    * Fix coding style issues found by flake8 ([tpo/onion-services/onionbalance!9][]).
* Workflow:
    * CI was fixed and updated, and now uses [GitLab CI][].
    * Added Git tags to all previous releases.
* Repository:
    * The Onionbalance repository was moved to
      [gitlab.torproject.org/tpo/onion-services/onionbalance][onionbalance-repo].
    * The old repository at [github.com/torproject/onionbalance][old-repository] is
      configured as a mirror.
* Documentation:
    * Onionbalance documentation was migrated to [Onion MkDocs][], then updated and
      included in the [Onion Services Ecosystem][ecosystem]
      ([tpo/onion-services/onionbalance#28][]).
    * New canonical documentation URL is
      [onionservices.torproject.org/apps/base/onionbalance][onionbalance-docs].
      The old documentation URLs are kept as redirects
      (https://onionbalance-v3.readthedocs.io and
      https://onionbalance.readthedocs.io).
    * Updated this ChangeLog to include dates for all releases.

[tpo/onion-services/onionbalance!4]: https://gitlab.torproject.org/tpo/onion-services/onionbalance/-/merge_requests/4
[tpo/onion-services/onionbalance!5]: https://gitlab.torproject.org/tpo/onion-services/onionbalance/-/merge_requests/5
[tpo/onion-services/onionbalance!6]: https://gitlab.torproject.org/tpo/onion-services/onionbalance/-/merge_requests/6
[tpo/onion-services/onionbalance!9]: https://gitlab.torproject.org/tpo/onion-services/onionbalance/-/merge_requests/9
[tpo/onion-services/onionbalance#8]: https://gitlab.torproject.org/tpo/onion-services/onionbalance/-/issues/8
[GitLab CI]: https://docs.gitlab.com/ee/ci/
[onionbalance-repo]: https://gitlab.torproject.org/tpo/onion-services/onionbalance/
[old-repository]: https://github.com/torproject/onionbalance
[Onion Mkdocs]: https://tpo.pages.torproject.net/web/onion-mkdocs/
[ecosystem]: https://onionservices.torproject.org
[onionbalance-docs]: https://onionservices.torproject.org/apps/base/onionbalance/
[tpo/onion-services/onionbalance#28]: https://gitlab.torproject.org/tpo/onion-services/onionbalance/-/issues/28

## v0.2.2 - 2021-07-29

* Add an OBv3 hacking guide.
* Remove tox and simplify build procedure.
* A single OnionBalance can now support multiple onion services.

## v0.2.1 - 2021-01-26

* v2 codebase now uses Cryptodome instead of the deprecated PyCrypto library.
* v3 codebase is now more flexible when it comes to requiring a live consensus.
  This should increase the reachability of Onionbalance in scenarios where the
  network is having trouble establishing a new consensus.
* v3 support for connecting to the control port through a Unix socket.  Patch
  by Peter Tripp.
* Introduce status socket support for v3 onions. Patch by vporton.
* Sending a SIGHUP signal now reloads the v3 config. Patch by Peter Chung.

## v0.2.0 - 2020-04-24

* Allow migration from Tor to Onionbalance by reading tor private keys directly
  using the `key` directive in the YAML config file. Also update
  `onionbalance-config` to support that.
* Improve `onionbalance-config` for v3 onions. Simplify the output
  directory (and change docs to reflect so) and the wizard suggestions.

## v0.1.9 - 2020-03-12

* Initial support for v3 onions!

## v0.1.8 - 2017-05-02

* Fix a bug which could cause descriptor fetching to crash and stall if an old
  instance descriptor was retrieved from a HSDir ([#64][]).
* Minors fixes to documentation and addition of a tutorial.

[#64]: https://github.com/DonnchaC/onionbalance/issues/64

## v0.1.7 - 2017-02-21

* Add functionality to reconnect to the Tor control port while Onionbalance is
  running. Thank you to Ceysun Sucu for the patch ([#45][]).
* Fix bug where instance descriptors were not updated correctly when an
  instance address was listed under multiple master service ([#49][]).
* Improve performance by only requesting each unique instance descriptor once
  per round, rather once for each time it was listed in the config file ([#51][]).
* Fix bug where an exception was raised when the status socket location did not
  exist.
* Improve the installation documentation for Debian and Fedora/EPEL
  installations.

[#45]: https://github.com/DonnchaC/onionbalance/issues/45
[#49]: https://github.com/DonnchaC/onionbalance/issues/49
[#51]: https://github.com/DonnchaC/onionbalance/issues/51

## v0.1.6 - 2016-12-13

* Remove unicode tags from the yaml files generated by onionbalance-config.
* Fix bug resulting in invalid instance onion addresses when attempting to
  remove the `.onion` TLD ([#44][]).

[#44]: https://github.com/DonnchaC/onionbalance/issues/44

## v0.1.5 - 2016-09-17

* Log error when Onionbalance does not have permission to read a private key
  ([#34][]).
* Fix bug loading descriptors when an address with .onion extension is listed
  in the configuration file ([#37][]).
* Add support for connecting to the Tor control port over a unix domain socket
  ([#35][]).

[#34]: https://github.com/DonnchaC/onionbalance/issues/34
[#37]: https://github.com/DonnchaC/onionbalance/issues/37
[#35]: https://github.com/DonnchaC/onionbalance/issues/35

## v0.1.4 - 2016-05-02

* Use setproctitle to set a cleaner process title
* Replace the python-schedule dependency with a custom scheduler.
* Add a Unix domain socket which outputs the status of the Onionbalance service
  when a client connects. By default this socket is created at
  `/var/run/onionbalance/control`. Thank you to Federico Ceratto
  for the original socket implementation.
* Add support for handling the `SIGINT` and `SIGTERM`
  signals. Thank you to Federico Ceratto for this feature.
* Upgrade tests to use the stable Tor 0.2.7.x release.
* Fix bug when validating the modulus length of a provided RSA private key.
* Upload distinct service descriptors to each hidden service directory by
  default. The distinct descriptors allows up to 60 introduction points or
  backend instances to be reachable by external clients.  Thank you to Ceysun
  Sucu for describing this technique in his Masters thesis.
* Add `INITIAL_DELAY` option to wait longer before initial
  descriptor publication. This is useful when there are many backend instance
  descriptors which need to be downloaded.
* Add configuration option to allow connecting to a Tor control port on a
  different host.
* Remove external image assets when documentation is generated locally instead
  of on ReadTheDocs.

## v0.1.3 - 2015-12-16

* Streamline the integration tests by using Tor and Chutney from the upstream
  repositories.
* Fix bug when `HSFETCH` is called with a `HSDir` argument (3d225fd).
* Remove the `schedule` package from the source code and re-add it as a
  dependency. This Python package is now packaged for Debian.
* Extensively restructure the documentation to make it more comprehensible.
* Add `--version` argument to the command line
* Add configuration options to output log entries to a log file.

## v0.1.2 - 2015-10-08

* Remove dependency on the schedule package to prepare for packaging
  Onionbalance in Debian. The schedule code is now included directly in
  `onionbalance/schedule.py`.
* Fix the executable path in the help messages for onionbalance and
  `onionbalance-config`.

## v0.1.1 - 2015-07-01

* Patch to resolve issue when saving generated torrc files from
  `onionbalance-config` in Python 2.

## v0.1.0 - 2015-06-30

* Initial release
