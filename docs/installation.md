# Installation

## Debian package

A package for Onionbalance should be available for [Debian][]-like systems.

    sudo apt-get install onionbalance

This will also install the [Tor daemon][] and other needed dependencies.

[Debian]: https://www.debian.org
[Tor daemon]: https://gitlab.torproject.org/tpo/core/tor

## Python package

Onionbalance is available as a [Python][] package [through PyPI][] and can be
installed in a number of ways.

The [Python][] package installation procedure will handle all the Python
dependencies, but won't install the [Tor daemon][] package, which should be
installed separately, preferentially through your operating system package
manager. Example: in a [Debian][]-like system, run

    sudo apt install tor

[Python]: https://python.org
[through PyPI]: https://pypi.org/project/onionbalance

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

## Global installation from source

!!! warning "Conflict with system-wide packages"

    The following procedure might create conflict with system-wide Python
    software installed through the operating system package manager,
    and therefore is not recommended except if you know what you're doing.

To build from source, first get the code:

    git clone https://gitlab.torproject.org/tpo/onion-services/onionbalance

Then switch to the working copy folder and install the needed dependencies:

    cd onionbalance
    sudo apt-get install -y python-is-python3 python3-pip
    sudo python3 -m pip install . --break-system-packages

## Local installation from source

It's also possible to run it directly from the [Git repository][], useful
if you plan to [hack on it](hacking.md).

The recommended way is to clone the Onionbalance repository and setup
a [virtualenv][]:

    sudo apt-get install -y python-is-python3 python3-pip
    git clone https://gitlab.torproject.org/tpo/onion-services/onionbalance
    cd onionbalance
    python3 -m venv venv
    source venv/bin/activate
    pip3 install -r requirements.txt
    pip3 install -r test-requirements.txt

Then Onionbalance can be run directly from the working copy:

    ./onionbalance.py

[Git repository]: https://gitlab.torproject.org/tpo/onion-services/onionbalance

!!! note "Environment activation"

    The [virtualenv][] should be activated in order to run Onionbalance.

    This means that that a command like `source venv/bin/activate`
    should be user before running Oniobalance, like after system
    reboots, fresh command line shells or inside scripts.
