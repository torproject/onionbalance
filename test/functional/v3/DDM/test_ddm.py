import pickle
import random
import string

import mock
import unittest
from onionbalance.hs_v3 import descriptor, params
from onionbalance.hs_v3.onionbalance import logger
from onionbalance.hs_v3.service import OnionbalanceService, BadServiceInit
from test.functional.util import random_onionv3_address, create_test_config_file_v3


def get_random_string(length):
    # random string generator
    seq = string.printable
    result_str = ''.join(random.choice(seq) for i in range(length))
    return result_str


# ------ Dummy-classes do not represent actual implementation and are only used for simplified testing. -------

class DummyIntroPoint(object):
    # dummy class for testing, fill with fake intro point data
    identifier = get_random_string(16)


class DummyHSdir(object):
    # dummy class for testing, fill with fake hsdir data
    hex_fingerprint = get_random_string(16)


class DummyDescriptor(object):
    # dummy class for testing, fill with fake descriptor data
    intro_points = None
    signing_key = get_random_string(16)
    inner_layer = "nnDtg7N8kRekv6dw32dRhCheNIBxCEo6JbVci"
    revision_counter = 1346
    responsible_hsdirs = None

    def set_responsible_hsdirs(self, responsible_hsdirs):
        self.responsible_hsdirs = responsible_hsdirs


class TestDDMService(unittest.TestCase):
    # fill service with fake intro points, responsible hsdirs and descriptors
    # deviating from actual implementation for testing purposes
    intro_points = []
    responsible_hsdirs = []
    descriptors = []

    # create intro points
    i = 0
    while i < 80:
        intro_point = DummyIntroPoint()
        intro_points.append(intro_point)
        i += 1

    # create hsdirs
    j = 0
    while j < 6:
        hsdir = DummyHSdir()
        responsible_hsdirs.append(hsdir)
        j += 1
    z = 0

    # create subdescriptors
    while z < 10:
        desc = DummyDescriptor()
        descriptors.append(desc)
        z += 1

    # fill service with fake descriptor data (mimic the first descriptor in descriptor-list)
    blinding_param = "3434343434343434343434343434343434343434"
    is_first_desc = True
    onion_address = 'bvy46sg2b5dokczabwv2pabqlrps3lppweyrebhat6gjieo2avojdvad.onion'

    @mock.patch('onionbalance.hs_v3.service.OnionbalanceService')
    def test_calculate_space(self, mock_OnionbalanceService):
        """
        test calculation of available space per descriptor, test with actual implementation
        """
        empty_desc = [
        "D1D1D1D1D1D1D1D1D1D1D1D1D1D1D1D1D1D1D1D1",
        "2F2F2F2F2F2F2F2F2F2F2F2F2F2F2F2F2F2F2F2F",
        "B0B0B0B0B0B0B0B0B0B0B0B0B0B0B0B0B0B0B0B0",
        "3A3A3A3A3A3A3A3A3A3A3A3A3A3A3A3A3A3A3A3A",
        "5A5A5A5A5A5A5A5A5A5A5A5A5A5A5A5A5A5A5A5A",
        "DFDFDFDFDFDFDFDFDFDFDFDFDFDFDFDFDFDFDFDF",
        "F7F7F7F7F7F7F7F7F7F7F7F7F7F7F7F7F7F7F7F7",
        "3434343434343434343434343434343434343434" ]
        available_space = OnionbalanceService._calculate_space(mock_OnionbalanceService, empty_desc)
        print(available_space)

        try:
            assert available_space == params.MAX_DESCRIPTOR_SIZE - len(pickle.dumps(empty_desc))
        except AssertionError:
            raise

    @mock.patch('onionbalance.hs_v3.service.OnionbalanceService')
    def test_calculate_desc(self, mock_OnionbalanceService):
        """
        test calculation of number of needed descriptors, test with actual implementation
        """
        available_space = 200
        num_descriptors = OnionbalanceService._calculate_needed_desc(mock_OnionbalanceService, self.intro_points,
                                                                     available_space)
        try:
            assert ((num_descriptors * available_space > len(pickle.dumps(self.intro_points))) and
                    (len(self.intro_points) <= params.N_INTROS_PER_DESCRIPTOR * num_descriptors))
        except AssertionError:
            raise

    def test_create_desc(self):
        """
        test creation of needed descriptors
        slightly deviating from actual implementation for testing purposes
        """
        ddm = True
        descriptors = []
        available_intro_points = self.intro_points.copy()
        num_descriptors = len(self.descriptors)

        # will contain intro points for every descriptor
        assigned_intro_points = []

        # this step is needed to access assigned intro points via index
        for i in range(num_descriptors):
            assigned_intro_points.append([0])

        # determine which intro point belongs to which descriptor
        i = 0
        while len(available_intro_points) > 0:
            assigned_intro_points[i].append(available_intro_points[0])
            available_intro_points.pop(0)
            if i + 1 == num_descriptors:
                i = 0
            else:
                i += 1
        print("Assigned all intro points.")

        for i in range(num_descriptors):
            # remove unnecessary first element (0)
            assigned_intro_points[i].pop(0)
            try:
                # create descriptor with assigned intro points
                desc = "%s %s %s %s" % (self.onion_address, self.blinding_param,
                                        assigned_intro_points[i], self.is_first_desc)
                descriptors.append(desc)
            except descriptor.BadDescriptor:
                return

            # size of pickle is a little larger, keeping it for safety reasons so that our descriptors don't get to big
            print(len(pickle.dumps(desc)))
            print(len(str(desc)))

            if ddm:
                print(
                    "Service %s created %s descriptor of subdescriptor %d (%s intro points) (blinding param: %s) "
                    "(size: %s bytes). About to publish:",
                    self.onion_address, "first" if self.is_first_desc else "second", i + 1,
                    len(assigned_intro_points[i]), self.blinding_param, len(str(desc)))
            else:
                print(
                    "Service %s created %s descriptor (%s intro points) (blinding param: %s) "
                    "(size: %s bytes). About to publish:",
                    self.onion_address, "first" if self.is_first_desc else "second",
                    len(assigned_intro_points[i]), self.blinding_param, len(str(desc)))
        try:
            assert (len(descriptors) == num_descriptors and
                    len(pickle.dumps(descriptors[i])) < params.MAX_DESCRIPTOR_SIZE)
        except AssertionError:
            raise


    @mock.patch('onionbalance.hs_v3.service.OnionbalanceService')
    def test_failsafe_param(self, mock_OnionbalanceService):
        """
        test functionality of added log message, test with actual implementation
        default (params.py): HSDIR_N_REPLICAS = 2, HSDIR_SPREAD_STORE = 3
        """
        num_descriptors_a = 1
        num_descriptors_b = 3
        num_descriptors_c = 4
        num_descriptors_d = 8
        failsafe_param_a = OnionbalanceService._load_failsafe_param(mock_OnionbalanceService,
                                                                    num_descriptors=num_descriptors_a)
        failsafe_param_b = OnionbalanceService._load_failsafe_param(mock_OnionbalanceService,
                                                                    num_descriptors=num_descriptors_b)
        failsafe_param_c = OnionbalanceService._load_failsafe_param(mock_OnionbalanceService,
                                                                    num_descriptors=num_descriptors_c)

        try:
            assert failsafe_param_a and failsafe_param_b and not failsafe_param_c
        except AssertionError:
            raise

        try:
            assert failsafe_param_a and failsafe_param_b and not failsafe_param_c
        except AssertionError:
            raise

        self.assertRaises(BadServiceInit, OnionbalanceService._load_failsafe_param, mock_OnionbalanceService,
                     num_descriptors=num_descriptors_d)

    def test_assign_hsdirs(self):
        """
        test assignment of hsdir to our descriptor(s)
        slightly deviating from actual implementation for testing purposes
        """
        available_hsdirs = self.responsible_hsdirs.copy()
        # will contain hsdirs for resp. descriptor
        assigned_hsdirs = []
        num_descriptors = 3

        # this step is needed to access assigned intro points via index
        for i in range(num_descriptors):
            assigned_hsdirs.append([0])

        # determine which hsdir belong to which descriptor
        i = 0
        while len(available_hsdirs) > 0:
            assigned_hsdirs[i].append(available_hsdirs[0])
            available_hsdirs.pop(0)
            logger.info("Assigned hsdir to (sub)descriptor %d.", i + 1)
            if i+1 == num_descriptors:
                i = 0
            else:
                i += 1

        if len(available_hsdirs) == 0:
            logger.info("Assigned all hsdirs.")

        if len(available_hsdirs) > 0:
            logger.info("Couldn't assign %d hsdirs (this should never happen). Continue anyway.",
                        len(available_hsdirs))

        for i in range(num_descriptors):
            # remove unnecessary first element (0)
            assigned_hsdirs[i].pop(0)
            print(assigned_hsdirs[i])
            try:
                # assign hsdirs to resp. descriptor
                self.descriptors[i].set_responsible_hsdirs(assigned_hsdirs[i])
            except AssertionError:
                raise

    def test_too_may_instances(self, num_instances = params.MAX_INSTANCES+10):
        """
        test functionality of added log message
        """
        list_instances = []
        i = 0
        while i < num_instances:
            list_instances.append(random_onionv3_address())
            i += 1

        with self.assertRaises(SystemExit):
            self.assertRaises(logger.error, create_test_config_file_v3(tmppath="/home/laura/Documents/test/empty",
                                                                  instance_address=list_instances,
                                                                  num_instances=num_instances))