from stem.control import Controller
from onionbalance.hs_v3 import descriptor


def test_comparing_descriptors():
    with Controller.from_port(port=5053) as controller:
        controller.authenticate()

        # get hidden service descriptor of a regular onion service
        desc_regular = controller.get_hidden_service_descriptor('fzleuxt5okkdxn7ywujxllx3udod6pewolfofyghfrbpaj2a6vrpzeyd')
        onion_address_regular = 'fzleuxt5okkdxn7ywujxllx3udod6pewolfofyghfrbpaj2a6vrpzeyd.onion'

        # needed for underlying functions to decrypt the descriptor
        descriptor_text_regular = str(desc_regular).encode('utf-8')

        # call underlying functions used in Onionbalance to decrypt the outer and inner layer of the descriptor of a backend instance
        regular_descriptor = descriptor.ReceivedDescriptor(descriptor_text_regular, onion_address_regular)

        # do the same for the Frontend-Service
        desc_ob = controller.get_hidden_service_descriptor('ap3tj5pxmnntonm236pdixktik2ut6cxxeodbxumgel4wodb5kh442ad')
        onion_address_ob = 'ap3tj5pxmnntonm236pdixktik2ut6cxxeodbxumgel4wodb5kh442ad.onion'
        descriptor_text_ob = str(desc_ob).encode('utf-8')
        ob_descriptor = descriptor.ReceivedDescriptor(descriptor_text_ob, onion_address_ob)



