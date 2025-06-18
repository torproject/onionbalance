#!/bin/bash
#
# Script to install Chutney, configure a Tor network and wait for the Onion
# Service system to be available.
#

# Ensure chutney codebase is available
if [ ! -d "chutney" ]; then
  git clone https://git.torproject.org/chutney.git
fi

# Go to chutney folder
cd chutney

# Ensure chutney is up-to-date
git pull

# Install dependencies, failing if a virtualenv is not available
pip3 install --upgrade . || exit 1

# Stop chutney network if it is already running
./chutney stop networks/hs-v3-min || exit 1

# Configure a new network
./chutney configure networks/hs-v3-min || exit 1

# Start the network: first phase
./chutney start networks/hs-v3-min || exit 1

# Start the network: second phase
# This is when the Onion Service node is started
CHUTNEY_LAUNCH_PHASE=2 ./chutney start networks/hs-v3-min || exit 1

# Wait for bootstrap
./chutney wait_for_bootstrap networks/hs-v3-min

# Check the status
./chutney status networks/hs-v3-min

# Retry verify until hidden service subsystem is working
n=0
until [ $n -ge 20 ]; do
  # Get chutney output
  output=$(./chutney verify networks/hs-v3-min)

  # Check if chutney output included 'Transmission: Success'.
  if [[ $output == *"Transmission: Success"* ]]; then
    # Get the Onion Service address
    # This worked with a previous chutney version
    #hs_address=$(echo $output | grep -Po -m 1 "([a-z2-7]{56}.onion:\d{2,5})" | head -n1)

    # Get the Onion Service address
    hs_address=$(echo $output | grep -Po -m 1 "([a-z2-7]{56}.onion)" | head -n1)

    # Get the client address
    client_address=$(echo $output | grep -Po -m 1 "(localhost:\d{2,5})" | head -n1)

    # All good
    if [ ! -z "$hs_address" ]; then
      echo "HS system running with service available at $hs_address"
      echo "Client address is $client_address"
      export CHUTNEY_ONION_ADDRESS="$hs_address"
      export CHUTNEY_CLIENT_PORT="$client_address"
      break
    fi
  fi

  # Still nees to wait
  echo "HS system not running yet. Sleeping 15 seconds"
  n=$[$n+1]
  sleep 15
done

# Go back to the parent folder
cd ..
