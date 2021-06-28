from PIL import Image

img = Image.open("/Users/yowasa/Documents/Resources/img/abuse.jpg")

size = min(img.size)

cropped = img.crop((0, 0, size, size))  # (left, upper, right, lower)
cropped = cropped.resize((128, 128))
cropped.save("/Users/yowasa/Documents/Resources/img/pil_cut_abuse.png", "PNG")

import hashlib
import requests


def requests_download_url(url, path):
    name = url[url.rfind("/") + 1:]
    hash_name = md5(name) + '.jpg'
    r = requests.get(url, stream=True)
    if r.status_code == 200:
        open(path + hash_name, 'wb').write(r.content)
    return hash_name


def md5(str):
    m = hashlib.md5()
    m.update(str.encode("utf8"))
    print(m.hexdigest())
    return m.hexdigest()
