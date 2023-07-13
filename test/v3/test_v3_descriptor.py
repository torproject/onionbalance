import unittest

from onionbalance.hs_v3 import consensus

def test_disaster_srv():
    """
    Test that disaster SRV creation is correct based on little-t-tor's
    unittests as test vectors (in particular see test_disaster_srv())
    """
    my_consensus = consensus.Consensus(do_refresh_consensus=False)

    # Correct disaster SRV for TPs: 1, 2, 3, 4, 5
    correct_srvs = [ "F8A4948707653837FA44ABB5BBC75A12F6F101E7F8FAF699B9715F4965D3507D",
                     "C17966DF8B4834638E1B7BF38944C4995B92E89749D1623E417A44938D08FD67",
                     "A3BAB4327F9C2F8B30A126DAD3ABCCE12DD813169A5D924244B57987AEE413C2",
                     "C79ABE7116FCF7810F7A5C76198B97339990C738B456EFDBC1399189927BADEC",
                     "941D5FE4289FBF2F853766EAC4B948B51C81A4137A44516342ABC80518E0183D"]

    for i in range(1,6):
        disaster_srv = my_consensus._get_disaster_srv(i)
        assert(disaster_srv.hex().upper() == correct_srvs[i-1])

if __name__ == '__main__':
    unittest.main()
