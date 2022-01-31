from hoshino.util import FreqLimiter
from .ItemCounter import *
from .HistoryCounter import *
from .XiuxianCounter import *
from hoshino import util
import random
import json

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
# 俸禄
FENGLU_MAP = {
    "1": 10,
    "2": 20,
    "3": 20,
    "4": 20,
    "5": 20,
    "6": 20,
    "7": 50,
    "8": 50,
    "9": 50,
    "10": 70,
    "11": 70,
    "12": 70,
    "13": 100,
    "14": 100,
    "15": 100,
    "16": 150,
    "17": 150,
    "18": 150,
    "19": 200,
    "20": 200,
    "21": 200,
    "22": 300,
    "23": 300,
    "24": 300,
    "25": 500,
    "26": 500,
    "27": 500,
    "28": 500,
    "29": 500,
    "30": 500,
    "31": 500,
    "32": 800,
    "33": 800,
    "34": 800,
    "35": 800,
    "36": 800,
    "37": 800,
    "38": 800,
    "39": 800,
    "40": 800,
}
# 地图
MAP = {
    '新手村': {"max_level": 1, "in_level": 0, "lingqi_max": 10, "lingqi_min": 10, "able": ['大千世界']},
    '大千世界': {"max_level": 9, "in_level": 2, "lingqi_max": 50, "lingqi_min": 30,
             "able": ['新手村', '修仙秘境', '苍穹神州', '狮府', '百炼山庄']},
    '狮府': {"max_level": 40, "in_level": 2, "lingqi_max": 50, "lingqi_min": 30, "able": ['大千世界']},
    '百炼山庄': {"max_level": 40, "in_level": 2, "lingqi_max": 50, "lingqi_min": 30, "able": ['大千世界']},
    '修仙秘境': {"max_level": 12, "in_level": 7, "lingqi_max": 100, "lingqi_min": 50,
             "able": ['大千世界', '灵寰福址', '无尽之海', '混元门', '蜀山派']},
    '混元门': {"max_level": 40, "in_level": 7, "lingqi_max": 100, "lingqi_min": 50, "able": ["修仙秘境"]},
    '蜀山派': {"max_level": 40, "in_level": 7, "lingqi_max": 100, "lingqi_min": 50, "able": ["修仙秘境"]},
    '无尽之海': {"max_level": 15, "in_level": 10, "lingqi_max": 120, "lingqi_min": 70, "able": ['修仙秘境', '百花谷']},
    '百花谷': {"max_level": 40, "in_level": 10, "lingqi_max": 120, "lingqi_min": 70, "able": ['无尽之海']},
    '苍穹神州': {"max_level": 18, "in_level": 13, "lingqi_max": 150, "lingqi_min": 100, "able": ['大千世界', '洪荒大陆', '九天十国']},
    '九天十国': {"max_level": 21, "in_level": 16, "lingqi_max": 200, "lingqi_min": 150, "able": ['苍穹神州', '洪荒大陆', '诸天万界','失落之境']},
    '洪荒大陆': {"max_level": 24, "in_level": 19, "lingqi_max": 260, "lingqi_min": 200, "able": ['苍穹神州', '混沌绝地']},
    '诸天万界': {"max_level": 27, "in_level": 22, "lingqi_max": 320, "lingqi_min": 280, "able": ['九天十国']},
    '灵寰福址': {"max_level": 30, "in_level": 25, "lingqi_max": 400, "lingqi_min": 350, "able": ['修仙秘境']},
    '混沌绝地': {"max_level": 31, "in_level": 30, "lingqi_max": 500, "lingqi_min": 500, "able": ['洪荒大陆']},
    '荧惑仙境': {"max_level": 40, "in_level": 32, "lingqi_max": 1000, "lingqi_min": 1000, "able": []},
}

ZONGMEN = {
    "混元门": {"map": "修仙秘境", "condition": "len(linggen)>=3", "condition_desc": "灵根数量至少为3才可拜入混元门"},
    "狮府": {"map": "大千世界", "condition": "('土' in linggen) or ('木' in linggen)", "condition_desc": "只有具有土或木灵根才可拜入狮府"},
    "百花谷": {"map": "无尽之海", "condition": "('水' in linggen) or ('木' in linggen)", "condition_desc": "只有具有水或木灵根才可拜入百花谷"},
    "百炼山庄": {"map": "大千世界", "condition": "'火' in linggen", "condition_desc": "只有具有火灵根可以拜入百炼山庄"},
    "蜀山派": {"map": "修仙秘境", "condition": "'金' in linggen", "condition_desc": "只有具有金灵根可以拜入蜀山派"},
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

LIANBAO_NEED_LINGQI = {
    "凡人": 200,
    "锻体": 300,
    "练气": 400,
    "筑基": 500,
    "结丹": 600,
    "金丹": 800,
    "元婴": 1000,
    "化神": 1200,
    "洞虚": 1500,
    "大乘": 1800,
    "天仙": 3000,
    "真仙": 4000,
    "金仙": 5000,
}

DAQIAN_MAP = {
    "1": {"id": "1", "name": "新手村", "in_level": 0},
    "2": {"id": "2", "name": "大千世界", "in_level": 2},
    "3": {"id": "3", "name": "修仙秘境", "in_level": 7},
    "4": {"id": "4", "name": "无尽之海", "in_level": 10},
    "5": {"id": "5", "name": "苍穹神州", "in_level": 13},
    "6": {"id": "6", "name": "九天十国", "in_level": 16},
    "7": {"id": "7", "name": "洪荒大陆", "in_level": 19},
    # "8": {"id": "8", "name": "诸天万界", "in_level": 22},
    # "9": {"id": "9", "name": "灵寰福址", "in_level": 25},
    # "10": {"id": "10", "name": "混沌绝地", "in_level": 30},
    # "11": {"id": "11", "name": "荧惑仙境", "in_level": 32}
}

QIE_CUO_MAP = {
    "1": {"id": "1", "name": "狮府", "in_level": 2},
    "2": {"id": "2", "name": "百炼山庄", "in_level": 2},
    "3": {"id": "3", "name": "混元门", "in_level": 7},
    "4": {"id": "4", "name": "蜀山派", "in_level": 7},
    "5": {"id": "5", "name": "百花谷", "in_level": 10},
}

# 瓶颈
PINGJING = [1, 6, 9, 12, 15, 18, 21, 24, 27, 30, 31, 34, 37]
# 修炼效率
XIULIAN_SPEED = [100, 70, 50, 40, 30]

# 时间限制
# 操作间隔
# flmt = FreqLimiter(10 * 60)
# # 死亡cd
# die_flmt = FreqLimiter(1 * 60 * 60)

# 测试服
flmt = FreqLimiter(1)
die_flmt = FreqLimiter(10)

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

# 丹方
with open(os.path.join(FILE_PATH, 'config/danfang.json'), 'r', encoding='UTF-8') as fa:
    DANFANG = json.load(fa, strict=False)

# 锻造
with open(os.path.join(FILE_PATH, 'config/duanzao.json'), 'r', encoding='UTF-8') as fa:
    DUANZAO = json.load(fa, strict=False)

# 特效
with open(os.path.join(FILE_PATH, 'config/base_skill.json'), 'r', encoding='UTF-8') as fa:
    BASE_SKILL = json.load(fa, strict=False)
# 藏经阁
with open(os.path.join(FILE_PATH, 'config/cangjing.json'), 'r', encoding='UTF-8') as fa:
    CANGJING = json.load(fa, strict=False)

# 藏宝阁
with open(os.path.join(FILE_PATH, 'config/cangbao.json'), 'r', encoding='UTF-8') as fa:
    CANGBAO = json.load(fa, strict=False)

# boss
with open(os.path.join(FILE_PATH, 'config/boss.json'), 'r', encoding='UTF-8') as fa:
    BOSS = json.load(fa, strict=False)
# boss bonus
with open(os.path.join(FILE_PATH, 'config/boss_bonus.json'), 'r', encoding='UTF-8') as fa:
    BOSS_BONUS = json.load(fa, strict=False)

# exp change to feature
with open(os.path.join(FILE_PATH, 'config/exp_feature.json'), 'r', encoding='UTF-8') as fa:
    EXP_FEATURE = json.load(fa, strict=False)

# level feature max
with open(os.path.join(FILE_PATH, 'config/feature_max.json'), 'r', encoding='UTF-8') as fa:
    LEVEL_FEATURE_MAX = json.load(fa, strict=False)


# 副本
with open(os.path.join(FILE_PATH, 'config/fuben.json'), 'r', encoding='UTF-8') as fa:
    FU_BEN = json.load(fa, strict=False)

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


# 添加道具
def add_item_ignore_limit(gid, uid, item, num=1):
    i_c = ItemCounter()
    i_c._add_item(gid, uid, int(item['id']), num)
    return 1


# 检查背包空间是否足够
def check_have_space(gid, uid):
    if count_item(gid, uid) >= get_max_count(gid, uid):
        return 0
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
    count = get_user_counter(gid, uid, UserModel.NA_JIE)
    if count:
        max += count
    return max

# 获取指定群组状态
def get_group_counter(gid, state: GroupModel):
    i_c = ItemCounter()
    return i_c._get_group_state(gid, state)

# 获取指定群组状态
def save_group_counter(gid, state: GroupModel, num):
    i_c = ItemCounter()
    return i_c._save_group_state(gid, state ,num)

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


# 获取指定用户历史状态
def get_user_history(gid, uid, state: UserHistory):
    i_c = HistoryCounter()
    return i_c._get_user_info(gid, uid, state)


# 获取用户全部历史状态
def get_all_user_history(gid, uid):
    i_c = HistoryCounter()
    li = i_c._query_user_info(gid, uid)
    map = {i[0]: i[1] for i in li}
    result_map = {}
    for i in UserHistory:
        result_map[i] = 0
        if map.get(i.value[0]):
            result_map[i] = map.get(i.value[0])
    return result_map


# 存储指定用户历史状态
def save_user_history(gid, uid, state: UserHistory, num):
    i_c = HistoryCounter()
    i_c._save_user_info(gid, uid, state, num)


# 指定用户历史状态+num
def add_user_history(gid, uid, state: UserHistory, num=1):
    i_c = HistoryCounter()
    base = i_c._get_user_info(gid, uid, state)
    i_c._save_user_info(gid, uid, state, base + num)


# 留存历史
def cal_history(user):
    # 记录最大等级
    his_map = get_all_user_history(user.gid, user.uid)
    if his_map.get(UserHistory.MAX_LEVEL) < user.level:
        save_user_history(user.gid, user.uid, UserHistory.MAX_LEVEL, user.level)
    # 留存灵石
    save_user_history(user.gid, user.uid, UserHistory.RESTART_LINGSHI, int(user.lingshi / 2))
    # 随机留存一个身上的道具
    counter = ItemCounter()
    items = counter._get_item(user.gid, user.uid)
    if items:
        i = random.choice(items)
        item = ITEM_INFO[str(i[0])]
        save_user_history(user.gid, user.uid, UserHistory.RESTART_ITEM, int(item['id']))
    else:
        save_user_history(user.gid, user.uid, UserHistory.RESTART_ITEM, 0)
    # 留存心法
    if user.gongfa != "无":
        xinfa = get_item_by_name(user.gongfa)
        save_user_history(user.gid, user.uid, UserHistory.RESTART_XINFA, int(xinfa['id']))
    else:
        save_user_history(user.gid, user.uid, UserHistory.RESTART_XINFA, 0)
    # 留存功法
    if user.gongfa2 != "无":
        gongfa = get_item_by_name(user.gongfa2)
        save_user_history(user.gid, user.uid, UserHistory.RESTART_GONGFA, int(gongfa['id']))
    else:
        save_user_history(user.gid, user.uid, UserHistory.RESTART_GONGFA, 0)
    # 留存神通
    if user.gongfa3 != "无":
        shentong = get_item_by_name(user.gongfa3)
        save_user_history(user.gid, user.uid, UserHistory.RESTART_SHENTONG, int(shentong['id']))
    else:
        save_user_history(user.gid, user.uid, UserHistory.RESTART_SHENTONG, 0)
    # 更新历史最高血量
    if his_map.get(UserHistory.MAX_HP) < user.battle_hp:
        save_user_history(user.gid, user.uid, UserHistory.MAX_HP, user.battle_hp)
    # 更新历史最高蓝量
    if his_map.get(UserHistory.MAX_MP) < user.battle_mp:
        save_user_history(user.gid, user.uid, UserHistory.MAX_MP, user.battle_mp)
    # 更新历史最高物攻
    if his_map.get(UserHistory.MAX_ACT) < user.battle_atk1:
        save_user_history(user.gid, user.uid, UserHistory.MAX_ACT, user.battle_atk1)
    # 更新历史最高魔攻
    if his_map.get(UserHistory.MAX_ACT2) < user.battle_atk2:
        save_user_history(user.gid, user.uid, UserHistory.MAX_ACT2, user.battle_atk2)
    # 更新历史最高物防
    if his_map.get(UserHistory.MAX_DEFEN1) < user.battle_defen1:
        save_user_history(user.gid, user.uid, UserHistory.MAX_DEFEN1, user.battle_defen1)
    # 更新历史最高术防
    if his_map.get(UserHistory.MAX_DEFEN2) < user.battle_defen2:
        save_user_history(user.gid, user.uid, UserHistory.MAX_DEFEN2, user.battle_defen2)


# 角色死亡
def delete_user(user):
    # 储存历史信息
    cal_history(user)

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
    # 删除上架物品
    it = ItemCounter()
    it._del_trade_info(user.gid, user.uid)
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
        # 大罗洞观
        self.daluo=0

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
            self.cal_buff(buff)
        # 心法加成
        xinfa = get_gongfa_by_name(self.gongfa)
        if xinfa:
            buff = xinfa.get('buff')
            if buff:
                self.cal_buff(buff)

    def cal_buff(self, buff):
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
        content = {"daohang": self.daohang, "atk1": self.battle_atk1, "atk2": self.battle_atk2,
                   "defen1": self.battle_defen1, "tizhi": self.tizhi, "lingli": self.lingli,
                   "defen2": self.battle_defen2, "hp": self.battle_hp, "mp": self.battle_mp, "level": self.level}
        if buff.get('hp_exec'):
            self.battle_hp = int(eval(buff.get('hp_exec'), content))
        if buff.get('mp_exec'):
            self.battle_mp = int(eval(buff.get('mp_exec'), content))
        if buff.get('atk1_exec'):
            self.battle_atk1 = int(eval(buff.get('atk1_exec'), content))
        if buff.get('atk2_exec'):
            self.battle_atk2 = int(eval(buff.get('atk2_exec'), content))
        if buff.get('defen1_exec'):
            self.battle_defen1 = int(eval(buff.get('defen1_exec'), content))
        if buff.get('defen2_exec'):
            self.battle_defen2 = int(eval(buff.get('defen2_exec'), content))

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
        self.max_item_count = get_max_count(self.gid, self.uid)
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
        item_id = get_user_counter(self.gid, self.uid, UserModel.LIANBAO_ITEM)
        if item_id:
            item = ITEM_INFO[str(item_id)]
            need = LIANBAO_NEED_LINGQI[item['level']]
            have = get_user_counter(self.gid, self.uid, UserModel.LIANBAO_LINGQI)
            if have >= need:
                await bot.send(ev, "炼宝灵气已经充足，请使用#练宝 指令获取炼制完成的法宝")
        await self.check_cd_ignore_other(bot, ev)
        if self.gongfa3 == "缩地成寸":
            if get_user_counter(self.gid, self.uid, UserModel.SUODI) > 0:
                add_user_counter(self.gid, self.uid, UserModel.SUODI, num=-1)
        if self.gongfa3 == "大罗洞观":
            if random.randint(1, 10) == 1:
                self.daluo = 1
                await bot.send(ev, "大罗入世，窥晓阴阳，观测天机，规避天道，此次行动取消CD")

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

    async def check_in_fuben(self, bot, ev):
        fuben = get_user_counter(ev.group_id, ev.uid, UserModel.FU_BEN)
        if fuben:
            await bot.finish(ev, f"你身处秘境之中，无法进行此项操作", at_sender=True)



    def start_cd(self):
        # 练宝相关
        item_id = get_user_counter(self.gid, self.uid, UserModel.LIANBAO_ITEM)
        if item_id:
            address = MAP.get(self.map)
            min = address["lingqi_min"]
            max = address["lingqi_max"]
            lingqi = int(random.randint(min, max) * 0.1)
            if self.gongfa3 == "天灵地动":
                lingqi = 2 * lingqi
            add_user_counter(self.gid, self.uid, UserModel.LIANBAO_LINGQI, lingqi)
        if not self.daluo:
            flmt.start_cd(self.uid)

class OtherUserInfo(AllUserInfo):
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


# 筛选道具名称
def filter_item_name(type=[], level=[]):
    result = [i for i in ITEM_NAME_MAP.keys()]
    if type:
        result = [i for i in result if ITEM_NAME_MAP[i]['type'] in type]
    if level:
        result = [i for i in result if ITEM_NAME_MAP[i]['level'] in level]
    return result


from hoshino.config.__bot__ import BASE_DB_PATH
from datetime import datetime, timedelta
from hoshino.util import DailyNumberLimiter

DB_PATH = os.path.expanduser(BASE_DB_PATH + "xiuxian_limit.db")


# 限制器操作类
class RecordDAO:
    def __init__(self, db_path):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self._create_table()

    def connect(self):
        return sqlite3.connect(self.db_path)

    def _create_table(self):
        with self.connect() as conn:
            conn.execute(
                "CREATE TABLE IF NOT EXISTS limiter"
                "(key TEXT NOT NULL, num INT NOT NULL, date INT, PRIMARY KEY(key))"
            )

    def exist_check(self, key):
        try:
            key = str(key)
            with self.connect() as conn:
                conn.execute("INSERT INTO limiter (key,num,date) VALUES (?, 0,-1)", (key,), )
            return
        except:
            return

    def get_num(self, key):
        self.exist_check(key)
        key = str(key)
        with self.connect() as conn:
            r = conn.execute(
                "SELECT num FROM limiter WHERE key=? ", (key,)
            ).fetchall()
            r2 = r[0]
        return r2[0]

    def clear_key(self, key):
        key = str(key)
        self.exist_check(key)
        with self.connect() as conn:
            conn.execute("UPDATE limiter SET num=0 WHERE key=?", (key,), )
        return

    def increment_key(self, key, num):
        self.exist_check(key)
        key = str(key)
        with self.connect() as conn:
            conn.execute("UPDATE limiter SET num=num+? WHERE key=?", (num, key,))
        return

    def get_date(self, key):
        self.exist_check(key)
        key = str(key)
        with self.connect() as conn:
            r = conn.execute(
                "SELECT date FROM limiter WHERE key=? ", (key,)
            ).fetchall()
            r2 = r[0]
        return r2[0]

    def set_date(self, date, key):
        print(date)
        self.exist_check(key)
        key = str(key)
        with self.connect() as conn:
            conn.execute("UPDATE limiter SET date=? WHERE key=?", (date, key,), )
        return


db = RecordDAO(DB_PATH)


# 每天每群限制n次
class DailyAmountLimiter(DailyNumberLimiter):
    def __init__(self, types, max_num, reset_hour):
        super().__init__(max_num)
        self.reset_hour = reset_hour
        self.type = types

    def check(self, key) -> bool:
        now = datetime.now(self.tz)
        key = list(key)
        key.append(self.type)
        key = tuple(key)
        day = (now - timedelta(hours=self.reset_hour)).day
        if day != db.get_date(key):
            db.set_date(day, key)
            db.clear_key(key)
        return bool(db.get_num(key) < self.max)

    def check10(self, key) -> bool:
        now = datetime.now(self.tz)
        key = list(key)
        key.append(self.type)
        key = tuple(key)
        day = (now - timedelta(hours=self.reset_hour)).day
        if day != db.get_date(key):
            db.set_date(day, key)
            db.clear_key(key)
        return bool(db.get_num(key) < 10)

    def get_num(self, key):
        key = list(key)
        key.append(self.type)
        key = tuple(key)
        return db.get_num(key)

    def increase(self, key, num=1):
        key = list(key)
        key.append(self.type)
        key = tuple(key)
        db.increment_key(key, num)

    def reset(self, key):
        key = list(key)
        key.append(self.type)
        key = tuple(key)
        db.clear_key(key)


daily_fenglu_limiter = DailyAmountLimiter("fenglu", 1, 5)
daily_huafu_limiter = DailyAmountLimiter("huafu", 2, 5)
daily_mission_limiter = DailyAmountLimiter("mission", 10, 5)
daily_shiLian_limiter = DailyAmountLimiter("shilian", 5, 5)
