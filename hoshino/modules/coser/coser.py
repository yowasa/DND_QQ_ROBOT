import hashlib
import os
import random

import requests

from hoshino import R
from hoshino import Service
from hoshino.typing import CQEvent


def md5(str):
    m = hashlib.md5()
    m.update(str.encode("utf8"))
    return m.hexdigest()


def download_coser_url(url, path):
    try:
        r = requests.get(url, stream=True, timeout=5)
        if r.status_code == 200:
            hash_name = md5(r.url) + '.jpg'
            open(os.path.join(path, hash_name), 'wb').write(r.content)
            return hash_name
    except:
        return None
    return None


sv = Service('coser', enable_on_default=True, help_=
'''[来张coser]''')

url = "https://api.iyk0.com/cos/"

"coser", "括丝", "COS", "Cos", "cOS", "coS"


@sv.on_fullmatch(["来张coser", "来张COS", "来张cos"])
async def coser(bot, ev: CQEvent):
    path = R.img("ghs/coser").path
    hash_name = download_coser_url(url, path)
    if hash_name:
        await bot.finish(ev, R.img(f"ghs/coser/{hash_name}").cqcode)
    list = os.listdir(path)  # 列出文件夹下所有的目录与文件
    coser = random.choice(list)
    await bot.finish(ev, R.img(f"ghs/coser/{coser}").cqcode)
