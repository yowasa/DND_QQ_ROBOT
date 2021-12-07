from hoshino.util import FreqLimiter
from hoshino import Service, priv
from hoshino.typing import CQEvent
from .ItemCounter import *
from .XiuxianCounter import *
from hoshino import util
import random
import json

sv = Service('修仙', manage_priv=priv.SUPERUSER, enable_on_default=False, visible=True, bundle='修仙', help_=
'''[#修仙手册] 查询修仙帮助
''')
# 境界列表
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
    "13": '结丹 初期',
    "14": '结丹 中期',
    "15": '结丹 后期',
    "16": '金丹 初期',
    "17": '金丹 中期',
    "18": '金丹 后期',
    "19": '元婴 初期',
    "20": '元婴 中期',
    "21": '元婴 后期',
    "22": '化神 初期',
    "23": '化神 中期',
    "24": '化神 后期',
    "25": '洞虚 初期',
    "26": '洞虚 中期',
    "27": '洞虚 后期',
    "28": '大乘 初期',
    "29": '大乘 中期',
    "30": '大乘 后期',
    "31": '渡劫期',
    "32": '天仙 初期',
    "33": '天仙 中期',
    "34": '天仙 后期',
    "35": '真仙 初期',
    "36": '真仙 中期',
    "37": '真仙 后期',
    "38": '金仙 初期',
    "39": '金仙 中期',
    "40": '金仙 后期',
}
# 境界所需经验
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
    "13": 400,
    "14": 400,
    "15": 400,
    "16": 800,
    "17": 800,
    "18": 800,
    "19": 1600,
    "20": 1600,
    "21": 1600,
    "22": 3200,
    "23": 3200,
    "24": 3200,
    "25": 5000,
    "26": 5000,
    "27": 5000,
    "28": 10000,
    "29": 10000,
    "30": 10000,
    "31": 0,
    "32": 50000,
    "33": 50000,
    "34": 50000,
    "35": 100000,
    "36": 100000,
    "37": 100000,
    "38": 1000000,
    "39": 1000000,
    "40": 1000000,
}
# 地图
MAP = {
    '新手村': {"max_level": 1, "in_level": 0, "lingqi_max": 10, "lingqi_min": 10},
    '大千世界': {"max_level": 9, "in_level": 2, "lingqi_max": 50, "lingqi_min": 30},
    '修仙秘境': {"max_level": 12, "in_level": 7, "lingqi_max": 100, "lingqi_min": 50},
    '秘境迷踪': {"max_level": 15, "in_level": 10, "lingqi_max": 120, "lingqi_min": 70},
    '苍穹神州': {"max_level": 18, "in_level": 13, "lingqi_max": 150, "lingqi_min": 100},
    '九天十国': {"max_level": 21, "in_level": 16, "lingqi_max": 200, "lingqi_min": 150},
    '洪荒大陆': {"max_level": 24, "in_level": 19, "lingqi_max": 260, "lingqi_min": 200},
    '诸天万界': {"max_level": 27, "in_level": 22, "lingqi_max": 320, "lingqi_min": 280},
    '灵寰福址': {"max_level": 30, "in_level": 25, "lingqi_max": 400, "lingqi_min": 350},
    '混沌绝地': {"max_level": 31, "in_level": 30, "lingqi_max": 500, "lingqi_min": 500},
    '荧惑仙境': {"max_level": 40, "in_level": 10, "lingqi_max": 1000, "lingqi_min": 1000},
}
# 境界所能拥有的道具上限
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
    "13": 9,
    "14": 9,
    "15": 9,
    "16": 10,
    "17": 10,
    "18": 10,
    "19": 10,
    "20": 10,
    "21": 10,
    "22": 10,
    "23": 10,
    "24": 10,
    "25": 15,
    "26": 15,
    "27": 15,
    "28": 15,
    "29": 15,
    "30": 15,
    "31": 15,
    "32": 20,
    "33": 20,
    "34": 20,
    "35": 20,
    "36": 20,
    "37": 20,
    "38": 20,
    "39": 20,
    "40": 20,
}
# 瓶颈
PINGJING = [1, 6, 9, 12, 15, 18, 21, 24, 27, 30, 31, 34, 37]
# 修炼效率
XIULIAN_SPEED = [100, 70, 50, 40, 30]

# 时间限制
# 操作间隔
flmt = FreqLimiter(10*60)
# 死亡cd
die_flmt = FreqLimiter(1*60*60)

# 测试服
# flmt = FreqLimiter(1)
# die_flmt = FreqLimiter(10)

# 文件路径
FILE_PATH = os.path.dirname(__file__)

# 物品列表
with open(os.path.join(FILE_PATH, 'config/item_info.json'), 'r', encoding='UTF-8') as fa:
    ITEM_INFO = json.load(fa, strict=False)
ITEM_NAME_MAP = {ITEM_INFO[i]["name"]: ITEM_INFO[i] for i in ITEM_INFO.keys()}

# 物品列表
with open(os.path.join(FILE_PATH, 'config/equipment.json'), 'r', encoding='UTF-8') as fa:
    EQUIPMENT_INFO = json.load(fa, strict=False)

# 功法列表
with open(os.path.join(FILE_PATH, 'config/gongfa.json'), 'r', encoding='UTF-8') as fa:
    GONGFA_INFO = json.load(fa, strict=False)

# 法宝列表
with open(os.path.join(FILE_PATH, 'config/fabao.json'), 'r', encoding='UTF-8') as fa:
    FABAO_INFO = json.load(fa, strict=False)


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
    if user.gongfa3 == "袖里乾坤":
        max = 2 * max
    return max


def get_max_count_by_level(level):
    max = ITEM_CARRY[str(level)]
    return max


# 获取指定用户状态
def get_user_counter(gid, uid, state: UserModel):
    i_c = ItemCounter()
    return i_c._get_user_info(gid, uid, state)


# 获取全部用户状态
def get_all_user_flag(gid, uid):
    i_c = ItemCounter()
    li = i_c._query_user_info(gid, uid)
    map = {i[0]: i[1] for i in li}
    result_map = {}
    for i in UserModel:
        result_map[i] = 0
        if map.get(i.value[0]):
            result_map[i] = map.get(i.value[0])
    return result_map


# 存储指定用户状态
def save_user_counter(gid, uid, state: UserModel, num):
    i_c = ItemCounter()
    i_c._save_user_info(gid, uid, state, num)


# 指定用户状态+1
def add_user_counter(gid, uid, state: UserModel, num=1):
    i_c = ItemCounter()
    base = i_c._get_user_info(gid, uid, state)
    i_c._save_user_info(gid, uid, state, base + num)


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


class AllUserInfo():
    def __init__(self, user):
        self.gid = user.gid
        self.uid = user.uid
        self.name = user.name
        self.linggen = user.linggen
        self.exp = user.exp
        self.level = user.level
        self.belong = user.belong
        self.map = user.map
        self.gongfa = user.gongfa  # 心法
        self.fabao = user.fabao
        self.wuqi = user.wuqi
        self.wuxing = user.wuxing
        self.lingli = user.lingli
        self.daohang = user.daohang
        self.act = user.act
        self.defen = user.defen
        self.defen2 = user.defen2
        self.hp = user.hp
        self.mp = user.mp
        self.skill = user.skill
        self.tizhi = user.tizhi
        self.act2 = user.act2
        self.gongfa2 = user.gongfa2  # 功法
        self.gongfa3 = user.gongfa3  # 神通
        # 处理战斗数据
        self.duel_battle_info()
        # 处理其他数据
        self.other_info()

    def duel_battle_info(self):  # 标签库
        # 基础属性
        self.battle_hp = self.hp
        self.battle_mp = self.mp
        # 物理攻击力
        self.battle_atk1 = self.act
        # 术法攻击力
        self.battle_atk2 = self.act2
        # 物理攻击力
        self.battle_defen1 = self.defen
        # 术法攻击力
        self.battle_defen2 = self.defen2
        #
        self.battle_boost = 0
        self.battle_double = 0
        self.battle_dodge = 0

        num = len(self.linggen)
        buff_rate = 1 + (50 / num) / 100
        low_buff_rate = 1 + ((50 / num) * 0.7) / 100

        # 灵根加成
        if '金' in self.linggen:
            self.battle_atk1 = int(self.battle_atk1 * low_buff_rate)
        if '木' in self.linggen:
            self.battle_hp = int(self.battle_hp * buff_rate)
        if '水' in self.linggen:
            self.battle_mp = int(self.battle_mp * buff_rate)
        if '火' in self.linggen:
            self.battle_atk2 = int(self.battle_atk2 * low_buff_rate)
        if '土' in self.linggen:
            self.battle_defen1 = int(self.battle_defen1 * buff_rate)
            self.battle_defen2 = int(self.battle_defen2 * buff_rate)
        # 武器加成
        wuqi = get_equip_by_name(self.wuqi)
        if wuqi:
            buff = wuqi['buff']
            if buff.get('atk1'):
                self.battle_atk1 += buff.get('atk1')
            if buff.get('atk2'):
                self.battle_atk2 += buff.get('atk2')
            if buff.get('hp'):
                self.battle_hp += buff.get('hp')
            if buff.get('mp'):
                self.battle_mp += buff.get('mp')
            if buff.get('defen1'):
                self.battle_defen1 += buff.get('defen1')
            if buff.get('defen2'):
                self.battle_defen2 += buff.get('defen2')
            if buff.get('boost'):
                self.battle_boost += buff.get('boost')
            if buff.get('double'):
                self.battle_double += buff.get('double')
            if buff.get('dodge'):
                self.battle_dodge += buff.get('dodge')
            content = {"daohang": self.daohang, "atk1": self.battle_atk1, "atk2": self.battle_atk2}
            if buff.get('atk1_exec'):
                self.battle_atk1 = int(eval(buff.get('atk1_exec'), content))
            if buff.get('atk2_exec'):
                self.battle_atk2 = int(eval(buff.get('atk2_exec'), content))

    def other_info(self):
        flags = get_all_user_flag(self.gid, self.uid)
        self.flags = flags
        # 伤势
        self.shangshi = flags.get(UserModel.SHANGSHI)
        shangshi_li = ["无", "轻伤", "重伤", "濒死"]
        # 伤势描述
        self.shangshi_desc = shangshi_li[self.shangshi]
        # 持有道具数
        self.have_item_count = count_item(self.gid, self.uid)
        # 最大持有道具数
        self.max_item_count = get_max_count_by_level(self.level)
        # 灵石
        self.lingshi = flags.get(UserModel.LINGSHI)
        # 杀人数量
        self.sharen = flags.get(UserModel.KILL)

    async def check_and_start_cd(self, bot, ev):
        await self.check_cd(bot, ev)
        self.start_cd()

    async def check_cd(self, bot, ev):
        if self.shangshi >= 2:
            await bot.finish(ev, "你伤势过重，只能修养！")
        await self.check_cd_ignore_other(bot, ev)

    async def check_cd_ignore_other(self, bot, ev):
        if not flmt.check(self.uid):
            self.daohang -= 1
            if self.daohang < 0:
                delete_user(self)
                await bot.finish(ev, f"道心不稳，爆体而亡!", at_sender=True)
            ct = XiuxianCounter()
            ct._save_user_info(self)
            await util.silence(ev, 10 * 60, skip_su=False)
            await bot.finish(ev, f"做事急躁，有损道心，道行-1，距离下次操作还需要{round(int(flmt.left_time(self.uid)))}秒")

    def start_cd(self):
        if self.gongfa3 == "大罗洞观":
            if random.randint(1, 20) > 1:
                flmt.start_cd(self.uid)
        else:
            flmt.start_cd(self.uid)


def get_full_user(gid, uid):
    ct = XiuxianCounter()
    user = ct._get_user(gid, uid)
    if not user:
        return None
    return AllUserInfo(user)


async def get_ev_user(bot, ev):
    gid = ev.group_id
    uid = ev.user_id
    user = get_full_user(gid, uid)
    if not user:
        await bot.finish(ev, "江湖上还没有过您的传说，请先注册账号")
    return user


# 随机获得灵根
def get_LingGen():
    ran = random.randint(1, 100)
    li = [5, 25, 40, 25, 5]
    len = 0
    sum = 0
    for i in range(5):
        sum = sum + li[i]
        if ran <= sum:
            len += 1
    linggen = ['金', '木', '水', '火', '土']
    lg = random.sample(linggen, len)
    str_lg = ''.join(lg)
    return str_lg


# 获取装备
def get_equip_by_name(name):
    return EQUIPMENT_INFO.get(name)


# 获取功法
def get_gongfa_by_name(name):
    return GONGFA_INFO.get(name)


# 获取法宝
def get_fabao_by_name(name):
    return FABAO_INFO.get(name)
