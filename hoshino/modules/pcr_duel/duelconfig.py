import base64
import json
import math
from datetime import timedelta
from io import BytesIO

from PIL import Image

from hoshino import R
from hoshino.config import pcr_duel as cfg
from hoshino.util import DailyNumberLimiter
from . import duel_chara as chara
from .CECounter import *
from .DuelCounter import *
from .common_util import *

BLACKLIST_ID = [1000, 1072, 4031, 9000, 1069, 1073, 1907, 1910, 1913, 1914, 1915, 1916, 1917, 1919, 9601, 9602, 9603,
                9604]  # 黑名单ID
WAIT_TIME = 30  # 对战接受等待时间
WAIT_TIME_jy = 30  # 交易接受等待时间
DUEL_SUPPORT_TIME = 30  # 赌钱等待时间
from hoshino.config.__bot__ import BASE_DB_PATH

DB_PATH = os.path.expanduser(BASE_DB_PATH + "pcr_duel.db")

CARD_LEVEL_MAX = 100  # 女友等级上限

GECHA_DUNDCORE = 100  # 抽武器所需副本币

# 次数限制设置
SIGN_DAILY_LIMIT = 1  # 机器人每天签到的次数
DUEL_DAILY_LIMIT = 5  # 每个人每日发起决斗上限
DUN_DAILY_LIMIT = 5  # 每个人每日副本上限
BOSS_DAILY_LIMIT = 3  # 会战与世界boss次数
EQUIP_DAILY_LIMIT = 5  # 副本商城兑换次数
ZERO_GET_LIMIT = 3  # 没钱补给次数
GIFT_DAILY_LIMIT = 5  # 每日购买礼物次数上限
DATE_DAILY_LIMIT = 1  # 每天女友约会次数上限
MANAGE_DAILY_LIMIT = 1  # 每日城市结算次数
RECRUIT_DAILY_LIMIT = 5  # 每日招募女友次数

# 重置次数时间
RESET_HOUR = 5  # 每日使用次数的重置时间，0代表凌晨0点，1代表凌晨1点，以此类推

# 抽卡
GACHA_COST = 500  # 抽老婆需求
SHANGXIAN_NUM = 100000  # 增加女友上限所需金币
SHANGXIAN_SW = 2000  # 扩充女友上限，需要的声望值
WAREHOUSE_NUM = 10  # 仓库增加上限

# 补给
ZERO_GET_AMOUNT = 1000  # 没钱补给量
ZERO_GET_REQUIREMENT = 300  # 要求多少钱以下才能领补给

# 决斗
WinSWBasics = 400  # 赢了获得的基础声望
LoseSWBasics = 150  # 输了掉的基础声望
favor_reduce = 30  # 当输掉女友时，损失的好感度
WIN_NUM = 1  # 下注获胜赢得的倍率
Suo = 1  # 梭哈额外获取的金币倍率
WIN_EXP = 5000  # 决斗胜利获得经验
NTR_QUEEN_REWARD = 1000  # 命中妻子额外金币奖励
NTR_BIND_REWARD = 2000  # 命中绑定额外金币奖励
LOSS_QUEEN_PUNISH_SW = 300  # 输掉妻子惩罚声望
LOSS_BIND_PUNISH_SW = 500  # 输掉绑定惩罚声望
FULL_GIRL_COMPENSATE = 1000  # 满人获胜额外补偿金币
FAVOR_GIRL_COMPENSATE = 500  # 好感保护额外补偿金币

# 好感
PRINCESS_HEART_FAVOR = 10000  # 触发赠送公主之心的好感阈值
ETERNAL_LOVE_FAVOR = 30000  # 获取永恒爱恋好感度阈值
NEED_favor = 3000  # 成为妻子所需要的好感
NEED_score = 30000  # 成为妻子所需要的金币

# 功能开关
BREAK_UP_SWITCH = True  # 分手系统开关
Remake_allow = False  # 是否允许重开
Suo_allow = True  # 是否允许梭哈

# 交易
Zhuan_Need = 0.05  # 转账所需的手续费比例
Jiao_Need = 0.05  # 交易女友所需手续费比例
Suo_Ex_NEED = 0.5  # 开启梭哈时转账交易手续费比例
WAIT_TIME_CHANGE = 30  # 礼物交换等待时间

# 爵位
FILE_PATH = os.path.dirname(__file__)  # 用于加载dlcjson
LEVEL_GIRL_NEED = {
    "1": 1,
    "2": 3,
    "3": 5,
    "4": 7,
    "5": 9,
    "6": 11,
    "7": 13,
    "8": 15,
    "9": 17,
    "10": 20,
}  # 升级所需要的老婆，格式为["等级“: 需求]
LEVEL_COST_DICT = {
    "1": 0,
    "2": 2000,
    "3": 5000,
    "4": 10000,
    "5": 30000,
    "6": 50000,
    "7": 100000,
    "8": 200000,
    "9": 500000,
    "10": 1000000
}  # 升级所需要的钱钱，格式为["等级“: 需求]
LEVEL_SW_NEED = {
    "1": 0,
    "2": 100,
    "3": 500,
    "4": 1000,
    "5": 2000,
    "6": 3000,
    "7": 5000,
    "8": 10000,
    "9": 30000,
    "10": 50000,
}  # 升级所需要的声望，格式为["等级“: 需求]

LEVEL_FR_NEED = {
    "1": 0,
    "2": 0,
    "3": 0,
    "4": 10,
    "5": 50,
    "6": 100,
    "7": 200,
    "8": 300,
    "9": 500,
    "10": 800,
}  # 升级所需要的繁荣，格式为["等级“: 需求]

# 城市
LEVEL_HAVE_MANOR = {
    "1": 0,
    "2": 0,
    "3": 500,
    "4": 700,
    "5": 900,
    "6": 1100,
    "7": 1300,
    "8": 1500,
    "9": 1700,
    "10": 2000,
}
MANOR_INIT_GOLD = 30000  # 启动资金

# 这里是庆典设置区 ~~开关类，1为开，0为关~~
Show_Cele_Not = False  # 查询庆典时，显示未开放的庆典
# 金币庆典
Gold_Cele = 0  # 群庆典初始化时，是否开启金币庆典
Gold_Cele_Num = 2  # 金币庆典倍率，实际获得金币倍率为金币庆典倍率*基础倍率
# 签到庆典
QD_Cele = 0  # 群庆典初始化时，是否开启签到庆典
QD_Gold_Cele_Num = 2  # 签到庆典金币倍率
QD_SW_Cele_Num = 2  # 签到庆典声望倍率
# 梭哈庆典
Suo_Cele = 0  # 群庆典初始化时，是否开启梭哈倍率庆典
Suo_Cele_Num = 2  # 梭哈额外倍率，实际获得梭哈倍率为梭哈庆典倍率*基础倍率
# 免费招募庆典
FREE_DAILY = 0  # 群庆典初始化时，是否开启免费招募庆典
FREE_DAILY_LIMIT = 1  # 每天免费招募的次数
# 限时开放声望招募
SW_add = 0  # 群庆典初始化时，是否开启无限制等级声望招募

# 战斗
GJ_EXP_RATE = 20  # 挂机修炼获取经验倍率（每分钟）
MAX_RANK = 20  # 最大rank等级
RANK_LIST = {
    1: 5000,
    2: 10000,
    3: 15000,
    4: 20000,
    5: 25000,
    6: 30000,
    7: 35000,
    8: 40000,
    9: 45000,
    10: 50000,
    11: 100000,
    12: 200000,
    13: 300000,
    14: 400000,
    15: 500000,
    16: 600000,
    17: 700000,
    18: 800000,
    19: 900000,
    20: 1000000,
}  # rank升级要求，格式为["rank":金币]
MAX_STAR = 5  # 最大星级
STAR_LIST = {
    1: 30,
    2: 50,
    3: 80,
    4: 100,
    5: 150,
}  # 升星消耗

# 礼物
GIFT_DICT = {
    "玩偶": 0,
    "礼服": 1,
    "歌剧门票": 2,
    "水晶球": 3,
    "耳环": 4,
    "发饰": 5,
    "小裙子": 6,
    "热牛奶": 7,
    "书": 8,
    "鲜花": 9
}  # 礼物字典
GIFTCHOICE_DICT = {
    0: [0, 2, 1],
    1: [1, 0, 2],
    2: [2, 1, 0],
}  # 选择礼物字典

# 文案
RELATIONSHIP_DICT = {
    0: ["初见", "浣花溪上见卿卿，脸波明，黛眉轻。"],
    50: ["相识", "有美一人，清扬婉兮。邂逅相遇，适我愿兮。"],
    100: ["熟悉", "夕阳谁唤下楼梯，一握香荑。回头忍笑阶前立，总无语，也依依。"],
    300: ["朋友", "锦幄初温，兽烟不断，相对坐调笙。"],
    500: ["朦胧", "和羞走，倚门回首，却把青梅嗅。"],
    1000: ["喜欢", "夜月一帘幽梦，春风十里柔情。"],
    2000: ["依恋", "愿我如星君如月，夜夜流光相皎洁。"],
    3000: ["挚爱", "江山看不尽，最美镜中人。"]
}  # 好感文案
Gift10 = [
    "这个真的可以送给我吗，谢谢(害羞的低下了头)。",
    "你是专门为我准备的吗，你怎么知道我喜欢这个呀，谢谢你！",
    "啊，我最喜欢这个，真的谢谢你。"
]  # 最喜欢文案
Gift5 = [
    "谢谢送我这个，我很开心。",
    "这个我很喜欢，谢谢。",
    "你的礼物我都很喜欢哦，谢谢。"
]  # 喜欢文案
Gift2 = [
    "送我的吗，谢谢你。",
    "谢谢你的礼物。",
    "为我准备了礼物吗，谢谢。"
]  # 一般文案
Gift1 = [
    "不用为我特意准备礼物啦，不过还是谢谢你哦。",
    "嗯，谢谢。",
    "嗯，我收下了，谢谢你。"
]  # 不喜欢文案
Addgirlfail = [
    # '你参加了一场舞会，热闹的舞会场今天竟然没人同你跳舞。',
    # '你邀请到了心仪的女友跳舞，可是跳舞时却踩掉了她的鞋，她生气的离开了。',
    # '你为这次舞会准备了很久，结果一不小心在桌子上睡着了，醒来时只看到了过期的邀请函。',
    # '你参加了一场舞会，可是舞会上只有一名男性向你一直眨眼。',
    # '你准备参加一场舞会，可惜因为忘记穿礼服，被拦在了门外。',
    # '你沉浸在舞会的美食之中，忘了此行的目的。',
    # '你本准备参加舞会，却被会长拉去出了一晚上刀。',
    # '舞会上你和另一个贵族发生了争吵，你一拳打破了他的鼻子，两人都被请出了舞会。',
    # '舞会上你很快约到了一名女伴跳舞，但是她不是你喜欢的类型。',
    # '你约到了一位心仪的女伴，但是她拒绝了与你回家，说想再给你一个考验。',
    # '你和另一位贵族同时看中了一个女孩，但是在三人交谈时，你渐渐的失去了话题。',
    '舞会开始了，但是没有一人看向你。你的心情很失落，悄悄地离开了。',
    '本来想在舞会上表演魔术的你被人当场拆穿，恼怒的你和他打了起来。你们被请出了舞会。',
    '你对一位女孩一见钟情，在舞会上对她展开了疯狂的追求。但是她觉得你太花心，拒绝了你的邀请。',
    '舞会上你碰见了曾经的女友，她一脸惊讶的看着你。你狼狈的跑了出去。',
]  # 舞会失败文案
Addgirlsuccess = [
    # '你参加了一场舞会，你优雅的舞姿让每位年轻女孩都望向了你。',
    # '你参加了一场舞会，你的帅气使你成为了舞会的宠儿。',
    # '你在舞会门口就遇到了一位女孩，你挽着她的手走进了舞会。',
    # '你在舞会的闲聊中无意中谈到了自己显赫的家室，你成为了舞会的宠儿。',
    # '没有人比你更懂舞会，每一个女孩都为你的风度倾倒。',
    # '舞会上你没有约到女伴，但是舞会后却有个女孩偷偷跟着你回了家。',
    # '舞会上你和另一个贵族发生了争吵，一位女孩站出来为你撑腰，你第一次的注意到了这个可爱的女孩。',
    # '你强壮的体魄让女孩们赞叹不已，她们纷纷来问你是不是一位军官。',
    # '你擅长在舞会上温柔地对待每一个人，女孩们也向你投来了爱意。',
    # '一个可爱的女孩一直在舞会上望着你，你犹豫了一会，向她发出了邀请。',
    '在舞会上，你优雅的舞姿吸引了一个女孩，她向你走了过来。',
    '你预先做的准备很成功，在舞会上你约到了一位十分美丽的女孩。',
    '一个可爱的女孩一直在舞会上偷偷望着你，你心中一动，向她发出了邀请。',
    '舞会十分的热闹，你没有找到机会，只得离开。但有一位少女跟着你走了出来',
]  # 舞会成功文案
Login100 = [
    '今天是练习击剑的一天，不过你感觉你的剑法毫无提升。',
    '优雅的贵族从不晚起，可是你今天一直睡到了中午。',
    '今天你点了一份豪华的午餐却忘记了带钱，窘迫的你毫无贵族的姿态。',
    '今天你在路上看上了别人的女友，却没有鼓起勇气向他决斗。',
    '今天你十分抑郁，因为发现自己最近上升的只有体重。'
]  # 签到失败文案
Login200 = [
    '今天是练习击剑的一天，你感觉到了你的剑法有所提升。',
    '早起的你站在镜子前许久，天底下竟然有人可以这么帅气。',
    '今天你搞到了一瓶不错的红酒，你的酒窖又多了一件存货。',
    '今天巡视城市时，一个小孩子崇拜地望着你，你感觉十分开心。',
    '今天一个朋友送你一张音乐会的门票，你打算邀请你的女友同去。',
    '今天一位国王的女友在路上向你抛媚眼，也许这就是个人魅力吧。'
]  # 正常签到文案
Login300 = [
    '今天是练习击剑的一天，你感觉到了你的剑法大有长进。',
    '今天你救下了一个落水的小孩，他的家人说什么也要你收下一份心意。',
    '今天你巡视城市时，听到几个小女孩说想长大嫁给帅气的领主，你心里高兴极了。',
    '今天你打猎时猎到了一只鹿，你骄傲的把鹿角加入了收藏。',
    '今天你得到了一匹不错的马，说不定可以送去比赛。'
]  # 成功签到文案
Login600 = [
    '今天是练习击剑的一天，你觉得自己已经可谓是当世剑圣。',
    '今天你因为城市治理有方，获得了皇帝的嘉奖。',
    '今天你的一位叔叔去世了，无儿无女的他，留给了你一大笔遗产。',
    '今天你在比武大会上获得了优胜，获得了全场的喝彩。',
    '今天你名下的马夺得了赛马的冠军，你感到无比的自豪。'
]  # 大成功签到文案
LoginMorning = [
    '{女友}:早安。美好的一起从早起开始，别赖床了。早餐已经做好了哦。\n你艰难的在床上翻了个身，睡眼朦胧的起来了。',
    '{女友}:啦啦啦啦，啦啦啦——。\n你在梦中感觉身体十分的沉重，隐约听见一阵歌声在耳边徘徊。睁开眼发现，{女友}正在看着你，停止歌声微微一笑，早上好。',
    '{女友}:哈～早安，今天起得这么早啊。\n她揉了揉眼睛了，有点惊讶的看着站在厨房的你。你笑了笑，觉得一直被照顾有点不好意思，所以今天打算自己做。',
    '{女友}:早安，亲爱的，该起床了哦。\n你被一阵香气吸引睁开了眼睛，发现床边放着一顿冒着热气的早餐，而她正坐在床边一脸微笑的看着你。',
]
LoginNoon = [
    '走出家门，刺眼的阳光一下照了过来。{女友}撑起阳伞走到了你的身边。\n{女友}:午安，达令。要一起喝杯下午茶吗？',
    '{女友}:午安，今天的天气很不错呢。要一起出去逛逛吗？\n你点了点头，和{女友}手牵手出门度过了一个愉快的下午。',
    '{女友}:午安！亲爱的。\n正走在路上的你感觉背后一沉，就听见了一个熟悉的声音。一支冰淇淋被送到了你的嘴边。\n{女友}:尝尝吧，很好吃的。\n你吃了一口冰淇淋，之后和她在街上闲逛了起来。',
    '{女友}:午安，亲爱的，辛苦了。\n你正坐在桌前办公。{女友}走了过来，将茶点放在了桌上。走到你的背后帮你揉起了肩膀。你的心情慢慢舒缓了下来。',
]
LoginNight = [
    '夜深了，白天的一切喧闹都沉静了下来。你独自一人走在院子里，突然看见了一个美妙的背影，她转过身来，看见你后露出了微笑。\n{女友}:晚上好，要一起看月亮吗？',
    '{女友}:亲爱的，夜深了。该休息了。\n夜晚，{女友}来到了书房里，看见还在工作的你，鼓起了脸颊。抢过你手中的文件，推着你回到了卧室。',
    '{女友}:今晚月色真美，亲爱的。\n你和{女友}手牵手躺在屋顶，一起仰望着美丽的星空。你想到，今晚，注定是一个美妙的夜晚。',

]
Date5 = [
    '你比约会的时间晚到了十分钟，嘟着嘴的她看起来不太满意。',
    '一向善于言辞的你，今天的约会却不时冷场，她看起来不是很开心。',
    '今天的约会上你频频打哈欠，被她瞪了好几次，早知道昨晚不该晚睡的。',
    '“为您旁边的这个姐姐买朵花吧。”你们被卖花的男孩拦下，你本想买花却发现自己忘记了带钱，她看起来不是很开心。'
]  # 约会失败文案
Date10 = [
    '你带她去熟悉的餐厅吃饭，她觉得今天过得很开心。',
    '你带她去看了一场马术表演，并约她找机会一起骑马出去，她愉快的答应了。',
    '“为您旁边的这个姐姐买朵花吧。”你们被卖花的男孩拦下，你买了一束花还给了小孩一笔小费，你的女友看起来很开心。',
    '你邀请她去看一场歌剧，歌剧中她不时微笑，看起来十分开心。'
]  # 约会一般文案
Date15 = [
    '你和她一同骑马出行，两个人一同去了很多地方，度过了愉快的一天。',
    '你新定做了一件最新款的礼服，约会中她称赞你比往常更加帅气。',
    '你邀请她共赴一场宴会，宴会上你们无所不谈，彼此间的了解增加了。',
    '你邀请她去看一场歌剧，歌剧中她一直轻轻地握着你的手。'
]  # 约会成功文案
Date20 = [
    '你邀请她共赴一场宴会，宴会中她亲吻了你的脸颊后，害羞的低下了头，这必然是你和她难忘的一天。',
    '约会中你们被一群暴民劫路，你为了保护她手臂受了伤。之后她心疼的抱住了你，并为你包扎了伤口。',
    '你邀请她去看你的赛马比赛，你骑着爱马轻松了夺取了第一名，冲过终点后，你大声地向着看台喊出了她的名字，她红着脸低下了头。',
    '你和她共同参加了一场盛大的舞会，两人的舞步轻盈而优雅，被评为了舞会第一名，上台时你注视着微笑的她，觉得她今天真是美极了。'
]  # 约会大成功文案

# 加载dlc开关
cfg.load_dlc_switch()
# 加载时装列表
cfg.refresh_fashion()
# 刷新dlc-角色 dlc-介绍配置
cfg.refresh_config()
# 检查dlcswitch是否有漏加的新dlc
cfg.check_dlc()


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


daily_zero_get_limiter = DailyAmountLimiter("zero_get", ZERO_GET_LIMIT, RESET_HOUR)
daily_sign_limiter = DailyAmountLimiter("sign", SIGN_DAILY_LIMIT, RESET_HOUR)
daily_free_limiter = DailyAmountLimiter("free", FREE_DAILY_LIMIT, RESET_HOUR)
daily_duel_limiter = DailyAmountLimiter("duel", DUEL_DAILY_LIMIT, RESET_HOUR)
daily_date_limiter = DailyAmountLimiter("date", DATE_DAILY_LIMIT, RESET_HOUR)
daily_gift_limiter = DailyAmountLimiter("gift", GIFT_DAILY_LIMIT, RESET_HOUR)
daily_dun_limiter = DailyAmountLimiter("dun", DUN_DAILY_LIMIT, RESET_HOUR)
daily_boss_limiter = DailyAmountLimiter("boss", BOSS_DAILY_LIMIT, RESET_HOUR)
daily_equip_limiter = DailyAmountLimiter("equip", EQUIP_DAILY_LIMIT, RESET_HOUR)
daily_manor_limiter = DailyAmountLimiter("manor", MANAGE_DAILY_LIMIT, RESET_HOUR)
daily_recruit_limiter = DailyAmountLimiter("recruit", RECRUIT_DAILY_LIMIT, RESET_HOUR)


# 生成没被约过的角色列表
def get_newgirl_list(gid):
    chara_id_list = list(cfg.chara_info.keys())
    duel = DuelCounter()
    old_list = duel._get_card_list(gid)
    dlc_blacklist = get_dlc_blacklist(gid)
    new_list = []
    for card in chara_id_list:
        card = int(card)
        if card not in BLACKLIST_ID and card not in old_list and card not in dlc_blacklist:
            new_list.append(card)
    return new_list


# 增加角色经验
def add_exp(gid, uid, cid, exp):
    CE = CECounter()
    zslevel = CE._get_zhuansheng(gid, uid, cid)
    if zslevel > 0:
        expzf = 1 + ((zslevel + zslevel - 1) / 10)
    else:
        expzf = 1
    now_level = CE._get_card_level(gid, uid, cid)
    level_flag = 0
    need_exp = math.ceil((now_level + 1) * 100 * expzf)
    exp_info = CE._get_card_exp(gid, uid, cid)
    now_exp = exp_info + exp
    if now_level >= CARD_LEVEL_MAX:
        level_flag = 1
        last_exp = now_exp
        now_exp = 0
    while now_exp >= need_exp:
        now_level = now_level + 1
        now_exp = now_exp - need_exp
        need_exp = math.ceil((now_level + 1) * 100 * expzf)
        if now_level >= CARD_LEVEL_MAX:
            level_flag = 1
            last_exp = now_exp
            now_exp = 0
            break
    if level_flag == 1:
        CE._add_card_exp(gid, uid, cid, now_level, now_exp)
        CE._add_exp_chizi(gid, uid, last_exp)
        msg = f"目前等级为{now_level}，由于超出等级上限，{last_exp}点经验加入经验池"
        return [1, last_exp, msg]
    else:
        CE._add_card_exp(gid, uid, cid, now_level, now_exp)
        msg = f"目前等级为{now_level}"
        return [0, now_level, msg]


# 返回好感对应的关系和文本
def get_relationship(favor):
    for relation in RELATIONSHIP_DICT.keys():
        if favor >= relation:
            relationship = RELATIONSHIP_DICT[relation]
    return relationship[0], relationship[1]


# 取得该群未开启的dlc所形成的黑名单
def get_dlc_blacklist(gid):
    dlc_blacklist = []
    for dlc in cfg.dlcdict.keys():
        if gid not in cfg.dlc_switch[dlc]:
            dlc_blacklist += cfg.dlcdict[dlc]
    return dlc_blacklist


# 随机获得一件装备并返回获得信息
def add_equip_info(gid, uid, level, down_list):
    CE = CECounter()
    # 加载装备列表
    with open(os.path.join(FILE_PATH, 'equipment.json'), 'r', encoding='UTF-8') as fa:
        equiplist = json.load(fa, strict=False)
    equiplistinfo = []
    for equiplevel in equiplist:
        if str(level) == str(equiplist[equiplevel]['level']):
            equiplistinfo = equiplist[equiplevel]
            break
    equipid = random.sample(down_list, 1)
    equipinfo = []
    for eid in equiplistinfo['e_list']:
        if str(equipid[0]) == str(equiplistinfo['e_list'][eid]['eid']):
            equipinfo = equiplistinfo['e_list'][eid]
            equipinfo['model'] = equiplistinfo['model']
            CE._add_equip(gid, uid, equipid[0], 1)
            break
    return equipinfo


# 根据装备名称获取装备信息
def get_equip_info_name(ename):
    equiplist = {}
    with open(os.path.join(FILE_PATH, 'equipment.json'), 'r', encoding='UTF-8') as fa:
        equiplist = json.load(fa, strict=False)
    equipinfo = []
    fand_flag = 0
    for i in equiplist:
        if fand_flag == 1:
            break
        for j in equiplist[i]['e_list']:
            if str(ename) == str(equiplist[i]['e_list'][j]['name']):
                equipinfo = equiplist[i]['e_list'][j]
                equipinfo['model'] = equiplist[i]['model']
                equipinfo['icon'] = get_equip_icon(equiplist[i]['e_list'][j]['eid'])
                fand_flag = 1
                break
    return equipinfo


# 抽卡
def get_gecha_equip(gid, uid, gechanum, xnum, dnum, unum, gechainfo):
    equip_list = ''
    CE = CECounter()
    xingchenlist = {
        1: 1,
        2: 1,
        3: 2,
        4: 5,
        5: 10,
        6: 20,
    }
    get_xcz = 0
    for i in range(gechanum):
        xnum = xnum + 1
        dnum = dnum + 1
        unum = unum + 1
        # 获取本次抽卡类型
        if unum == int(gechainfo['up_num']):
            # 抽大保底
            charinfo = gechainfo['ugecha']
        elif dnum == 100:
            # 抽10连小保底
            charinfo = gechainfo['dgecha']
        elif xnum == 10:
            # 抽10连小保底
            charinfo = gechainfo['xgecha']
        else:
            # 普通抽卡
            charinfo = gechainfo['gecha']

        equip_type_run = int(math.floor(random.uniform(1, 100)))
        get_equip_quality = 1
        z_equip_quality = 0
        for gechalevel in charinfo['quality']:
            z_equip_quality = z_equip_quality + charinfo['quality'][gechalevel]
            if z_equip_quality >= equip_type_run:
                get_equip_quality = int(gechalevel)
                break
        down_list = []
        for equip_down in charinfo['equip']:
            if int(get_equip_quality) == int(equip_down):
                down_list = charinfo['equip'][equip_down]
        if get_equip_quality == 5:
            xnum = 0
            dnum = 0
            unum = 0
        elif get_equip_quality == 4:
            xnum = 0
            dnum = 0
        elif get_equip_quality == 3:
            xnum = 0
        # 随机获得一个品质的装备
        equip_info = add_equip_info(gid, uid, get_equip_quality, down_list)
        get_xc = xingchenlist[get_equip_quality]
        get_xcz = get_xcz + get_xc
        # print(equip_info)
        equip_list = equip_list + f"\n{equip_info['model']}品质{equip_info['type']}:{equip_info['name']}"
    now_num = CE._add_xingchen_num(gid, uid, get_xcz)
    CE._add_gecha_num(gid, uid, xnum, dnum, unum)
    msg = f"{equip_list}\n您总共获得了{get_xcz}星尘，目前星尘数量为{now_num}个\n300个星尘可以兑换本期UP的UR装备哦"
    return msg


# 获取蛋池信息
def get_gecha_info(gechaname):
    gechalist = {}
    with open(os.path.join(FILE_PATH, 'equipgecha.json'), 'r', encoding='UTF-8') as fa:
        gechalist = json.load(fa, strict=False)
    gechainfo = []
    for gecha in gechalist:
        if str(gechaname) == str(gechalist[gecha]['name']):
            gechainfo = gechalist[gecha]
            break
    return gechainfo


# 返回boss图片
def get_boss_icon(bossname):
    PIC_PATH = os.path.join(FILE_PATH, 'boss')
    path = os.path.join(PIC_PATH, f'{bossname}.JPG')
    mes = ''
    if os.path.exists(path):
        img = Image.open(path)
        bio = BytesIO()
        img.save(bio, format='JPEG')
        base64_str = 'base64://' + base64.b64encode(bio.getvalue()).decode()
        mes = f"[CQ:image,file={base64_str}]"
    return mes


def get_equip_icon(eid):
    PIC_PATH = os.path.join(FILE_PATH, 'equpimg')
    path = os.path.join(PIC_PATH, f'{eid}.png')
    mes = ''
    if os.path.exists(path):
        img = Image.open(path)
        size = img.size
        sf_weight = math.ceil(size[0] / (size[1] / 60))
        img = img.resize((sf_weight, 60))
        bio = BytesIO()
        img.save(bio, format='PNG')
        base64_str = 'base64://' + base64.b64encode(bio.getvalue()).decode()
        mes = f"[CQ:image,file={base64_str}]"
    return mes


def get_nextbossinfo(zhoumu, bossid, shijieflag):
    bosslist = {}
    with open(os.path.join(FILE_PATH, 'bossinfo.json'), 'r', encoding='UTF-8') as fa:
        bosslist = json.load(fa, strict=False)
    bossinfo = []
    for x in bosslist:
        if zhoumu in bosslist[x]['zhoumu']:
            for j in bosslist[x]['bosslist']:
                if str(bossid) == str(bosslist[x]['bosslist'][j]['bossid']):
                    bossinfo = bosslist[x]['bosslist'][j]
                    bossinfo['zhoumu'] = zhoumu
                    bossinfo['icon'] = get_boss_icon(bosslist[x]['bosslist'][j]['name'])
                    if shijieflag == 1:
                        bossinfo['hp'] = bossinfo['hp'] * 10
                    break
    return bossinfo


# 获取当前群的boss状态
def get_boss_info(gid):
    CE = CECounter()
    bosslist = {}
    with open(os.path.join(FILE_PATH, 'bossinfo.json'), 'r', encoding='UTF-8') as fa:
        bosslist = json.load(fa, strict=False)
    bossinfo = []
    # 此处写数据库查询boss信息
    # print('群id:'+str(gid))
    nowinfo = CE._get_bossinfo(gid)
    # print(nowinfo)
    for x in bosslist:
        if nowinfo[0] in bosslist[x]['zhoumu']:
            for j in bosslist[x]['bosslist']:
                if str(nowinfo[1]) == str(bosslist[x]['bosslist'][j]['bossid']):
                    bossinfo = bosslist[x]['bosslist'][j]
                    bossinfo['zhoumu'] = nowinfo[0]
                    bossinfo['icon'] = get_boss_icon(bosslist[x]['bosslist'][j]['name'])
                    if nowinfo[2] > 0:
                        bossinfo['hp'] = nowinfo[2]
                    else:
                        if gid == 999:
                            bossinfo['hp'] = bossinfo['hp'] * 10

                    break
    return bossinfo


# 根据装备id获取装备信息
def get_equip_info_id(eid):
    equiplist = {}
    with open(os.path.join(FILE_PATH, 'equipment.json'), 'r', encoding='UTF-8') as fa:
        equiplist = json.load(fa, strict=False)
    equipinfo = []
    fand_flag = 0
    for i in equiplist:
        if fand_flag == 1:
            break
        for j in equiplist[i]['e_list']:
            if str(eid) == str(equiplist[i]['e_list'][j]['eid']):
                equipinfo = equiplist[i]['e_list'][j]
                equipinfo['model'] = equiplist[i]['model']
                equipinfo['icon'] = get_equip_icon(equiplist[i]['e_list'][j]['eid'])
                fand_flag = 1
                break
    return equipinfo


# 查询单角色战斗能力
def get_card_battle_info(gid, uid, cid):
    ce = get_card_ce(gid, uid, cid)
    # 基础分配
    hp = ce
    atk = ce / 10
    # 计算攻守偏移
    base = hashval(str(cid), 50)
    atk_pian = 1 + (25 - base) / 100
    hp_pian = 1 + (base - 25) / 100
    hp = int(hp * hp_pian)
    atk = int(atk * atk_pian)
    # 计算性格加成
    if check_have_character(cid, "勇敢"):
        atk = int(atk * 1.1)
    if check_have_character(cid, "慎重"):
        hp = int(hp * 1.1)
    return hp, atk


# 查询单角色战力
def get_card_ce(gid, uid, cid):
    duel = DuelCounter()
    CE = CECounter()
    # 获取角色时装穿戴信息
    up_info = duel._get_fashionup(gid, uid, cid, 0)
    fashion_ce = 0
    if up_info:
        # 获取穿戴时装所加的战斗力
        fashion_info = get_fashion_info(up_info)
        fashion_ce = fashion_info['add_ce'] * 10
    # 获取角色等级
    zslevel = CE._get_zhuansheng(gid, uid, cid)
    zljcadd = zslevel * 30
    if zslevel > 0:
        zlzf = 1 + ((zslevel + zslevel - 1) / 10)
    else:
        zlzf = 1
    level_info = CE._get_card_level(gid, uid, cid)
    if get_weather(gid) == WeatherModel.SHUYU:
        level_info = 200
    level_ce = level_info * 50 + level_info * zljcadd
    favor = duel._get_favor(gid, uid, cid)
    # 获取角色穿戴装备列表
    equip_ce = 0
    equip_start_buff = 0
    dreeslist = CE._get_dress_list(gid, uid, cid)
    for eid in dreeslist:
        equipinfo = get_equip_info_id(eid)
        if equipinfo:
            equip_start_buff += int(equipinfo['level'])
            if equipinfo['type_id'] == 99:
                if equipinfo['eid'] == 9999:
                    favor_jc = math.ceil(favor / 2500)
                    if favor_jc == 0:
                        favor_jc = 1
                    if favor_jc > 10:
                        favor_jc = 10
                    equip_ce = equip_ce + equipinfo['add_ce'] * favor_jc
                elif equipinfo['eid'] == 10000:
                    zhuans_jc = zslevel
                    if zhuans_jc == 0:
                        zhuans_jc = 1
                    if zslevel > 5:
                        zhuans_jc = 5
                    equip_ce = equip_ce + equipinfo['add_ce'] * zhuans_jc
            else:
                equip_ce = equip_ce + equipinfo['add_ce']
    # 获取角色好感信息

    # 计算角色好感战力加成
    favor_ce = math.ceil(favor / 500 * 200)
    # 获取角色星级
    cardstar = CE._get_cardstar(gid, uid, cid)
    starz = 0
    n = 0
    while n <= cardstar:
        starz += n
        n += 1
    addsrat = 1 + starz / 10
    equip_start_buff = 1 + equip_start_buff / 100
    # 计算角色rank战力加成
    rank = CE._get_rank(gid, uid, cid)
    card_ce = math.ceil(
        (100 + fashion_ce + level_ce * addsrat + favor_ce + equip_ce) * equip_start_buff * (1 + rank / 8) * zlzf)
    if duel._get_queen_owner(gid, cid) != 0:
        item = get_item_by_name("永恒爱恋")
        num = check_have_item(gid, uid, item)
        if num:
            card_ce = int(card_ce * 1.3)
    return card_ce


# 获取战力排行榜
def get_power_rank(gid):
    duel = DuelCounter()
    CE = CECounter()
    girls = CE._get_cards_byrank(gid, 50)
    if len(girls) > 0:
        data = sorted(girls, key=lambda cus: cus[1], reverse=True)
        new_data = []
        for girl_data in data:
            gid1, rank, uid, cid = girl_data
            gpower = get_card_ce(gid1, uid, cid)
            new_data.append((rank, gpower, uid, cid))
        rankData = sorted(new_data, key=lambda cus: cus[1], reverse=True)
        return rankData
    else:
        return []


# 取爵位名
def get_noblename(level: int):
    namedict = {
        "1": "平民",
        "2": "骑士",
        "3": "准男爵",
        "4": "男爵",
        "5": "子爵",
        "6": "伯爵",
        "7": "侯爵",
        "8": "公爵",
        "9": "国王",
        "10": "皇帝",
    }
    return namedict[str(level)]


# 返回副本信息
def get_dun_info(dunname):
    # 加载副本列表
    dungeonlist = {}
    with open(os.path.join(FILE_PATH, 'dungeon.json'), 'r', encoding='UTF-8') as fa:
        dungeonlist = json.load(fa, strict=False)
    dungeoninfo = []
    findnum = 0
    for dungeon in dungeonlist:
        if str(dunname) == str(dungeonlist[dungeon]['name']):
            dungeoninfo = dungeonlist[dungeon]
            findnum = 1
            break
    if findnum == 1:
        return dungeoninfo
    else:
        return ''


# 返回角色时装立绘
def get_fashion_icon(fid):
    return str(R.img(f'dlc/fashion/{fid}.jpg').cqcode)


# 返回角色时装列表
def get_fashion(cid):
    returnfashion = []
    for fashion in cfg.fashionlist:
        if str(cid) == str(cfg.fashionlist[fashion]['cid']):
            fashioninfo = cfg.fashionlist[fashion]
            fashioninfo['icon'] = get_fashion_icon(cfg.fashionlist[fashion]['fid'])
            returnfashion.append(fashioninfo)
    return returnfashion


# 返回时装信息
def get_fashion_buy(fname):
    fashioninfo = []
    for fashion in cfg.fashionlist:
        if str(fname) == str(cfg.fashionlist[fashion]['name']):
            fashioninfo = cfg.fashionlist[fashion]
            fashioninfo['icon'] = get_fashion_icon(cfg.fashionlist[fashion]['fid'])
            return fashioninfo
    return fashioninfo


# 返回时装信息
def get_fashion_info(fid):
    fashioninfo = []
    for fashion in cfg.fashionlist:
        if str(fid) == str(cfg.fashionlist[fashion]['fid']):
            fashioninfo = cfg.fashionlist[fashion]
            fashioninfo['icon'] = get_fashion_icon(cfg.fashionlist[fashion]['fid'])
            return fashioninfo
    return fashioninfo


# 返回爵位对应的女友数
def get_girlnum(level: int):
    numdict = LEVEL_GIRL_NEED
    return numdict[str(level)]


# 返回对应的女友上限
def get_girlnum_buy(gid, uid):
    numdict = LEVEL_GIRL_NEED
    duel = DuelCounter()
    level = duel._get_level(gid, uid)
    num = duel._get_warehouse(gid, uid)
    housenum = int(numdict[str(level)]) + num
    return housenum


# 返回升级到爵位所需要的金币数
def get_noblescore(level: int):
    numdict = LEVEL_COST_DICT
    return numdict[str(level)]


# 返回升级到爵位所需要的声望数
def get_noblesw(level: int):
    numdict = LEVEL_SW_NEED
    return numdict[str(level)]


def get_noblefr(level: int):
    numdict = LEVEL_FR_NEED
    return numdict[str(level)]


# 判断当前女友数是否大于于上限
def girl_outlimit(gid, uid):
    duel = DuelCounter()
    level = duel._get_level(gid, uid)
    girlnum = get_girlnum_buy(gid, uid)
    cidlist = duel._get_cards(gid, uid)
    cidnum = len(cidlist)
    if cidnum > girlnum:
        return True
    else:
        return False


# 魔改图片拼接
def concat_pic(pics, border=0):
    num = len(pics)
    w = pics[0].size[0]
    h_sum = 0
    for pic in pics:
        h_sum += pic.size[1]
    des = Image.new('RGBA', (w, h_sum + (num - 1) * border), (255, 255, 255, 255))
    h = 0
    for i, pic in enumerate(pics):
        des.paste(pic, (0, (h + i * border)), pic)
        h += pic.size[1]
    return des


def get_nv_icon_with_fashion(gid, uid, cid):
    duel = DuelCounter()
    up_info = duel._get_fashionup(gid, uid, cid, 0)
    if up_info:
        fashion_info = get_fashion_info(up_info)
        return fashion_info['icon']
    else:
        return get_nv_icon(cid)


def get_nv_icon(cid):
    c = chara.fromid(cid)
    mes = c.icon.cqcode
    PIC_PATH = R.img('dlc/full').path
    path = os.path.join(PIC_PATH, f'{cid}31.png')
    if os.path.exists(path):
        mes = str(R.img(f'dlc/full/{cid}31.png').cqcode)
    return mes


# 根据角色id和礼物id，返回增加的好感和文本
def check_gift(cid, giftid):
    lastnum = cid % 10
    if lastnum == giftid:
        favor = 20
        text = random.choice(Gift10)
        return favor, text
    num1 = lastnum % 3
    num2 = giftid % 3
    choicelist = GIFTCHOICE_DICT[num1]

    if num2 == choicelist[0]:
        favor = 10
        text = random.choice(Gift5)
        return favor, text
    if num2 == choicelist[1]:
        favor = 5
        text = random.choice(Gift2)
        return favor, text
    if num2 == choicelist[2]:
        favor = 1
        text = random.choice(Gift1)
        return favor, text


async def get_user_card_dict(bot, group_id):
    mlist = await bot.get_group_member_list(group_id=group_id)
    d = {}
    for m in mlist:
        d[m['user_id']] = m['card'] if m['card'] != '' else m['nickname']
    return d


def uid2card(uid, user_card_dict):
    return str(uid) if uid not in user_card_dict.keys() else user_card_dict[uid]


# 爵位等级获取城市面积
def get_all_manor(level):
    return LEVEL_HAVE_MANOR.get(str(level))


# 获取城市面积
def get_city_manor(gid, uid, level):
    if check_technolog_counter(gid, uid, TechnologyModel.SATELLITE_CITY):
        local = int(get_all_manor(level) * 0.125)
    else:
        local = int(get_all_manor(level) * 0.1)
    item = get_item_by_name("帝王法令")
    if check_have_item(gid, uid, item):
        local += 50
    return local


# 获取耕地面积
def get_geng_manor(gid, uid, level, geng):
    return int((get_all_manor(level) - get_city_manor(gid, uid, level)) * (geng / 100))


# 获取耕地税率
def get_geng_profit(gid, uid):
    return get_user_counter(gid, uid, UserModel.TAX_RATIO)


# 获取上缴税费
def get_taxes(gid, uid, level):
    return 2000 + 3000 * level


# 获取建筑情况
def get_all_build_counter(gid, uid):
    i_c = ItemCounter()
    info = i_c._get_build_info(gid, uid)
    build_num_map = {}
    for i in info:
        b_m = BuildModel.get_by_id(i[0])
        build_num_map[b_m] = i[1]
    return build_num_map
