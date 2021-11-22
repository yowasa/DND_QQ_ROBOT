import os
import hashlib
import requests


def md5(str):
    m = hashlib.md5()
    m.update(str.encode("utf8"))
    return m.hexdigest()

def download_coser_url(url, path):
    r = requests.get(url, stream=True)
    if r.status_code == 200:
        hash_name = md5(r.url) + '.jpg'
        open(os.path.join(path, hash_name), 'wb').write(r.content)
        return hash_name
    return None


url = "https://api.iyk0.com/cos/"
download_coser_url(url,"/Users/yowasa/Documents/content/Resources/img/ghs/coser")
