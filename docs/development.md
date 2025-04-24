# Onionbalance development

Onionbalance development guidelines and workflow are listed here.

## Release procedure

Release cycle workflow.

### Version update

Set the version number:

    ONIONBALANCE_VERSION=0.2.4

Update the version in some files, like:

    dch -i # debian/changelog
    $EDITOR onionbalance/__init__.py

### Regenerate the manpages

Build updated manual pages:

    make manpages

Check:

    man -l docs/man/onionbalance.1
    man -l docs/man/onionbalance-config.1

### Register the changes

Update the ChangeLog:

    $EDITOR ChangeLog

Commit and tag:

    git diff # review
    git commit -a -m "Feat: Onionbalance $ONIONBALANCE_VERSION"
    git tag -s $ONIONBALANCE_VERSION -m "Onionbalance $ONIONBALANCE_VERSION"

Push changes and tags. Example:

    git push origin        && git push upstream
    git push origin --tags && git push upstream --tags

Once a tag is pushed, a [GitLab release][] is created.

[GitLab release]: https://docs.gitlab.com/ee/user/project/releases/

### Build packages

Build the Python package:

    make build-python-package

Install this package in a fresh virtual machine. Example:

    sudo apt-get install -y python3-pip tor
    pip install --break-system-packages \
      dist/onionbalance-$ONIONBALANCE_VERSION-*.whl

Then test it:

    $HOME/.local/bin/onionbalance --version
    $HOME/.local/bin/onionbalance-config --no-interactive

If the package worked, upload it to the [Test PyPI][] instance:

    make upload-python-test-package

Install again the test package, by fetching it from [Test PyPI][], and in
another fresh virtual machine:

    sudo apt-get install -y python3-pip tor
    pip install -i https://pypi.org/simple/ \
                --extra-index-url https://test.pypi.org/simple \
                --break-system-packages \
                onionbalance==$ONIONBALANCE_VERSION

Do the tests again in this new installation.
If the the package works as expected, upload it to PyPI:

    make upload-python-package

Finally, install the package one more time, but now fetching it from [PyPI][],
and in yet another fresh virtual machine:

    sudo apt-get install -y python3-pip tor
    pip install --break-system-packages \
      onionbalance==$ONIONBALANCE_VERSION

Do the tests once more, in this new installation.

[Test PyPI]: https://test.pypi.org
[PyPI]: https://pypi.org

### Announcement

Announce the new release:

* Post a message to the [Tor Forum][], using the [onion-services-announce tag][].
* Send a message to the [tor-announce][] mailing list ONLY in special cases,
  like important security issues (severity `HIGH` or `CRITICAL`).

Template:

```
Subject: [RELEASE] Onionbalance [security] release $ONIONBALANCE_VERSION

Greetings,

We just released [Onionbalance][] $ONIONBALANCE_VERSION, a descriptor publisher
and load balancer for Onion Services.

[This release fixes a security issue. Please upgrade as soon as possible!]

[Onionbalance]: https://onionservices.torproject.org/apps/web/onionbalance

# ChangeLog

$CHANGELOG
```

[tor-announce]: https://lists.torproject.org/cgi-bin/mailman/listinfo/tor-announce
[Tor Forum]: https://forum.torproject.org
[onion-services-announce tag]: https://forum.torproject.org/tag/onion-services-announce
