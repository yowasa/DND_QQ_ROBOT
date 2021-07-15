import random
from .ItemCounter import *


# 记录决斗和下注数据
class DuelJudger:
    def __init__(self):
        self.on = {}
        self.accept_on = {}
        self.support_on = {}
        self.fire_on = {}
        self.deadnum = {}
        self.support = {}
        self.turn = {}
        self.duelid = {}
        self.isaccept = {}
        self.hasfired_on = {}

    def set_support(self, gid):
        self.support[gid] = {}

    def get_support(self, gid):
        return self.support[gid] if self.support.get(gid) is not None else 0

    def add_support(self, gid, uid, id, score):
        self.support[gid][uid] = [id, score]

    def get_support_id(self, gid, uid):
        if self.support[gid].get(uid) is not None:
            return self.support[gid][uid][0]
        else:
            return 0

    def get_support_score(self, gid, uid):
        if self.support[gid].get(uid) is not None:
            return self.support[gid][uid][1]
        else:
            return 0

    # 五个开关：决斗，接受，下注， 开枪, 是否已经开枪

    def get_on_off_status(self, gid):
        return self.on[gid] if self.on.get(gid) is not None else False

    def turn_on(self, gid):
        self.on[gid] = True

    def turn_off(self, gid):
        self.on[gid] = False

    def get_on_off_accept_status(self, gid):
        return self.accept_on[gid] if self.accept_on.get(gid) is not None else False

    def turn_on_accept(self, gid):
        self.accept_on[gid] = True

    def turn_off_accept(self, gid):
        self.accept_on[gid] = False

    def get_on_off_support_status(self, gid):
        return self.support_on[gid] if self.support_on.get(gid) is not None else False

    def turn_on_support(self, gid):
        self.support_on[gid] = True

    def turn_off_support(self, gid):
        self.support_on[gid] = False

    def get_on_off_fire_status(self, gid):
        return self.fire_on[gid] if self.fire_on.get(gid) is not None else False

    def turn_on_fire(self, gid):
        self.fire_on[gid] = True

    def turn_off_fire(self, gid):
        self.fire_on[gid] = False

    def get_on_off_hasfired_status(self, gid):
        return self.hasfired_on[gid] if self.hasfired_on.get(gid) is not None else False

    def turn_on_hasfired(self, gid):
        self.hasfired_on[gid] = True

    def turn_off_hasfired(self, gid):
        self.hasfired_on[gid] = False

    # 记录决斗者id
    def init_duelid(self, gid):
        self.duelid[gid] = []

    def set_duelid(self, gid, id1, id2):
        self.duelid[gid] = [id1, id2]

    def get_duelid(self, gid):
        return self.duelid[gid] if self.accept_on.get(gid) is not None else [0, 0]

    # 查询一个决斗者是1号还是2号
    def get_duelnum(self, gid, uid):
        return self.duelid[gid].index(uid) + 1

    # 记录由谁开枪
    def init_turn(self, gid):
        self.turn[gid] = 1

    def get_turn(self, gid):
        return self.turn[gid] if self.turn[gid] is not None else 0

    def change_turn(self, gid):
        if self.get_turn(gid) == 1:
            self.turn[gid] = 2
            return 2
        else:
            self.turn[gid] = 1
            return 1

    # 记录子弹位置
    def init_deadnum(self, gid):
        self.deadnum[gid] = None

    def set_deadnum(self, gid, num):
        self.deadnum[gid] = num

    def get_deadnum(self, gid):
        return self.deadnum[gid] if self.deadnum[gid] is not None else False

    # 记录是否接受
    def init_isaccept(self, gid):
        self.isaccept[gid] = False

    def on_isaccept(self, gid):
        self.isaccept[gid] = True

    def off_isaccept(self, gid):
        self.isaccept[gid] = False

    def get_isaccept(self, gid):
        return self.isaccept[gid] if self.isaccept[gid] is not None else False


# 记录礼物交换数据
class GiftChange:
    def __init__(self):
        self.giftchange_on = {}
        self.waitchange = {}
        self.isaccept = {}
        self.changeid = {}

    # 礼物交换开关
    def get_on_off_giftchange_status(self, gid):
        return self.giftchange_on[gid] if self.giftchange_on.get(gid) is not None else False

    def turn_on_giftchange(self, gid):
        self.giftchange_on[gid] = True

    def turn_off_giftchange(self, gid):
        self.giftchange_on[gid] = False

    # 礼物交换发起开关
    def get_on_off_waitchange_status(self, gid):
        return self.waitchange[gid] if self.waitchange.get(gid) is not None else False

    def turn_on_waitchange(self, gid):
        self.waitchange[gid] = True

    def turn_off_waitchange(self, gid):
        self.waitchange[gid] = False

    # 礼物交换是否接受开关
    def turn_on_accept_giftchange(self, gid):
        self.isaccept[gid] = True

    def turn_off_accept_giftchange(self, gid):
        self.isaccept[gid] = False

    def get_isaccept_giftchange(self, gid):
        return self.isaccept[gid] if self.isaccept[gid] is not None else False

    # 记录礼物交换请求接收者id
    def init_changeid(self, gid):
        self.changeid[gid] = []

    def set_changeid(self, gid, id2):
        self.changeid[gid] = id2

    def get_changeid(self, gid):
        return self.changeid[gid] if self.changeid.get(gid) is not None else 0


class duelrandom():
    def __init__(self):
        self.random_gold_on = {}
        self.random_gold = {}
        self.rdret = {}
        self.user = {}

    def turn_on_random_gold(self, gid):
        self.random_gold_on[gid] = True

    def turn_off_random_gold(self, gid):
        self.random_gold_on[gid] = False

    def set_gold(self, gid):
        self.user[gid] = []

    def add_gold(self, gid, gold, num):
        self.random_gold[gid] = {'GOLD': gold, 'NUM': num}

    def get_gold(self, gid):
        return self.random_gold[gid]['GOLD']

    def get_num(self, gid):
        return self.random_gold[gid]['NUM']

    def add_user(self, gid, uid):
        self.user[gid].append(uid)

    def get_on_off_random_gold(self, gid):
        return self.random_gold_on[gid] if self.random_gold_on.get(gid) is not None else False

    def random_g(self, gid, gold, num):
        z = []
        ret = random.sample(range(1, gold), num - 1)
        ret.append(0)
        ret.append(gold)
        ret.sort()
        for i in range(len(ret) - 1):
            z.append(ret[i + 1] - ret[i])
        self.rdret[gid] = z

    def get_user_random_gold(self, gid, num):
        rd = random.randint(0, num - 1)
        print(rd)
        ugold = self.rdret[gid][rd]
        self.rdret[gid].remove(ugold)
        return ugold


# 红包发送操作实例
r_gold = duelrandom()
# 决斗数据操作实例
duel_judger = DuelJudger()
# 礼物交换操作实例
gift_change = GiftChange()

ITEM_INFO = {
    "1": {
        "id": "1",
        "name": "天命之子",
        "rank": "S",
        "desc": "无视100的等级上限 为自己的女友增加10级 最高不超过200级(仅100满级以上可以使用)",
    },
    "2": {
        "id": "2",
        "name": "前世之忆",
        "rank": "S",
        "desc": "保留女友的等级rank为自己女友增加一次转生次数 不能超过转生次数限制",
    },
    "3": {
        "id": "3",
        "name": "命运牵引",
        "rank": "S",
        "desc": "定向招募卡池中的女友,无视卡池限制与女友上限",
    },
    "4": {
        "id": "4",
        "name": "空想之物",
        "rank": "A",
        "desc": "90%概率随机获得一件UR装备 10%概率获得MR装备",
    },
    "5": {
        "id": "5",
        "name": "好事成双",
        "rank": "A",
        "desc": "选择自己已拥有的一件道具 令其数量+1",
    },
    "6": {
        "id": "6",
        "name": "四重存在",
        "rank": "A",
        "desc": "选择自己一个A级以下的道具 令其数量+3",
    },
    "7": {
        "id": "7",
        "name": "狂赌之渊",
        "rank": "S",
        "desc": "为本群开启梭哈庆典 持续到这个小时结束",
    },
    "8": {
        "id": "8",
        "name": "咲夜怀表",
        "rank": "A",
        "desc": "使用后刷新自己的副本 签到 低保 约会 决斗 礼物次数",
    },
    "9": {
        "id": "9",
        "name": "梦境巡游",
        "rank": "B",
        "desc": "发现女友，可以刷新发现结果，选择要或不要，至多10次",
    },

    "10": {
        "id": "10",
        "name": "超再生力",
        "rank": "B",
        "desc": "使用后刷新自己当日副本限制次数及决斗次数",
    },
    "11": {
        "id": "11",
        "name": "有效分裂",
        "rank": "B",
        "desc": "使用后随机获取两个道具",
    },
    "12": {
        "id": "12",
        "name": "异界馈赠",
        "rank": "C",
        "desc": "随机增加财富(10000-100000)",
    },
    "13": {
        "id": "13",
        "name": "乐善好施",
        "rank": "C",
        "desc": "发送一次50000金币5个的红包(不消耗自己的金币) 每有一个人领取 增加500声望",
    },
    "14": {
        "id": "14",
        "name": "藏宝图",
        "rank": "C",
        "desc": "进行一次愉快的挖宝 随机金币 声望 装备 道具",
    },
    "15": {
        "id": "15",
        "name": "战无不胜",
        "rank": "C",
        "desc": "使用后下一次副本战斗战力计算增加2倍",
    },
    "16": {
        "id": "16",
        "name": "战斗记忆",
        "rank": "C",
        "desc": "增加300000经验到自己经验池",
    },
    "17": {
        "id": "17",
        "name": "零时迷子",
        "rank": "C",
        "desc": "使用后刷新自己当日副本限制次数",
    },
    "18": {
        "id": "18",
        "name": "鬼人药剂",
        "rank": "D",
        "desc": "使用后下一次副本战斗战力计算增加1倍",
    },
    "19": {
        "id": "19",
        "name": "派对狂欢",
        "rank": "D",
        "desc": "为本群开启免费招募庆典 持续到这个小时结束",
    },
    "20": {
        "id": "20",
        "name": "公主之心",
        "rank": "D",
        "desc": "全部女友增加30好感",
    },
    "21": {
        "id": "21",
        "name": "生财有道",
        "rank": "D",
        "desc": "随机增加财富(1000-30000)",
    },
    "22": {
        "id": "22",
        "name": "小恩小惠",
        "rank": "D",
        "desc": "随机增加声望(100-3000)",
    },
    "23": {
        "id": "23",
        "name": "再来一瓶",
        "rank": "D",
        "desc": "刷新自己签到次数",
    },
    "24": {
        "id": "24",
        "name": "精英对局",
        "rank": "D",
        "desc": "刷新自己的决斗次数",
    },
    "25": {
        "id": "25",
        "name": "经验之书",
        "rank": "D",
        "desc": "增加100000经验到自己经验池",
    },
    "26": {
        "id": "26",
        "name": "许愿神灯",
        "rank": "S",
        "desc": "使用后获取指定道具",
    },
    "27": {
        "id": "27",
        "name": "永恒爱恋",
        "rank": "S",
        "desc": "无需使用，持有多个时不重复计算，当持有永恒爱恋时妻子计算战力增加100%",
    },
    "28": {
        "id": "28",
        "name": "光学迷彩",
        "rank": "A",
        "desc": "无需使用，只要带在身上决斗时就不会承受损失，但是决斗失败有10%的概率被消耗掉",
    },
    "29": {
        "id": "29",
        "name": "贤者之石",
        "rank": "B",
        "desc": "使用后接下来5次副本掉落装备随机替换为品质高一级的红魔馆系列装备(最高不超过UR)",
    },
    "30": {
        "id": "30",
        "name": "击鼓传花",
        "rank": "B",
        "desc": "决斗胜利时获得金币声望增加20% 决斗失败时转移到获胜者的身上 一个人不能持有两件击鼓传花（会被覆盖）",
    },
    "31": {
        "id": "31",
        "name": "投影魔术",
        "rank": "C",
        "desc": "选择一名其他角色，获得一件稀有度低于其持有的最高稀有度的道具的复制",
    },

}

ITEM_NAME_MAP = {ITEM_INFO[i]["name"]: ITEM_INFO[i] for i in ITEM_INFO.keys()}

ITEM_RANK_MAP = {}

for k, v in ITEM_INFO.items():
    if not ITEM_RANK_MAP.get(v['rank']):
        ITEM_RANK_MAP[v['rank']] = []
    ITEM_RANK_MAP.get(v['rank']).append(v['id'])


# 随机选择道具
def choose_item():
    number = random.randint(1, 100)
    if number == 1:
        i_ids = ITEM_RANK_MAP['S']
    elif number <= 6:
        i_ids = ITEM_RANK_MAP['A']
    elif number <= 16:
        i_ids = ITEM_RANK_MAP['B']
    elif number <= 36:
        i_ids = ITEM_RANK_MAP['C']
    else:
        i_ids = ITEM_RANK_MAP['D']
    id = random.choice(i_ids)
    return ITEM_INFO.get(id)


# 根据名字获取道具
def get_item_by_name(name):
    return ITEM_NAME_MAP.get(name)


# 检查是否持有道具
def check_have_item(gid, uid, item):
    i_c = ItemCounter()
    num = i_c._get_item_num(gid, uid, int(item['id']))
    return num


# 添加道具
def add_item(gid, uid, item):
    if item['name'] == '击鼓传花':
        if check_have_item(gid, uid, item):
            return
    i_c = ItemCounter()
    i_c._add_item(gid, uid, int(item['id']))


# 消耗道具
def use_item(gid, uid, item):
    i_c = ItemCounter()
    i_c._add_item(gid, uid, int(item['id']), num=-1)


# 获取指定用户状态
def get_user_counter(gid, uid, state: UserModel):
    i_c = ItemCounter()
    return i_c._get_user_info(gid, uid, state)


# 存储指定用户状态
def save_user_counter(gid, uid, state: UserModel, num):
    i_c = ItemCounter()
    i_c._save_user_info(gid, uid, state, num)
