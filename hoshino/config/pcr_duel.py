import json
from . import RES_DIR
import os

dlcdict = {}
dlcintro = {}
chara_info = {}

# 加载时装列表
fashionlist = {}



def refresh_chara():
    global chara_info
    with open(os.path.join(RES_DIR, 'duel/chara.json'), 'r', encoding='UTF-8') as f:
        chara_info = json.load(f)


def refresh_config():
    global dlcdict, dlcintro
    with open(os.path.join(RES_DIR, 'duel/dlc_config.json'), 'r', encoding='UTF-8') as f:
        ex_dlc_info = json.load(f)
    ex_info = {}
    ex_dict = {}
    for k, item in ex_dlc_info.items():
        ex_info[item['code']] = item['desc']
        ex_chara_ids = [int(id) for id in chara_info.keys() if item['index'] <= int(id) <= item['to']]
        ex_dict[item['code']] = ex_chara_ids
    dlcdict = {**ex_dict}
    dlcintro = {**ex_info}


def refresh_fashion():
    global fashionlist
    with open(os.path.join(RES_DIR, 'duel/fashion_config.json'), 'r', encoding='UTF-8') as fa:
        fashionlist = json.load(fa)


def save_fashion():
    global fashionlist
    with open(os.path.join(RES_DIR, 'duel/fashion_config.json'), 'w', encoding='UTF-8') as f:
        json.dump(fashionlist, fp=f, ensure_ascii=False, indent=4)
