#!/usr/bin/env bash
#
# Script to install Tor on Debian-like systems
#

# Parameters
DIRNAME="`dirname $0`"
KEYRING="/usr/share/keyrings/deb.torproject.org-keyring.gpg"

# Error and output handling
set -ex

# Get distro metadata
source /etc/os-release

# Configure repository
cat <<-EOF | sudo tee /etc/apt/sources.list.d/tor.list
deb     [signed-by=${KEYRING}] https://deb.torproject.org/torproject.org $VERSION_CODENAME main
deb-src [signed-by=${KEYRING}] https://deb.torproject.org/torproject.org $VERSION_CODENAME main
EOF

# Get the keyring
sudo $DIRNAME/get-tor-debian-key $KEYRING

# Install Tor
sudo apt-get update
sudo apt-get install -y tor deb.torproject.org-keyring
