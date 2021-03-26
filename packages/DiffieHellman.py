import pyDH
key = 0
def keyCreation():
    global key
    p_key = pyDH.DiffieHellman()
    key = p_key.gen_public_key()
    return key

def dhfunc(otherParty_pubkey):
    pubkey = key.gen_public_key()
    sharedkey = key.gen_shared_key(otherParty_pubkey)
    return sharedkey    
