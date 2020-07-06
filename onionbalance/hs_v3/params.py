import os

# Parameters definining Onionbalance behavior

# How long to wait for onionbalance to bootstrap before starting periodic
# events (in seconds)
INITIAL_CALLBACK_DELAY = 45

# Every how often we should be fetching instance descriptors (in seconds)
FETCH_DESCRIPTOR_FREQUENCY = 5 * 60
FETCH_DESCRIPTOR_FREQUENCY_TESTNET = 10

# Every how often we should be checking whether we should publish our frontend
# descriptor (in seconds). Triggering this callback doesn't mean we will
# actually upload a descriptor. We only upload a descriptor if it has expired,
# the intro points have changed, etc.
PUBLISH_DESCRIPTOR_CHECK_FREQUENCY = 2 * 60
PUBLISH_DESCRIPTOR_CHECK_FREQUENCY_TESTNET = 5

# How long should we keep a frontend descriptor before we expire it (in
# seconds)?
FRONTEND_DESCRIPTOR_LIFETIME = 30 * 60
FRONTEND_DESCRIPTOR_LIFETIME_TESTNET = 10

# How many intros should we use from each instance in the final frontend
# descriptor?
# [TODO: This makes no attempt to hide the use of onionbalance. In the future we
# should be smarter and sneakier here.]
N_INTROS_PER_INSTANCE = 5

# If we last received a descriptor for this instance more than
# INSTANCE_DESCRIPTOR_TOO_OLD seconds ago, consider the instance to be down.
INSTANCE_DESCRIPTOR_TOO_OLD = 30 * 60
INSTANCE_DESCRIPTOR_TOO_OLD_TESTNET = 10

# Parameters defined by HSv3 spec and little-t-tor implementation

# Number of replicas per descriptor
HSDIR_N_REPLICAS = 2
# How many uploads per replica
# [TODO: Get these from the consensus instead of hardcoded]
HSDIR_SPREAD_STORE = 4

# Max descriptor size (in bytes) (see hs_cache_get_max_descriptor_size() in
# little-t-tor)
MAX_DESCRIPTOR_SIZE = 50000

# Misc parameters

DEFAULT_LOG_LEVEL = os.environ.get('ONIONBALANCE_LOG_LEVEL', 'warning')
