import json
from . import RES_DIR
import os
from ._pcr_duel_data import OLD_CHARA_NAME

dlcdict = {}
dlcintro = {}
chara_info = {}

# 加载时装列表
fashionlist = {}

pcr = OLD_CHARA_NAME.keys()
yozilist = range(1523, 1544)
bangdreamlist = range(1601, 1636)
millist = range(3001, 3055)
collelist = range(4001, 4639)
mrfzlist = range(5001, 5180)
blhxlist = range(6000, 6506)
genshinlist = range(7001, 7020)
koilist = range(7100, 7104)
sakulist = range(7200, 7204)
cloverlist = range(7300, 7307)
majsoullist = range(7400, 7476)
noranekolist = range(7500, 7510)
fgolist = range(8001, 8301)

# 这里记录dlc名字和对应列表
dlcdict_origin = {
    'pcr': pcr,
    'blhx': blhxlist,
    'yozi': yozilist,
    'genshin': genshinlist,
    'bangdream': bangdreamlist,
    'million': millist,
    'kancolle': collelist,
    'koikake': koilist,
    'sakukoi': sakulist,
    'cloverdays': cloverlist,
    'majsoul': majsoullist,
    'noraneko': noranekolist,
    'fgo': fgolist,
    'mrfz': mrfzlist
}
# 这里记录每个dlc的介绍
dlcintro_origin = {
    'pcr': '公主链接角色包',
    'blhx': '碧蓝航线手游角色包',
    'yozi': '柚子社部分角色包',
    'genshin': '原神角色包',
    'bangdream': '邦邦手游角色包。',
    'million': '偶像大师百万剧场角色包',
    'kancolle': '舰队collection角色包',
    'koikake': '恋×シンアイ彼女角色包',
    'sakukoi': '桜ひとひら恋もよう角色包',
    'cloverdays': 'Clover Days角色包',
    'majsoul': '雀魂角色包',
    'noraneko': 'ノラと皇女と野良猫ハート角色包',
    'fgo': 'FGO手游角色包',
    'mrfz': '明日方舟手游角色包'
}


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

    dlcdict = {**dlcdict_origin, **ex_dict}
    dlcintro = {**dlcintro_origin, **ex_info}


def refresh_fashion():
    global fashionlist
    with open(os.path.join(RES_DIR, 'duel/fashion_config.json'), 'r', encoding='UTF-8') as fa:
        fashionlist = json.load(fa)


def save_fashion():
    global fashionlist
    with open(os.path.join(RES_DIR, 'duel/fashion_config.json'), 'w', encoding='UTF-8') as f:
        json.dump(fashionlist, fp=f, ensure_ascii=False, indent=4)
