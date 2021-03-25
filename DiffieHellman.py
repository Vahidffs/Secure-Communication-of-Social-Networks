import pyDH
key = 0
def keyCreation():
    global key
    key = pyDH.DiffieHellman()
    return key

def dhfunc(otherParty_pubkey):
    pubkey = key.gen_public_key()
    sharedkey = key.gen_shared_key(otherParty_pubkey)
    return sharedkey    
