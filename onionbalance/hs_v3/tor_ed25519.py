from stem.util import ed25519

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey, Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization

from onionbalance.hs_v3.ext import ed25519_exts_ref
from onionbalance.hs_v3.ext import slow_ed25519

def load_tor_key_from_disk(key_bytes):
    """
    Load a private identity key from little-t-tor.
    """
    # Verify header
    if (key_bytes[:29] != b'== ed25519v1-secret: type0 =='):
        raise ValueError("Tor key does not start with Tor header")

    expanded_sk = key_bytes[32:]

    # The rest should be 64 bytes (a,h):
    # 32 bytes for secret scalar 'a'
    # 32 bytes for PRF key 'h'
    if (len(expanded_sk) != 64):
        raise ValueError("Tor private key has the wrong length")

    return TorEd25519PrivateKey(expanded_sk)

def _blinded_sign_with_tor_key(msg, identity_key, blinded_key, blinding_nonce):
    """
    This is identical to stem's hidden_service.py:_blinded_sign() but takes an
    extended private key (i.e. in tor format) as its argument, instead of the
    standard format that hazmat does. It basically omits the "extended the key"
    step and does everything else the same.
    """
    identity_key_bytes = identity_key.private_bytes(
        encoding = serialization.Encoding.Raw,
        format = serialization.PrivateFormat.Raw,
        encryption_algorithm = serialization.NoEncryption(),
    )

    # blind the ESK with this nonce
    esk = identity_key_bytes

    mult = 2 ** (ed25519.b - 2) + sum(2 ** i * ed25519.bit(blinding_nonce, i) for i in range(3, ed25519.b - 2))
    s = ed25519.decodeint(esk[:32])
    s_prime = (s * mult) % ed25519.l
    k = esk[32:]
    k_prime = ed25519.H(b'Derive temporary signing key hash input' + k)[:32]
    blinded_esk = ed25519.encodeint(s_prime) + k_prime

    # finally, sign the message

    a = ed25519.decodeint(blinded_esk[:32])
    r = ed25519.Hint(b''.join([blinded_esk[i:i + 1] for i in range(ed25519.b // 8, ed25519.b // 4)]) + msg)
    R = ed25519.scalarmult(ed25519.B, r)
    S = (r + ed25519.Hint(ed25519.encodepoint(R) + blinded_key + msg) * a) % ed25519.l

    return ed25519.encodepoint(R) + ed25519.encodeint(S)

"""
Tor ed25519 keys

Expose classes for ed25519 keys in Tor's extended key format which can mimic
the hazmat ed25519 public/private key classes, so that we can use them
interchangeably in stem.

Tor uses the "extended" (a,h) format for its private keys, whereas hazmat uses
the "standard" (seed,A) format: https://blog.mozilla.org/warner/2011/11/29/ed25519-keys/

Since you can't go from the "extended" format to the "standard" format, we
created these wrappers that act exactly like hazmat keys when it comes to their
interface.
"""


class TorEd25519PrivateKey(object):
    """
    Represents the private part of a blinded ed25519 key of an onion service
    and should expose a public_key() method and a sign() method.
    """
    def __init__(self, expanded_sk):
        self.priv_key = expanded_sk
        self.pub_key_bytes = ed25519_exts_ref.publickeyFromESK(self.priv_key)
        self.pub_key = TorEd25519PublicKey(self.pub_key_bytes)

    def public_key(self):
        return self.pub_key

    def private_bytes(self, encoding=None, format=None, encryption_algorithm=None):
        return self.priv_key

    def sign(self, msg):
        return ed25519_exts_ref.signatureWithESK(msg, self.priv_key, self.pub_key_bytes)

    @property
    def __class__(self):
        """
        This is an epic hack to make this class look like a hazmat ed25519 public
        key in the eyes of stem:
          https://github.com/asn-d6/onionbalance/issues/10#issuecomment-610425916

        The __class_ attribute is what's being used by unittest.mock and the C
        API to trick isinstance() checks, so as long as stem uses isinstance()
        this is gonna work:
          https://docs.python.org/3/library/unittest.mock.html#unittest.mock.Mock.__class__
          https://docs.python.org/3/c-api/object.html#c.PyObject_IsInstance
        """
        return Ed25519PrivateKey

class TorEd25519PublicKey(object):
    """
    Represents the public blinded ed25519 key of an onion service and should
    expose a public_bytes() method and a verify() method.
    """
    def __init__(self, public_key):
        self.public_key = public_key

    def public_bytes(self, encoding=None, format=None):
        return self.public_key

    def verify(self, signature, message):
        """
        raises exception if sig not valid
        """
        slow_ed25519.checkvalid(signature, message, self.public_key)

    @property
    def __class__(self):
        return Ed25519PublicKey
