import os

# Parameters defining Onionbalance behavior

# How long to wait for onionbalance to bootstrap before starting periodic
# events (in seconds)
INITIAL_CALLBACK_DELAY = 45

# Every how often we should be fetching instance descriptors (in seconds)
FETCH_DESCRIPTOR_FREQUENCY = 10 * 60
FETCH_DESCRIPTOR_FREQUENCY_TESTNET = 20

# Every how often we should be checking whether we should publish our frontend
# descriptor (in seconds). Triggering this callback doesn't mean we will
# actually upload a descriptor. We only upload a descriptor if it has expired,
# the intro points have changed, etc.
PUBLISH_DESCRIPTOR_CHECK_FREQUENCY = 5 * 60
PUBLISH_DESCRIPTOR_CHECK_FREQUENCY_TESTNET = 10

# How long should we keep a frontend descriptor before we expire it (in
# seconds)?
FRONTEND_DESCRIPTOR_LIFETIME = 60 * 60
FRONTEND_DESCRIPTOR_LIFETIME_TESTNET = 20

# How many instances should we generally allow?
MAX_INSTANCES = 60

# How many intros should we use from each instance in the frontend
# descriptors?
# [TODO: This makes no attempt to hide the use of onionbalance. In the future we
# should be smarter and sneakier here.]
N_INTROS_PER_INSTANCE = 2

# max number of intro points that a descriptor is allowed to contain
N_INTROS_PER_DESCRIPTOR = 20

# If we last received a descriptor for this instance more than
# INSTANCE_DESCRIPTOR_TOO_OLD seconds ago, consider the instance to be down.
INSTANCE_DESCRIPTOR_TOO_OLD = 60 * 60
INSTANCE_DESCRIPTOR_TOO_OLD_TESTNET = 20

# Parameters defined by HSv3 spec and little-t-tor implementation

# Number of replicas per descriptor
HSDIR_N_REPLICAS = 2

# How many uploads per replica
# [TODO: Get these from the consensus instead of hardcoded]
# default value of HSDIR_SPREAD_FETCH of the client is currently 3 - uploading distinct descriptors to more
# HSDirs than that wouldn't be very effective as they couldn't be fetched
# because of that HSDIR_SPREAD_STORE is set to 3 (instead of 4)
HSDIR_SPREAD_STORE = 3

# number of HSDirs that we can use to upload our descriptor(s)
N_HSDIRS = HSDIR_N_REPLICAS * HSDIR_SPREAD_STORE

# Max descriptor size (in bytes) (see hs_cache_get_max_descriptor_size() in
# little-t-tor)
MAX_DESCRIPTOR_SIZE = 50000

# Misc parameters

DEFAULT_LOG_LEVEL = os.environ.get('ONIONBALANCE_LOG_LEVEL', 'warning')

