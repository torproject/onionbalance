import os
import unittest
# import mock
from datetime import datetime

import yaml

from onionbalance.hs_v3.manager import status_socket_location
from onionbalance.hs_v3.status import StatusSocketHandlerMixin


class DummyDescriptor(object):
    pass


class DummyInstance(object):
    pass


class DummyService(object):
    def __init__(self):
        self.instances = []


class TestStatus(unittest.TestCase):
    def test_status(self):
        # Mock a fake Tor network
        from onionbalance.hs_v3.onionbalance import my_onionbalance

        time_format = "%Y-%m-%d %H:%M:%S"

        service = DummyService()
        service.onion_address = 'bvy46sg2b5dokczabwv2pabqlrps3lppweyrebhat6gjieo2avojdvad.onion'
        service.first_descriptor = None
        service.second_descriptor = None
        my_onionbalance.services = [service]
        status = StatusSocketHandlerMixin(my_onionbalance)
        self.assertEqual(status._outputString(), '{"services": [{"instances": [], "onionAddress": "bvy46sg2b5dokczabwv2pabqlrps3lppweyrebhat6gjieo2avojdvad.onion", "publishAttemptFirstDescriptor": null, "publishAttemptSecondDescriptor": null}]}')

        service.first_descriptor = DummyDescriptor()
        service.first_descriptor.last_publish_attempt_ts = datetime.strptime('2020-06-16 20:00:12', time_format)
        service.first_descriptor.last_upload_ts = datetime.strptime('2020-06-16 20:00:13', time_format)
        service.second_descriptor = DummyDescriptor()
        service.second_descriptor.last_publish_attempt_ts = datetime.strptime('2020-06-16 20:00:14', time_format)
        service.second_descriptor.last_upload_ts = datetime.strptime('2020-06-16 20:00:15', time_format)
        self.assertEqual(status._outputString(), '{"services": [{"instances": [], "onionAddress": "bvy46sg2b5dokczabwv2pabqlrps3lppweyrebhat6gjieo2avojdvad.onion", "publishAttemptFirstDescriptor": "2020-06-16 20:00:12", "publishAttemptSecondDescriptor": "2020-06-16 20:00:14"}]}')

        service.first_descriptor = None
        service.second_descriptor = None
        instance1 = DummyInstance()
        instance1.onion_address = 'vkmiy6biqcyphtx5exswxl5sjus2vn2b6pzir7lz5akudhwbqk5muead'
        instance1.intro_set_modified_timestamp = datetime.strptime('2020-06-16 21:00:12', time_format)
        instance1.descriptor = DummyDescriptor()
        instance1.descriptor.received_ts = datetime.strptime('2020-06-11 20:00:10', time_format)
        instance1.descriptor.intro_set = ['127.0.0.1', '127.0.0.2']
        instance2 = DummyInstance()
        instance2.onion_address = 'jhkhjkhdgjkhdfjkhgfjkhgkjdhgjkfdhgjkfdhhdfgjfhdgkjfhkd88'
        instance2.intro_set_modified_timestamp = None
        instance2.descriptor = DummyDescriptor()
        instance2.descriptor.received_ts = datetime.strptime('2020-07-11 20:00:10', time_format)
        instance2.descriptor.intro_set = ['127.0.0.1', '127.0.0.2']
        service.instances = [instance1, instance2]
        self.assertEqual(status._outputString(), '{"services": [{"instances": [{"descriptorReceived": "2020-06-11 20:00:10", "introPointsNum": 2, "introSetModified": "2020-06-16 21:00:12", "onionAddress": "vkmiy6biqcyphtx5exswxl5sjus2vn2b6pzir7lz5akudhwbqk5muead.onion"}, {"onionAddress": "jhkhjkhdgjkhdfjkhgfjkhgkjdhgjkfdhgjkfdhhdfgjfhdgkjfhkd88.onion", "received": "2020-07-11 20:00:10"}], "onionAddress": "bvy46sg2b5dokczabwv2pabqlrps3lppweyrebhat6gjieo2avojdvad.onion", "publishAttemptFirstDescriptor": null, "publishAttemptSecondDescriptor": null}]}')


class TestStatusSocketLocation(unittest.TestCase):
    def test_location(self):
        try:
            del os.environ['ONIONBALANCE_STATUS_SOCKET_LOCATION']
        except KeyError:
            pass
        config_data = yaml.safe_load("dummy: x")
        self.assertEqual(status_socket_location(config_data), None)
        config_data = yaml.safe_load("status-socket-location: /home/user/test.sock")
        self.assertEqual(status_socket_location(config_data), '/home/user/test.sock')
        os.environ['ONIONBALANCE_STATUS_SOCKET_LOCATION'] = '/home/user/test2.sock'
        self.assertEqual(status_socket_location(config_data), '/home/user/test2.sock')


if __name__ == '__main__':
    unittest.main()
