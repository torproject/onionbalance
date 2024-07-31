# Installing Onionbalance

!!! warning

    This section refers to the older v2 codebase.
    Although outdated, it's still available for historic purposes.

Onionbalance requires at least one system that is running the
Onionbalance management server.

The Onionbalance software does not need to be installed on the backend
servers which provide the onion service content (i.e. web site, IRC
server etc.).

Onionbalance is not yet packaged for most Linux and BSD. The tool can be
installed from PyPI or directly from the Git repository:

```console
# pip install onionbalance
```

or

```console
$ git clone https://github.com/asn-d6/onionbalance.git
$ cd onionbalance
# python setup.py install
```

If you are running Debian Jessie (with backports enabled) or later you
can install Onionbalance with the following command:

```console
# apt-get install onionbalance
```

There is also a python 3 based package available in Fedora \>= 25:

```console
# yum install python3-onionbalance
```

For CentOS or RedHat 7 there is a python 2 based package available in
the EPEL Repository:

```console
# yum install python2-onionbalance
```

All tagged releases on Github or PyPi are signed with my GPG key:

    pub   4096R/0x3B0D706A7FBFED86 2013-06-27 [expires: 2016-07-11]
          Key fingerprint = 7EFB DDE8 FD21 11AE A7BE  1AA6 3B0D 706A 7FBF ED86
    uid                 [ultimate] Donncha O'Cearbhaill <donncha@donncha.is>
    sub   3072R/0xD60D64E73458F285 2013-06-27 [expires: 2016-07-11]
    sub   3072R/0x7D49FC2C759AA659 2013-06-27 [expires: 2016-07-11]
    sub   3072R/0x2C9C6F4ABBFCF7DD 2013-06-27 [expires: 2016-07-11]

Now that Onionbalance is installed, please move to
[Installing Tor](installing_tor.md).
