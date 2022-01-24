import json
import os
from hoshino.util import FreqLimiter
from .counter.LimiterCounter import DailyAmountLimiter

CE_SHI_FLAG = True

# 境界列表
LEVEL_MAP = {
    "1": {'id': "1", 'name': '凡人', "sub_level": 1, "need_exp": 10},
    "2": {'id': "2", 'name': '锻体', "sub_level": 5, "need_exp": 50},
    "3": {'id': "3", 'name': '炼气', "sub_level": 3, "need_exp": 200},
    "4": {'id': "4", 'name': '筑基', "sub_level": 3, "need_exp": 400},
    "5": {'id': "5", 'name': '结丹', "sub_level": 3, "need_exp": 1000},
    "6": {'id': "6", 'name': '金丹', "sub_level": 9, "need_exp": 2000},
    "7": {'id': "7", 'name': '元婴', "sub_level": 3, "need_exp": 4000},
    "8": {'id': "8", 'name': '化神', "sub_level": 3, "need_exp": 10000},
    "9": {'id': "9", 'name': '洞虚', "sub_level": 3, "need_exp": 20000},
    "10": {'id': "10", 'name': '大乘', "sub_level": 3, "need_exp": 40000},
    "11": {'id': "11", 'name': '渡劫', "sub_level": 1, "need_exp": 0},
    "12": {'id': "12", 'name': '天仙', "sub_level": 3, "need_exp": 50000},
    "13": {'id': "13", 'name': '真仙', "sub_level": 3, "need_exp": 100000},
    "14": {'id': "15", 'name': '金仙', "sub_level": 3, "need_exp": 200000}
}
# 俸禄
FENGLU_MAP = {
    "凡人": 10,
    "锻体": 20,
    "炼气": 50,
    "筑基": 70,
    "结丹": 70,
    "结丹": 100,
    "金丹": 200,
    "元婴": 300,
    "化神": 500,
    "洞虚": 800,
    "大乘": 800,
    "渡劫": 800,
    "天仙": 1000,
    "真仙": 1000,
    "金仙": 1000,
}
# 地图
MAP = {
    '新手村': {"max_level": 1, "in_level": 0, "aura_max": 10, "aura_min": 10, "path": ['大千世界']},
    '大千世界': {"max_level": 3, "in_level": 2, "aura_max": 50, "aura_min": 30,
             "path": ['新手村', '修仙秘境', '苍穹神州', '狮府', '百炼山庄']},
    '狮府': {"max_level": 14, "in_level": 2, "aura_max": 50, "aura_min": 30, "path": ['大千世界']},
    '百炼山庄': {"max_level": 14, "in_level": 2, "aura_max": 50, "aura_min": 30, "path": ['大千世界']},
    '修仙秘境': {"max_level": 4, "in_level": 3, "aura_max": 100, "aura_min": 50,
             "path": ['大千世界', '灵寰福址', '无尽之海', '混元门', '蜀山派']},
    '混元门': {"max_level": 14, "in_level": 3, "aura_max": 100, "aura_min": 50, "path": ["修仙秘境"]},
    '蜀山派': {"max_level": 14, "in_level": 3, "aura_max": 100, "aura_min": 50, "path": ["修仙秘境"]},
    '无尽之海': {"max_level": 5, "in_level": 4, "aura_max": 120, "aura_min": 70, "path": ['修仙秘境', '百花谷']},
    '百花谷': {"max_level": 14, "in_level": 4, "aura_max": 120, "aura_min": 70, "path": ['无尽之海']},
    '苍穹神州': {"max_level": 6, "in_level": 5, "aura_max": 150, "aura_min": 100, "path": ['大千世界', '洪荒大陆', '九天十国']},
    '九天十国': {"max_level": 7, "in_level": 6, "aura_max": 200, "aura_min": 150, "path": ['苍穹神州', '诸天万界']},
    '洪荒大陆': {"max_level": 8, "in_level": 7, "aura_max": 260, "aura_min": 200, "path": ['苍穹神州']},
    '诸天万界': {"max_level": 9, "in_level": 8, "aura_max": 320, "aura_min": 280, "path": ['九天十国']},
    '灵寰福址': {"max_level": 10, "in_level": 9, "aura_max": 400, "aura_min": 350, "path": ['修仙秘境']},
    '混沌绝地': {"max_level": 11, "in_level": 10, "aura_max": 500, "aura_min": 500, "path": []},
    '荧惑仙境': {"max_level": 14, "in_level": 12, "aura_max": 1000, "aura_min": 1000, "path": []},
}
# 宗门
ZONGMEN = {
    "混元门": {"map": "修仙秘境", "condition": "len(magic_root)>=3", "condition_desc": "灵根数量至少为3才可拜入混元门"},
    "狮府": {"map": "大千世界", "condition": "('土' in magic_root) or ('木' in magic_root)",
           "condition_desc": "只有具有土或木灵根才可拜入狮府"},
    "百花谷": {"map": "无尽之海", "condition": "('水' in magic_root) or ('木' in magic_root)",
            "condition_desc": "只有具有水或木灵根才可拜入百花谷"},
    "百炼山庄": {"map": "大千世界", "condition": "'火' in magic_root", "condition_desc": "只有具有火灵根可以拜入百炼山庄"},
    "蜀山派": {"map": "修仙秘境", "condition": "'金' in magic_root", "condition_desc": "只有具有金灵根可以拜入蜀山派"},
}

# 境界所能拥有的道具上限
ITEM_CARRY = {
    "凡人": 3,
    "锻体": 5,
    "炼气": 7,
    "筑基": 9,
    "结丹": 10,
    "结丹": 11,
    "金丹": 12,
    "元婴": 13,
    "化神": 14,
    "洞虚": 15,
    "大乘": 16,
    "渡劫": 17,
    "天仙": 18,
    "真仙": 19,
    "金仙": 20
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

YOULI_DAQIAN_MAP = {
    "1": {"id": "1", "name": "新手村", "in_level": 1},
    "2": {"id": "2", "name": "大千世界", "in_level": 2},
    "3": {"id": "3", "name": "修仙秘境", "in_level": 3},
    "4": {"id": "4", "name": "无尽之海", "in_level": 4},
    "5": {"id": "5", "name": "苍穹神州", "in_level": 5},
    "6": {"id": "6", "name": "九天十国", "in_level": 6},
    # "7": {"id": "7", "name": "洪荒大陆", "in_level": 7},
    # "8": {"id": "8", "name": "诸天万界", "in_level": 8},
    # "9": {"id": "9", "name": "灵寰福址", "in_level": 9},
    # "10": {"id": "10", "name": "混沌绝地", "in_level": 10},
    # "11": {"id": "11", "name": "荧惑仙境", "in_level": 12}
}

QIE_CUO_MAP = {
    "1": {"id": "1", "name": "狮府", "in_level": 2},
    "2": {"id": "2", "name": "百炼山庄", "in_level": 2},
    "3": {"id": "3", "name": "混元门", "in_level": 7},
    "4": {"id": "4", "name": "蜀山派", "in_level": 7},
    "5": {"id": "5", "name": "百花谷", "in_level": 10},
}

# 修炼效率
XIULIAN_SPEED = [100, 70, 50, 40, 30]

# 时间限制
# 操作间隔
flmt = FreqLimiter(10 * 60)
# 死亡cd
die_flmt = FreqLimiter(1 * 60 * 60)

# 测试服
if CE_SHI_FLAG:
    flmt = FreqLimiter(10)
    die_flmt = FreqLimiter(60)

# 文件路径
FILE_PATH = os.path.dirname(__file__)

# 物品列表
with open(os.path.join(FILE_PATH, 'config/item_info.json'), 'r', encoding='UTF-8') as fa:
    ITEM_INFO = json.load(fa, strict=False)
ITEM_NAME_MAP = {ITEM_INFO[i]["name"]: ITEM_INFO[i] for i in ITEM_INFO.keys()}

# 装备
with open(os.path.join(FILE_PATH, 'config/equipment.json'), 'r', encoding='UTF-8') as fa:
    EQUIPMENT_INFO = json.load(fa, strict=False)

# 功法列表
with open(os.path.join(FILE_PATH, 'config/ability.json'), 'r', encoding='UTF-8') as fa:
    ABILITY_INFO = json.load(fa, strict=False)

ABILITY_NAME_MAP = {ABILITY_INFO[i]["name"]: ABILITY_INFO[i] for i in ABILITY_INFO.keys()}

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
with open(os.path.join(FILE_PATH, 'config/battle_skill.json'), 'r', encoding='UTF-8') as fa:
    BASE_SKILL = json.load(fa, strict=False)

# 藏经阁
with open(os.path.join(FILE_PATH, 'config/cangjing.json'), 'r', encoding='UTF-8') as fa:
    CANGJING = json.load(fa, strict=False)

# boss
with open(os.path.join(FILE_PATH, 'config/boss.json'), 'r', encoding='UTF-8') as fa:
    BOSS = json.load(fa, strict=False)

# boss bonus
with open(os.path.join(FILE_PATH, 'config/boss_bonus.json'), 'r', encoding='UTF-8') as fa:
    BOSS_BONUS = json.load(fa, strict=False)

# exp change to feature
with open(os.path.join(FILE_PATH, 'config/exp_feature.json'), 'r', encoding='UTF-8') as fa:
    EXP_FEATURE = json.load(fa, strict=False)

# 每天领取俸禄次数
daily_fenglu_limiter = DailyAmountLimiter("fenglu", 1, 5)
# 每天画符次数
daily_huafu_limiter = DailyAmountLimiter("huafu", 2, 5)
# 每天任务次数
daily_mission_limiter = DailyAmountLimiter("mission", 10, 5)
