import secrets, random, string, hashlib, json


def token_urlsafe(length=64):
    return secrets.token_urlsafe(length)


def token_bytes(length=64):
    return str(secrets.token_bytes(length))


def token_rand(length=64):
    chars = string.ascii_letters + string.digits + string.punctuation
    t = ''.join(random.choice(chars) for i in range(length))
    return t


def token_core(data_pass={}):
    secret = create_secret(data_pass)
    return secret


def create_secret(data_pass={}):

    if type(data_pass) is dict and 'email' in data_pass.keys() and 'username' in data_pass.keys():
        gen = hashlib.blake2b()
        blck_items = data_pass
        blck_items['pwd'] = token_rand()

        for key, blck in blck_items.items():
            gen.update(blck.encode('utf-8'))

        secret_blck = gen.hexdigest()
        blck_items['secret'] = secret_blck
        secret_content = json.dumps(blck_items)

        return secret_content

    return False