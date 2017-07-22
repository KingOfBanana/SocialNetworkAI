from hashlib import md5
def md5Encode(str):
    m = md5()
    m.update(str.encode('utf8'))
    return m.hexdigest()