# use xor for bytes
def bxor(b1, b2):
    # if one byte input is empty, convert it into zeroes
    if not b1 and b2:
        b1 = bytes(len(b2))
    if not b2 and b1:
        b2 = bytes(len(b1))
    # if byte inputs of unequal length pad with zeroes
    if len(b1) < len(b2):
        len_diff = len(b2) - len(b1)
        b1 = bytes(len_diff) + b1
    elif len(b2) < len(b1):
        len_diff = len(b1) - len(b2)
        b2 = bytes(len_diff) + b2

    print("b1: {0}, b2: {1}".format(b1, b2))
    result = bytearray()
    for b1, b2 in zip(b1, b2):
        result.append(b1 ^ b2)
    print("result of xor: {0}\n".format(bytes(result)))
    return bytes(result)


def calculate_secret_key(secret_keys_list, secret_key):
    calculated_key = bytes(0)

    for key in secret_keys_list:
        if not calculated_key:
            calculated_key = key
        else:
            calculated_key = bxor(calculated_key, key)

    calculated_key = bxor(calculated_key, secret_key)
    return calculated_key
