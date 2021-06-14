import secrets, random, string, hashlib, json


def token_urlsafe(length=64):
    return secrets.token_urlsafe(length)


def token_bytes(length=64):
    return str(secrets.token_bytes(length))


def token_rand(length=64):
    chars = string.ascii_letters + string.digits + string.punctuation
    t = ''.join(random.choice(chars) for i in range(length))
    return t


def create_secret(blck_items={}):
    if type(blck_items) is dict and 'email' in blck_items.keys() and 'username' in blck_items.keys():
        gen = hashlib.blake2b()

        for key, blck in blck_items.items():
            gen.update(blck.encode('utf-8'))

        secret_blck = gen.hexdigest()

        return secret_blck

    return False
