# Onionbalance installation

## Debian package

A package for Onionbalance should be available on [Debian][]-like systems.

    sudo apt install onionbalance

This will also install the [Tor daemon][] and other needed dependencies.

[Debian]: https://www.debian.org
[Tor daemon]: https://gitlab.torproject.org/tpo/core/tor

## Python package

Onionbalance is available as a [Python][] package [through PyPI][pypi] and can
be installed in a number of ways.

The [Python][] package installation procedure will handle all the Python
dependencies, but won't install the [Tor daemon][] package, which should be
installed separately, preferentially through your operating system package
manager. Example: in a [Debian][]-like system, run

    sudo apt install -y tor

[Python]: https://python.org
[pypi]: https://pypi.org/project/onionbalance

Once the [Tor daemon][] is installed, proceed installing the [Python][] package.
Some options are detailed below.

### Using pipx

The recommended way to install the Onionbalance from the [Python][] package is
via [pipx][]:

    pipx install onionbalance

[pipx]: https://pipx.pypa.io/stable/

### Using pip and a virtualenv

Another installation option is to use [pip][] with a [virtualenv][]:

    mkdir onionbalance
    cd onionbalance
    python3 -m venv venv
    source venv/bin/activate
    pip install onionbalance

The `onionbalance` folder will store the [virtualenv][], and can also be
used to host Onionbalance configuration and data.

!!! note "Environment activation"

    The [virtualenv][] should be activated in order to run Onionbalance.

    This means that that a command like `source venv/bin/activate`
    should be user before running Oniobalance, like after system
    reboots, fresh command line shells or inside scripts.

[pip]: https://pypi.org/project/pip/
[virtualenv]: https://virtualenv.pypa.io/

### Using pip without a virtualenv

!!! warning "Conflict with system-wide packages"

    The following procedure might create conflict with system-wide Python
    software installed through the operating system package manager,
    and therefore is not recommended except if you know what you're doing.

If you prefer, Onionbalance can also be installed directly using [pip][]
without a [virtualenv][], but **this might conflict with system-wide installed
[Python][] packages**, and therefore is not usually recommended:

    pip install onionbalance --break-system-packages

### Python package installation from source

!!! warning "Conflict with system-wide packages"

    The following procedure might create conflict with system-wide Python
    software installed through the operating system package manager,
    and therefore is not recommended except if you know what you're doing.

To install the [Python][] package from source, first get the code and
install it using [pip][]:

    sudo apt install -y python3-pip
    git clone https://gitlab.torproject.org/tpo/onion-services/onionbalance
    cd onionbalance
    python3 -m pip install . --break-system-packages

The Onionbalance executable will be available usually at your
`$HOME/.local/bin` folder.

System-wide installation from source is also possible. The simpler way
is to invoke the last command above with `sudo`.

    sudo python3 -m pip install . --break-system-packages

For system-wide installations, the Onionbalance executable should be available in
a path like `/usr/local/bin/onionbalance`.

## Running from source

It's also possible to run it directly from the [Git repository][], useful
if you plan to [hack on it](hacking.md):

    git clone https://gitlab.torproject.org/tpo/onion-services/onionbalance
    cd onionbalance

[Git repository]: https://gitlab.torproject.org/tpo/onion-services/onionbalance

There are a number of ways to run from sources after the repository is cloned.

### Local installation from source using Debian packages

When in a [Debian][]-based system, Onionbalance dependencies can be installed
with:

    sudo apt install -y python3 python-is-python3 python3-cryptography \
                        python3-future python3-pycryptodome            \
                        python3-setproctitle python3-stem python3-yaml \
                        tor

The Onionbalance can then run directly from the working copy:

    ./onionbalance.py

### Local installation from source using Python packages

Onionbalance's [Python][] dependencies can be installed directly from
[PyPI][pypi], by setting up a [virtualenv][]:

    sudo apt install -y python-is-python3 python3-pip
    git clone https://gitlab.torproject.org/tpo/onion-services/onionbalance
    cd onionbalance
    python3 -m venv venv
    source venv/bin/activate
    pip3 install -r requirements.txt
    pip3 install -r test-requirements.txt

The Onionbalance can then run directly from the working copy:

    ./onionbalance.py

[Git repository]: https://gitlab.torproject.org/tpo/onion-services/onionbalance

!!! note "Environment activation"

    The [virtualenv][] should be activated in order to run Onionbalance.

    This means that that a command like `source venv/bin/activate`
    should be user before running Oniobalance, like after system
    reboots, fresh command line shells or inside scripts.
