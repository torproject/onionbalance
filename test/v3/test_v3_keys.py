import unittest
import binascii

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey

import stem.util
from stem.descriptor.hidden_service import HiddenServiceDescriptorV3

from onionbalance.hs_v3 import tor_ed25519

ONION_ADDR = "4a2zwxetkje5lwvahfv75arzrctn6bznkwmosvfyobmyv2fc3idbpwyd.onion"
PRIVKEY_FILE_HEX = "3d3d206564323535313976312d7365637265743a207479706530203d3d000000a0c632db831865c9562c5eca9446c50d1c6a88d9985e372986c9ae800a7f347a93bd4a97b9b18adf2ad9bceee4d167bf3d61362440066c22719d3cb5d1f97011"

class TestKeys(unittest.TestCase):
    def test_load_tor_privkey(self):
        privkey_bytes = binascii.unhexlify(PRIVKEY_FILE_HEX)
        privkey = tor_ed25519.load_tor_key_from_disk(privkey_bytes)
        pubkey = privkey.public_key()

        # Make sure that the fake instances are right
        self.assertTrue(isinstance(privkey, Ed25519PrivateKey))
        self.assertTrue(isinstance(pubkey, Ed25519PublicKey))

        # Make sure that the public key matches the onion address
        onion_addr_pubkey_bytes = HiddenServiceDescriptorV3.identity_key_from_address(ONION_ADDR)
        self.assertEqual(onion_addr_pubkey_bytes, pubkey.public_bytes())

        # Check that signature verification works
        msg = b"07-04-2020 weird days"
        msg_sig = privkey.sign(msg)
        onion_addr_pubkey = tor_ed25519.TorEd25519PublicKey(onion_addr_pubkey_bytes)
        onion_addr_pubkey.verify(msg_sig, msg)

        # Now check that it won't just verify any message
        self.assertRaises(Exception, onion_addr_pubkey.verify, msg_sig, b"another message another day")

        # Now check that stem will accept this
        self.assertEqual(stem.util._pubkey_bytes(privkey), pubkey.public_bytes())
        self.assertEqual(stem.util._pubkey_bytes(pubkey), pubkey.public_bytes())

        # Now check that blinding can work
        blinded_key_bytes = stem.descriptor.hidden_service._blinded_pubkey(privkey, b"a"*32)
        blinded_key = tor_ed25519.TorEd25519PublicKey(blinded_key_bytes)
        signature = tor_ed25519._blinded_sign_with_tor_key(b"haha", privkey, blinded_key_bytes, b"a"*32)

        blinded_key.verify(signature, b"haha")

if __name__ == '__main__':
    unittest.main()

