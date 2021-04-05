import pyDHE
def keyCreation():
    p_key = pyDHE.new()
    key = p_key.gen_public_key()
    return key

def dhfunc(otherParty_pubkey):
    pubkey = key.gen_public_key()
    sharedkey = key.gen_shared_key(otherParty_pubkey)
    return sharedkey    
