from Crypto.Random import get_random_bytes


def create_secret_key(k):
    secret_key = get_random_bytes(k)
    return secret_key
