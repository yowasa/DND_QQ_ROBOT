import requests
from PIL import Image
from io import BytesIO
from hoshino import R
from hoshino.config._pcr_duel_data import OLD_CHARA_NAME


def download_chara_icon(id_):
    url = f'https://redive.estertion.win/card/full/{id_}31.webp'
    save_path = R.img(f'test/{id_}31.png').path
    try:
        rsp = requests.get(url, stream=True, timeout=5)
    except Exception as e:
        print(e)

    if 200 == rsp.status_code:
        img = Image.open(BytesIO(rsp.content))
        img.save(save_path)
    else:
        print(f"id为{id_}失败")

for i in OLD_CHARA_NAME.keys():
    download_chara_icon(i)