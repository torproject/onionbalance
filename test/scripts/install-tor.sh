#!/bin/bash
# Script to install Tor
set -ex

sudo apt install apt-transport-https
echo "deb http://deb.torproject.org/torproject.org bionic main" | sudo tee -a /etc/apt/sources.list
echo "deb-src http://deb.torproject.org/torproject.org bionic main" | sudo tee -a /etc/apt/sources.list

echo "wget -qO- https://deb.torproject.org/torproject.org/A3C4F0F979CAA22CDBA8F512EE8CBC9E886DDD89.asc | gpg --import"
wget -qO- https://deb.torproject.org/torproject.org/A3C4F0F979CAA22CDBA8F512EE8CBC9E886DDD89.asc | gpg --import
echo "gpg --export A3C4F0F979CAA22CDBA8F512EE8CBC9E886DDD89 | sudo apt-key add -"
gpg --export A3C4F0F979CAA22CDBA8F512EE8CBC9E886DDD89 | sudo apt-key add -

sudo apt-get update -qq
sudo apt-get install -qq tor deb.torproject.org-keyring
