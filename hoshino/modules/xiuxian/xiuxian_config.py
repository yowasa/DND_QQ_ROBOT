from hoshino.util import FreqLimiter
from hoshino import Service, priv
from hoshino.typing import CQEvent
from .ItemCounter import *
from .XiuxianCounter import *

sv = Service('修仙', manage_priv=priv.SUPERUSER, enable_on_default=False, visible=True, bundle='修仙', help_=
'''[#修仙手册] 查询修仙帮助
''')
JingJieMap = {
    "1": '凡人',
    "2": '锻体 1阶',
    "3": '锻体 2阶',
    "4": '锻体 3阶',
    "5": '锻体 4阶',
    "6": '锻体 5阶',
    "7": '炼气 初期',
    "8": '炼气 中期',
    "9": '炼气 后期',
    "10": '筑基 初期',
    "11": '筑基 中期',
    "12": '筑基 后期',
}

EXP_NEED_MAP = {
    "1": 10,
    "2": 50,
    "3": 50,
    "4": 50,
    "5": 50,
    "6": 50,
    "7": 100,
    "8": 100,
    "9": 100,
    "10": 200,
    "11": 200,
    "12": 200,
}

MAP = {
    '新手村': {"max_level": 1, "in_level": 0},
    '大千世界': {"max_level": 9, "in_level": 2},
    '修仙秘境': {"max_level": 12, "in_level": 10},
}

ITEM_CARRY = {
    "1": 1,
    "2": 3,
    "3": 3,
    "4": 3,
    "5": 3,
    "6": 3,
    "7": 5,
    "8": 5,
    "9": 5,
    "10": 7,
    "11": 7,
    "12": 7,
}

# 时间限制
flmt = FreqLimiter(600)

die_flmt = FreqLimiter(3600)

ITEM_INFO = {
    "1": {
        "id": "1",
        "name": "造化丸",
        "type": "丹药",
        "desc": "获取50点经验",
    },
    "2": {
        "id": "2",
        "name": "瞬息万里符",
        "type": "符咒",
        "desc": "被将要被击杀时消耗背包中的此符 躲避一次击杀",
    }
}
ITEM_NAME_MAP = {ITEM_INFO[i]["name"]: ITEM_INFO[i] for i in ITEM_INFO.keys()}


# 根据名字获取道具
def get_item_by_name(name):
    return ITEM_NAME_MAP.get(name)


# 检查是否持有道具
def check_have_item(gid, uid, item):
    i_c = ItemCounter()
    num = i_c._get_item_num(gid, uid, int(item['id']))
    return num


# 添加道具
def add_item(gid, uid, item, num=1):
    i_c = ItemCounter()
    if count_item(gid, uid) >= get_max_count(gid, uid):
        return 0
    i_c._add_item(gid, uid, int(item['id']), num)
    return 1


# 消耗道具
def use_item(gid, uid, item, num=1):
    i_c = ItemCounter()
    i_c._add_item(gid, uid, int(item['id']), num=-num)


# 获取道具总数
def count_item(gid, uid):
    i_c = ItemCounter()
    return i_c._count_item_num(gid, uid)


# 获取角色最大持有物品数量
def get_max_count(gid, uid):
    ct = XiuxianCounter()
    user = ct._get_user(gid, uid)
    max = ITEM_CARRY[str(user.level)]
    return max


# 获取指定用户状态
def get_user_counter(gid, uid, state: UserModel):
    i_c = ItemCounter()
    return i_c._get_user_info(gid, uid, state)


# 存储指定用户状态
def save_user_counter(gid, uid, state: UserModel, num):
    i_c = ItemCounter()
    i_c._save_user_info(gid, uid, state, num)


# 角色死亡
def delete_user(user):
    ct = XiuxianCounter()
    # 删除角色基本信息
    ct._del_user(user.gid, user.uid)
    # 删除角色状态
    for i in UserModel:
        save_user_counter(user.gid, user.uid, i, 0)
    # 删除角色物品
    counter = ItemCounter()
    items = counter._get_item(user.gid, user.uid)
    for i in items:
        item = ITEM_INFO[str(i[0])]
        num = i[1]
        use_item(user.gid, user.uid, item, num)
    # 进入死亡cd
    die_flmt.start_cd(user.uid)
