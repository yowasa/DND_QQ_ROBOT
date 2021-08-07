import json
from . import RES_DIR
import os

# dlc字典
dlcdict = {}
# dlc介绍
dlcintro = {}
# 角色信息
chara_info = {}
# 加载时装列表
fashionlist = {}
# dlc群组开关
dlc_switch = {}


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

def save_dlc_switch():
    with open(os.path.join(RES_DIR,f'duel/dlc_switch.json'), 'w', encoding='UTF-8') as f:
        json.dump(dlc_switch, f, ensure_ascii=False)

def load_dlc_switch():
    global dlc_switch
    with open(os.path.join(RES_DIR,f'duel/dlc_switch.json'), 'r', encoding='UTF-8') as f:
        dlc_switch = json.load(f, strict=False)


# 检查有没有没加到json里的dlc
def check_dlc():
    global dlcdict,dlc_switch
    for dlc in dlcdict.keys():
        if dlc not in dlc_switch.keys():
            dlc_switch[dlc] = []
    save_dlc_switch()