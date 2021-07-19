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
        "desc": "获得一件MR装备",
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
        "desc": "为本群开启梭哈庆典 持续到这个小时结束。注：庆典期间转账交易税率将提高到50%",
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
    "32": {
        "id": "32",
        "name": "等价交换",
        "rank": "C",
        "desc": "选择一个自己持有的道具 将其变为对应稀有度的其他道具",
    },
    "33": {
        "id": "33",
        "name": "人海战术",
        "rank": "A",
        "desc": "随机获取10件D级道具",
    },
    "34": {
        "id": "34",
        "name": "公平交易",
        "rank": "C",
        "desc": "选择自己持有的一个道具 将其变成对应低一级稀有度的随机两件其他道具",
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
def add_item(gid, uid, item, num=1):
    if item['name'] == '击鼓传花':
        if check_have_item(gid, uid, item):
            return
    i_c = ItemCounter()
    i_c._add_item(gid, uid, int(item['id']), num)


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


class BuildModel(Enum):
    CENTER = {"id": 101, "name": "市政中心", "sw": 1000, "gold": 10000, "area": 10, "time": 1, "limit": 1,
              "desc": "城市管理枢纽只有拥有才能执行行政命令"}
    MARKET = {"id": 102, "name": "贸易市场", "sw": 1000, "gold": 50000, "area": 7, "time": 3, "limit": 10,
              "desc": "城市商业贸易中心，能为你带来不菲的收入（增加金币）"}
    ITEM_SHOP = {"id": 103, "name": "道具商店", "sw": 100, "gold": 10000, "area": 5, "time": 2, "limit": 1,
                 "desc": "神秘的道具商店，黑心老板商只允许顾客盲盒购买（可使用[购买道具]指令）"}
    TV_STATION = {"id": 104, "name": "报社", "sw": 5000, "gold": 10000, "area": 8, "time": 3, "limit": 10,
                  "desc": "城市的媒体部门，能宣传你的伟业（增加声望）"}
    POLICE_OFFICE = {"id": 105, "name": "警察局", "sw": 2000, "gold": 30000, "area": 10, "time": 3, "limit": 2,
                     "desc": "谁还想暴乱？城市的治安部门，让你城市治安稳定"}
    KONGFU = {"id": 106, "name": "练功房", "sw": 2500, "gold": 20000, "area": 6, "time": 2, "limit": 2,
              "desc": "挂机是游戏的一部分，挂机修炼获得的经验增加5倍(复数个叠加而非叠乘)"}
    HUANBAO = {"id": 107, "name": "环保局", "sw": 40000, "gold": 30000, "area": 15, "time": 3, "limit": 1,
               "desc": "环境保护，人人有责，可以依据领地林地面积提供声望"}
    ZHIHUI = {"id": 108, "name": "指挥部", "sw": 10000, "gold": 100000, "area": 20, "time": 3, "limit": 1,
              "desc": "作战指挥中心，可以提高副本战斗人员的战斗能力(副本战力计算+20%)"}
    DIZHI = {"id": 109, "name": "地质局", "sw": 3500, "gold": 200000, "area": 25, "time": 4, "limit": 2,
             "desc": "地址勘察中心，发现领地内不为人知的秘密(每日获取一个藏宝图)"}
    KELA = {"id": 110, "name": "科拉超深井", "sw": 50000, "gold": 500000, "area": 70, "time": 7, "limit": 1,
            "desc": "通向地球中心的超级深井，里面传来了地狱的声音(每日获取一个零时迷子，低概率产出咲夜怀表)"}
    FISSION_CENTER = {"id": 111, "name": "裂变中心", "sw": 100000, "gold": 1000000, "area": 120, "time": 10, "limit": 1,
                      "desc": "拥有无限可能性的裂变中心，他的存在让人裂开（每日获取两个有效分裂,低概率产出四重存在或好事成双）"}
    EQUIP_CENTER = {"id": 112, "name": "装备工坊", "sw": 2000, "gold": 100000, "area": 15, "time": 3, "limit": 1,
                    "desc": " 装备工坊 可以使用[装备熔炼]指令，用低级装备合成高级装备 合成品级越高失败率越高"}
    TECHNOLOGY_CENTER = {"id": 113, "name": "科技研究所", "sw": 100000, "gold": 1000000, "area": 30, "time": 5, "limit": 1,
                         "desc": "解锁领地科技 可以使用[科技列表],[我的科技]和[科技研发]指令，且仅在有科技研究所时科技效果才生效"}

    @staticmethod
    def get_by_id(id):
        for i in BuildModel:
            if i.value['id'] == id:
                return i
        return None

    @staticmethod
    def get_by_name(name):
        for i in BuildModel:
            if i.value['name'] == name:
                return i
        return None


class TechnologyModel(Enum):
    TRANSPARENT_TRADE = {"id": 201, "name": "透明交易", "sw": 3000, "gold": 30000, "time": 2,
                         "desc": "购买物品时可以先看物品再决定要不要买"}

    BRANCH_STORE = {"id": 202, "name": "道具分店", "sw": 1000, "gold": 30000, "time": 2,
                    "desc": "商店可以购物两次"}

    BATTLE_RADAR = {"id": 203, "name": "作战雷达", "sw": 20000, "gold": 250000, "time": 2,
                    "desc": "指挥部战力加成变为40%"}

    ARCHAEOLOGIST = {"id": 204, "name": "考古专家", "sw": 6000, "gold": 350000, "time": 3,
                     "desc": "藏宝图有更大的机会挖出更多的物品"}

    REFINING_TECHNOLOGY = {"id": 205, "name": "精致冶炼", "sw": 3500, "gold": 70000, "time": 2,
                           "desc": "装备工坊熔炼装备需求数量-1"}
    MONETARY_POLICY = {"id": 206, "name": "货币政策", "sw": 30000, "gold": 50000, "time": 4,
                       "desc": "贸易市场提供的金币增加50%"}

    MANIPULATION = {"id": 207, "name": "舆论操纵", "sw": 50000, "gold": 30000, "time": 4,
                    "desc": "报社提供的声望增加50%"}

    SATELLITE_CITY = {"id": 208, "name": "卫星城市", "sw": 80000, "gold": 750000, "time": 8,
                      "desc": "城市面积扩张到领地占比的1/8"}

    ROAD_PLANNING = {"id": 209, "name": "道路规划", "sw": 10000, "gold": 150000, "time": 2,
                     "desc": "拥堵状态阈值提高到90%"}

    SAND_FIX = {"id": 210, "name": "防风固沙", "sw": 5000, "gold": 30000, "time": 2,
                "desc": "提高沙尘天气的触发阈值"}

    @staticmethod
    def get_by_id(id):
        for i in TechnologyModel:
            if i.value['id'] == id:
                return i
        return None

    @staticmethod
    def get_by_name(name):
        for i in TechnologyModel:
            if i.value['name'] == name:
                return i
        return None


# 获取建筑情况
def check_build_counter(gid, uid, b_m: BuildModel):
    i_c = ItemCounter()
    return i_c._get_user_state(gid, uid, b_m.value['id'])


# 获取建筑情况
def check_technolog_counter(gid, uid, t_m: TechnologyModel):
    i_c = ItemCounter()
    return i_c._get_user_state(gid, uid, t_m.value['id'])
