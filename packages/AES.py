from Crypto.Cipher import AES
# Encryption
def AES_Key_Creator(key):
    print("node 3 ",key)
    cipher = AES.new(key,AES.MODE_EAX)
    return cipher
def AES_encrypt(cipher_obj,unencrypted_data):
    nonce = cipher_obj.nonce
    ciphertext, MAC = cipher_obj.encrypt_and_digest(unencrypted_data)
    return ciphertext, MAC , nonce
# Decryption
def decryptfunc(key,cipher_text,nonce,tag):

    cipher_suite = AES.new(key, AES.MODE_EAX, nonce=nonce)
    plain_text = cipher_suite.decrypt(cipher_text)
    try:
        cipher_suite.verify(tag)
        print("The message is authentic:", plain_text)
    except ValueError:
        print("Key incorrect or message corrupted")
    return plain_text
