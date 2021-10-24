import base64
import json
import math
import random
from datetime import timedelta
from io import BytesIO
import hashlib
from PIL import Image
from hoshino import R
from hoshino.config import pcr_duel as cfg
from hoshino.util import DailyNumberLimiter
from . import duel_chara as chara
from .CECounter import *
from .DuelCounter import *
from .ItemCounter import *

BLACKLIST_ID = [1000, 1072, 4031, 9000, 1069, 1073, 1907, 1910, 1913, 1914, 1915, 1916, 1917, 1919, 9601, 9602, 9603,
                9604]  # 黑名单ID
WAIT_TIME = 30  # 对战接受等待时间
WAIT_TIME_jy = 30  # 交易接受等待时间
DUEL_SUPPORT_TIME = 30  # 赌钱等待时间
from hoshino.config.__bot__ import BASE_DB_PATH

DB_PATH = os.path.expanduser(BASE_DB_PATH + "pcr_duel.db")

CARD_LEVEL_MAX = 50  # 女友等级上限

GECHA_DUNDCORE = 10  # 抽武器所需副本币

# 次数限制设置
SIGN_DAILY_LIMIT = 1  # 机器人每天签到的次数
DUEL_DAILY_LIMIT = 5  # 每个人每日发起决斗上限
DUN_DAILY_LIMIT = 1  # 每个人每日副本上限
STAGE_DAILY_LIMIT = 5  # 每个人每日关卡上限
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
WIN_EXP = 5  # 决斗胜利获得经验
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
Zhuan_Need = 0.1  # 转账所需的手续费比例
Jiao_Need = 0.1  # 交易女友所需手续费比例
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
GJ_EXP_RATE = 5  # 挂机修炼获取经验倍率（每小时）
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
    1: 50,
    2: 100,
    3: 200,
    4: 500,
    5: 800,
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

# 装备等级限制
EquipLevelLimit = {
    1: 0,
    2: 10,
    3: 20,
    4: 30,
    5: 40,
    6: 50,
}

# 分解得尘数
FenjieGet = {
    1: 1,
    2: 2,
    3: 5,
    4: 15,
    5: 30,
    6: 100,
}

# 角色性格
character = {
    "傲娇": "副本资源获取量+10% sp+1",
    "温柔": "队伍回复率增加5% 场外:增加1%",
    "勤奋": "修炼经验获取增加 副本获胜时5%概率触发恢复一次副本次数 更容易发现新道路",
    "坦率": "更容易触发彩蛋，更容易提高好感度",
    "勇敢": "个体atk增加10%",
    "固执": "队伍hp增加5% 场外:增加1%",
    "悠闲": "弱化敌人5%atk ",
    "淘气": "队伍连击率增加5% 场外:增加1%",
    "元气": "队伍闪避率增加5% 场外:增加1%",
    "弱气": "敌方不能够触发暴击 场外:队伍增加该角色10%的hp",
    "天然": "队伍暴击率增加5% 场外:增加1%",
    "毒舌": "敌方不能够触发回复 场外:队伍增加该角色10%的atk",
    "冷静": "队伍全属性提高1%",
    "自大": "队伍atk力增加5% 更难增加好感 场外:增加1%",
    "慎重": "个体hp增加10%",
    "病娇": "队伍boost率增加5% 不会被抢走 不能够分手 场外:增加1%",
    "无口": "敌方触发增益的概率降低20% ",
    "腹黑": "扣除对方5%血量"
}

ITEM_INFO = {
    "1": {
        "id": "1",
        "name": "天命之子",
        "rank": "S",
        "desc": "无视100的等级上限 为自己的女友增加10级 最高不超过200级(仅100满级以上可以使用)",
    },
    "2": {
        "id": "2",
        "name": "后宫之证",
        "rank": "S",
        "desc": "可以执行一次增加女友上限指令",
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
        "rank": "S",
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
        "name": "帝王法令",
        "rank": "EX",
        "desc": "无需使用，当持有帝王法令时城市面积计算增加50",
    },
    "8": {
        "id": "8",
        "name": "咲夜怀表",
        "rank": "A",
        "desc": "使用后刷新自己的副本 签到 低保 约会 决斗 礼物 boss次数",
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
        "desc": "使用后刷新持续恢复副本和决斗次数",
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
        "name": "蓝药水",
        "rank": "D",
        "desc": "使用后sp上限临时增加10点",
    },
    "16": {
        "id": "16",
        "name": "战斗记忆",
        "rank": "C",
        "desc": "增加100经验到自己经验池",
    },
    "17": {
        "id": "17",
        "name": "零时迷子",
        "rank": "C",
        "desc": "使用后刷新自己当日副本关卡限制次数",
    },
    "18": {
        "id": "18",
        "name": "红药水",
        "rank": "D",
        "desc": "使用后将副本队伍的hp回复至max",
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
        "desc": "增加50经验到自己经验池",
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
        "rank": "EX",
        "desc": "无需使用，当持有永恒爱恋时妻子hp和atk提高30%",
    },
    "28": {
        "id": "28",
        "name": "光学迷彩",
        "rank": "EX",
        "desc": "无需使用，只要带在身上决斗时就不会承受损失",
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
        "rank": "B",
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
        "desc": "选择自己持有的一个道具 将其变成对应低一级稀有度的随机一或两件道具",
    },
    "35": {
        "id": "35",
        "name": "加速世界",
        "rank": "A",
        "desc": "刷新城市结算",
    },
    "36": {
        "id": "36",
        "name": "收获之日",
        "rank": "D",
        "desc": "增加20副本币",
    },
    "37": {
        "id": "37",
        "name": "武装镇压",
        "rank": "D",
        "desc": "增加城市20点治安",
    },
    "38": {
        "id": "38",
        "name": "太平盛世",
        "rank": "D",
        "desc": "增加20点繁荣度",
    },
    "39": {
        "id": "39",
        "name": "基建狂魔",
        "rank": "C",
        "desc": "当前建筑进度增加1次结算 研发进度增加1次结算",
    },
    "40": {
        "id": "40",
        "name": "心意蛋糕",
        "rank": "D",
        "desc": "指定女友使用，增加100点好感",
    },
    "41": {
        "id": "41",
        "name": "蓬莱之药",
        "rank": "EX",
        "desc": "使用后每两小时恢复一次决斗次数与副本次数",
    },
    "42": {
        "id": "42",
        "name": "绯想之剑",
        "rank": "B",
        "desc": "使用后随机变更当前天气",
    },
    "43": {
        "id": "43",
        "name": "初级进阶许可",
        "rank": "C",
        "desc": "可以进行1-7级rank提升",
    },
    "44": {
        "id": "44",
        "name": "中级进阶许可",
        "rank": "B",
        "desc": "可以进行8-13级rank提升",
    },
    "45": {
        "id": "45",
        "name": "高级进阶许可",
        "rank": "A",
        "desc": "可以进行14-20级rank提升",
    },
    "46": {
        "id": "46",
        "name": "储能核心",
        "rank": "D",
        "desc": "可以进行【决斗储能】或【副本储能】",
    },

}

# 加载项目内配置文件
# 武器池信息
with open(os.path.join(FILE_PATH, 'equipgecha.json'), 'r', encoding='UTF-8') as fa:
    Gecha = json.load(fa, strict=False)

# 加载副本信息
with open(os.path.join(FILE_PATH, 'dungeon_new.json'), 'r', encoding='UTF-8') as fa:
    dungeonlist = json.load(fa, strict=False)
# 加载副本路径
with open(os.path.join(FILE_PATH, 'dungeon_road.json'), 'r', encoding='UTF-8') as fa:
    dungeon_road = json.load(fa, strict=False)
# 加载装备信息
with open(os.path.join(FILE_PATH, 'equipment_new.json'), 'r', encoding='UTF-8') as fa:
    equip_info = json.load(fa, strict=False)
# 加载角色技能定义
with open(os.path.join(FILE_PATH, 'skill_definition.json'), 'r', encoding='UTF-8') as fa:
    self_skill_def = json.load(fa, strict=False)
# 加载boss技能定义
with open(os.path.join(FILE_PATH, 'boss_skill_definition.json'), 'r', encoding='UTF-8') as fa:
    boss_skill_def = json.load(fa, strict=False)
# 加载角色性格映射
with open(os.path.join(FILE_PATH, 'char_character.json'), 'r', encoding='UTF-8') as fa:
    char_character_json = json.load(fa, strict=False)
# 加载角色技能映射
with open(os.path.join(FILE_PATH, 'char_skill.json'), 'r', encoding='UTF-8') as fa:
    char_skill_json = json.load(fa, strict=False)
# 加载角色战斗风格映射
with open(os.path.join(FILE_PATH, 'char_style.json'), 'r', encoding='UTF-8') as fa:
    char_style_json = json.load(fa, strict=False)
# 加载角色羁绊信息
with open(os.path.join(FILE_PATH, 'char_fetter.json'), 'r', encoding='UTF-8') as fa:
    char_fetter_json = json.load(fa, strict=False)
# 技能定义整合
skill_def_json = {**self_skill_def, **boss_skill_def}

equip_name_map = {equip_info[i]['name']: equip_info[i] for i in equip_info.keys()}


# 更新角色技能映射关系
def refresh_char_skill():
    with open(os.path.join(FILE_PATH, 'char_skill.json'), 'w', encoding='UTF-8') as fa:
        json.dump(char_skill_json, fp=fa, ensure_ascii=False, indent=4)


# 更新角色性格映射关系
def refresh_char_character():
    with open(os.path.join(FILE_PATH, 'char_character.json'), 'w', encoding='UTF-8') as fa:
        json.dump(char_character_json, fp=fa, ensure_ascii=False, indent=4)


# 更新角色羁绊信息
def refresh_char_fetter():
    with open(os.path.join(FILE_PATH, 'char_fetter.json'), 'w', encoding='UTF-8') as fa:
        json.dump(char_fetter_json, fp=fa, ensure_ascii=False, indent=4)


# 更新角色风格
def refresh_char_style():
    with open(os.path.join(FILE_PATH, 'char_style.json'), 'w', encoding='UTF-8') as fa:
        json.dump(char_style_json, fp=fa, ensure_ascii=False, indent=4)


# ========================== 定义类 ==========================
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
        self.is_opt = {}
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

    def init_is_opt(self, gid):
        self.is_opt[gid] = False

    def get_is_opt(self, gid):
        return self.is_opt[gid] if self.is_opt[gid] is not None else False

    def on_opt(self, gid):
        self.is_opt[gid] = True

    def off_opt(self, gid):
        self.is_opt[gid] = False


# 记录礼物交换数据
class GiftChange:
    def __init__(self):
        self.giftchange_on = {}
        self.waitchange = {}
        self.isaccept = {}
        self.changeid = {}
        self.is_opt = {}

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

    def init_is_opt(self, gid):
        self.is_opt[gid] = False

    def get_is_opt(self, gid):
        return self.is_opt[gid] if self.is_opt[gid] is not None else False

    def on_opt(self, gid):
        self.is_opt[gid] = True

    def off_opt(self, gid):
        self.is_opt[gid] = False


# 红包实例
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


# 战斗模板
class Attr(object):
    def __init__(self, maxhp, curhp, atk, sp):
        self.maxhp = maxhp
        self.hp = curhp
        self.atk = atk
        self.max_sp = sp
        self.sp = sp
        self.boost = 0
        self.crit = 0
        self.double = 0
        self.recover = 0
        self.dodge = 0
        self.preempt = 50
        self.skill = []
        self.all_skill = []


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


# 建筑枚举类
class BuildModel(Enum):
    CENTER = {"id": 101, "name": "市政府", "sw": 0, "gold": 10000, "area": 10, "time": 1, "limit": 1,
              "desc": "只有拥有市政府才能执行政策，税收，建造等行政命令", "cost": 1000}
    MARKET = {"id": 102, "name": "商场", "sw": 1000, "gold": 50000, "area": 12, "time": 3, "limit": 10,
              "desc": "城市商业贸易中心，能为你带来不菲的收入（增加2w金币）", "cost": 0}
    ITEM_SHOP = {"id": 103, "name": "神秘商店", "sw": 100, "gold": 10000, "area": 15, "time": 2, "limit": 1,
                 "desc": "神秘的道具商店，黑心老板商只允许顾客盲盒购买（可使用[购买道具]指令）", "cost": 5000}
    TV_STATION = {"id": 104, "name": "事务所", "sw": 5000, "gold": 10000, "area": 13, "time": 3, "limit": 10,
                  "desc": "城市的各种职能部门，能能让你的城市功能更加齐全（增加1500声望）", "cost": 5000}
    POLICE_OFFICE = {"id": 105, "name": "警察局", "sw": 2000, "gold": 30000, "area": 10, "time": 3, "limit": 2,
                     "desc": "城市的治安部门，让你城市治安稳定（增加10点治安）", "cost": 10000}
    KONGFU = {"id": 106, "name": "道馆", "sw": 2500, "gold": 20000, "area": 6, "time": 2, "limit": 2,
              "desc": "修炼是游戏的一部分，挂机修炼额外获得5点经验/小时(拥有两个的话会无视24小时时间限制)", "cost": 10000}
    HUANBAO = {"id": 107, "name": "环保协会", "sw": 40000, "gold": 30000, "area": 15, "time": 3, "limit": 1,
               "desc": "环境保护，人人有责，可以依据城市林地面积提供声望(林地面积*5)", "cost": 20000}
    ZHIHUI = {"id": 108, "name": "作战中心", "sw": 10000, "gold": 100000, "area": 20, "time": 3, "limit": 1,
              "desc": "作战指挥中心，每天获取一瓶蓝药水一瓶红药水", "cost": 30000}
    DIZHI = {"id": 109, "name": "冒险工会", "sw": 3500, "gold": 200000, "area": 30, "time": 4, "limit": 2,
             "desc": "冒险者的聚集地，为冒险者们提供服务(获取一张藏宝图)", "cost": 20000}
    KELA = {"id": 110, "name": "大本钟", "sw": 50000, "gold": 500000, "area": 70, "time": 7, "limit": 1,
            "desc": "城市中心地标建筑，每日准时报时(获取一个零时迷子，低概率产出咲夜怀表)", "cost": 50000}
    FISSION_CENTER = {"id": 111, "name": "裂变中心", "sw": 100000, "gold": 1000000, "area": 120, "time": 10, "limit": 1,
                      "desc": "拥有无限可能性的裂变中心（获取一个有效分裂,低概率产出四重存在或好事成双）", "cost": 80000}
    EQUIP_CENTER = {"id": 112, "name": "熔炼工厂", "sw": 2000, "gold": 100000, "area": 15, "time": 3, "limit": 1,
                    "desc": "可以使用[装备熔炼]指令，用低级装备合成高级装备,装备合成会有一定失败率哦", "cost": 10000}
    TECHNOLOGY_CENTER = {"id": 113, "name": "科研中心", "sw": 10000, "gold": 100000, "area": 30, "time": 5, "limit": 1,
                         "desc": "解锁城市科技 可以使用[我的科技]和[科技研发]指令", "cost": 20000}
    APARTMENT = {"id": 114, "name": "公寓", "sw": 1000, "gold": 10000, "area": 6, "time": 2, "limit": 5,
                 "desc": "人民住宿的设施，虽然挤了点但总比住城外强，增加5点繁荣度", "cost": 2000}
    MICHELIN_RESTAURANT = {"id": 115, "name": "米其林餐厅", "sw": 3000, "gold": 50000, "area": 20, "time": 3, "limit": 1,
                           "desc": "甜点餐厅，产出1个心意蛋糕，是约会的好地方", "cost": 20000}

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


# 科技枚举类
class TechnologyModel(Enum):
    # TRANSPARENT_TRADE = {"id": 201, "name": "透明交易", "sw": 3000, "gold": 30000, "time": 2,
    #                      "desc": "购买物品时可以先看物品再决定要不要买"}

    BRANCH_STORE = {"id": 202, "name": "道具分店", "sw": 1000, "gold": 30000, "time": 2,
                    "desc": "商店可以购物两次"}

    BATTLE_RADAR = {"id": 203, "name": "作战雷达", "sw": 20000, "gold": 250000, "time": 2,
                    "desc": "获取蓝药水变为两瓶"}

    ARCHAEOLOGIST = {"id": 204, "name": "考古专家", "sw": 6000, "gold": 350000, "time": 3,
                     "desc": "藏宝图有更大的机会挖出更多的物品"}

    REFINING_TECHNOLOGY = {"id": 205, "name": "精致冶炼", "sw": 3500, "gold": 70000, "time": 2,
                           "desc": "熔炼工坊熔炼装备需求数量-1"}
    MONETARY_POLICY = {"id": 206, "name": "货币政策", "sw": 30000, "gold": 50000, "time": 4,
                       "desc": "商场提供的金币增加50%"}

    MANIPULATION = {"id": 207, "name": "舆论操纵", "sw": 50000, "gold": 30000, "time": 4,
                    "desc": "事务所提供的声望增加50%"}

    SATELLITE_CITY = {"id": 208, "name": "卫星城市", "sw": 80000, "gold": 750000, "time": 8,
                      "desc": "城市面积扩张到城市占比的1/8"}

    ROAD_PLANNING = {"id": 209, "name": "道路规划", "sw": 10000, "gold": 150000, "time": 2,
                     "desc": "拥堵状态阈值提高到90%"}

    SAND_FIX = {"id": 210, "name": "防风固沙", "sw": 5000, "gold": 30000, "time": 2,
                "desc": "提高沙尘天气的触发阈值"}

    TOUHOU_COOK = {"id": 211, "name": "新东方厨师", "sw": 5000, "gold": 30000, "time": 3,
                   "desc": "米其林餐厅产出蛋糕+1 约会好感额外+100"}
    #
    # ENERGY_STORAGE_CORE = {"id": 212, "name": "储能核心", "sw": 1000, "gold": 10000, "time": 1,
    #                        "desc": "增加[决斗储能]和[副本储能]指令 消耗5次次数产生精英对局和零时迷子"}

    SEIZE_WEALTH = {"id": 213, "name": "巧夺民财", "sw": 50000, "gold": 10000, "time": 4,
                    "desc": "增加10%民众忍耐税收比例上限"}

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


# 天气枚举类
class WeatherModel(Enum):
    NONE = {"id": 0, "name": "无", "desc": "没有效果的天气"}
    KUAIQING = {"id": 1, "name": "快晴", "desc": "建造建筑消耗金币和声望减少20%"}
    WUYU = {"id": 2, "name": "雾雨", "desc": "使用资源收益型道具的收益提高25%"}
    YUNTIAN = {"id": 3, "name": "云天", "desc": "提升rank消耗金币减少20%"}
    CANGTIAN = {"id": 4, "name": "苍天", "desc": "进入副本的sp最大值+10"}
    BAO = {"id": 5, "name": "雹", "desc": "领取金币时会获得1w金币"}
    HUAYUN = {"id": 6, "name": "花云", "desc": "决斗失败损失声望降为0"}
    NONGWU = {"id": 7, "name": "浓雾", "desc": "狙击到对方妻子时抢夺对方1w金币 不足则扣除对方1000声望作为替代"}
    XUE = {"id": 8, "name": "雪", "desc": "购买道具消耗加倍，领地结算收入减半"}
    TAIYANGYU = {"id": 9, "name": "太阳雨", "desc": "决斗失败时无论好感多少都会丢失女友"}
    SHUYU = {"id": 10, "name": "疏雨", "desc": "女友计算战力时视为满级（100级）"}
    FENGYU = {"id": 11, "name": "风雨", "desc": "可以使用快速决斗指令"}
    QINGLAN = {"id": 12, "name": "晴岚", "desc": "结算时的建筑收益失效"}
    CHUANWU = {"id": 13, "name": "川雾", "desc": "决斗和副本10%概率额外消耗一次次数，也有10%概率不消耗次数"}
    TAIFENG = {"id": 14, "name": "台风", "desc": "拒绝决斗会随时1w金币,不足则损失1k声望"}
    ZHI = {"id": 15, "name": "凪", "desc": "决斗和副本指令无效"}
    ZUANSHICHEN = {"id": 16, "name": "钻石尘", "desc": "城市结算时建筑与科研进度无法推进"}
    HUANGSHA = {"id": 17, "name": "黄砂", "desc": "副本战斗失败回复hp至满血"}
    LIERI = {"id": 18, "name": "烈日", "desc": "使用道具时需要支付1w金币"}
    MEIYU = {"id": 19, "name": "梅雨", "desc": "副本挑战失败时20%概率恢复一次副本次数"}
    JIGUANG = {"id": 20, "name": "极光", "desc": "购买道具时20%获取绯想之剑"}

    @staticmethod
    def get_by_id(id):
        for i in WeatherModel:
            if i.value['id'] == id:
                return i
        return None

    @staticmethod
    def get_by_name(name):
        for i in WeatherModel:
            if i.value['name'] == name:
                return i
        return None


# ========================== 基础方法 ==========================
# 哈希到一定数字范围内
def hashval(str, siz):
    hash = 0
    for x in str: hash += (ord(x))
    return (hash % siz)


# md5编码
def md5(str):
    m = hashlib.md5()
    m.update(str.encode("utf8"))
    return m.hexdigest()


# ========================== 每日限制器 ==========================
daily_zero_get_limiter = DailyAmountLimiter("zero_get", ZERO_GET_LIMIT, RESET_HOUR)
daily_sign_limiter = DailyAmountLimiter("sign", SIGN_DAILY_LIMIT, RESET_HOUR)
daily_free_limiter = DailyAmountLimiter("free", FREE_DAILY_LIMIT, RESET_HOUR)
daily_duel_limiter = DailyAmountLimiter("duel", DUEL_DAILY_LIMIT, RESET_HOUR)
daily_date_limiter = DailyAmountLimiter("date", DATE_DAILY_LIMIT, RESET_HOUR)
daily_gift_limiter = DailyAmountLimiter("gift", GIFT_DAILY_LIMIT, RESET_HOUR)
daily_dun_limiter = DailyAmountLimiter("dun", DUN_DAILY_LIMIT, RESET_HOUR)
daily_stage_limiter = DailyAmountLimiter("stage", STAGE_DAILY_LIMIT, RESET_HOUR)
daily_boss_limiter = DailyAmountLimiter("boss", BOSS_DAILY_LIMIT, RESET_HOUR)
daily_equip_limiter = DailyAmountLimiter("equip", EQUIP_DAILY_LIMIT, RESET_HOUR)
daily_manor_limiter = DailyAmountLimiter("manor", MANAGE_DAILY_LIMIT, RESET_HOUR)
daily_recruit_limiter = DailyAmountLimiter("recruit", RECRUIT_DAILY_LIMIT, RESET_HOUR)

# ========================== 全局实例 ==========================
# 红包发送操作实例
r_gold = duelrandom()
# 决斗数据操作实例
duel_judger = DuelJudger()
# 礼物交换操作实例
gift_change = GiftChange()

# ========================== 初始化执行方法 ==========================
# 加载dlc开关
cfg.load_dlc_switch()
# 加载时装列表
cfg.refresh_fashion()
# 刷新dlc-角色 dlc-介绍配置
cfg.refresh_config()
# 检查dlcswitch是否有漏加的新dlc
cfg.check_dlc()

# 初始化道具
ITEM_NAME_MAP = {ITEM_INFO[i]["name"]: ITEM_INFO[i] for i in ITEM_INFO.keys()}
ITEM_RANK_MAP = {}
for k, v in ITEM_INFO.items():
    if not ITEM_RANK_MAP.get(v['rank']):
        ITEM_RANK_MAP[v['rank']] = []
    ITEM_RANK_MAP.get(v['rank']).append(v['id'])


# ========================== 其他方法 ==========================

# ========== 角色相关方法 ==========
# 获取指定用户状态
def get_user_counter(gid, uid, state: UserModel):
    i_c = ItemCounter()
    return i_c._get_user_info(gid, uid, state)


# 存储指定用户状态
def save_user_counter(gid, uid, state: UserModel, num):
    i_c = ItemCounter()
    i_c._save_user_info(gid, uid, state, num)


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
    # 等级上限提升次数
    zslevel = CE._get_zhuansheng(gid, uid, cid)
    now_level = CE._get_card_level(gid, uid, cid)
    need_exp = int(now_level * now_level / 5 + 5)
    exp_info = CE._get_card_exp(gid, uid, cid)
    now_exp = exp_info + exp
    if now_level < CARD_LEVEL_MAX + zslevel * 10:
        while now_exp >= need_exp:
            now_level = now_level + 1
            now_exp = now_exp - need_exp
            need_exp = int(now_level * now_level / 5 + 5)
            if now_level >= CARD_LEVEL_MAX + zslevel * 10:
                break
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


# ========== 装备相关方法 ==========
def get_equip_desc(info):
    model_name_li = ['N', 'R', 'SR', 'SSR', 'UR', 'MR']
    msg = f"[{info['type']}]{info['name']}\n装备品质：{model_name_li[info['level'] - 1]}\n"
    for e in info['effect'].keys():
        if e in ['hp', 'atk', 'sp', 'boost', 'crit', 'double', 'recover', 'dodge']:
            if info['effect'][e]['type'] == 'const':
                msg += f"{e}:{info['effect'][e]['value']} "
        elif e == 'skill':
            if info['effect'][e]['type'] == 'const':
                skill_msg = ' '.join(info['effect'][e]['value'])
                msg += f"{e}:{skill_msg} "
    if info.get('desc'):
        msg += '\n' + info.get('desc')
    return msg


# 根据装备id获取装备信息
def get_equip_info_id(eid):
    e = equip_info.get(str(eid))
    if not e:
        return None
    pin = ['N', 'R', 'SR', 'SSR', 'UR', 'MR']
    equipinfo = {'eid': e['eid'], 'type': e['type'], 'type_id': e['type_id'], 'name': e['name'],
                 'model': pin[e['level'] - 1], 'level': e['level'], 'desc': get_equip_desc(e)}
    return equipinfo


# 根据装备名称获取装备信息
def get_equip_info_name(ename):
    e = equip_name_map.get(ename)
    if not e:
        return None
    pin = ['N', 'R', 'SR', 'SSR', 'UR', 'MR']
    equipinfo = {'eid': e['eid'], 'type': e['type'], 'type_id': e['type_id'], 'name': e['name'],
                 'model': pin[e['level'] - 1], 'level': e['level'], 'desc': get_equip_desc(e)}
    return equipinfo


# 随机获得一件装备并返回获得信息
def add_equip_info(gid, uid, level, down_list):
    CE = CECounter()
    chose_li = [equip_info[i]['eid'] for i in equip_info.keys() if
                equip_info[i]['level'] == level and equip_info[i]['eid'] in down_list]
    equipid = random.choice(chose_li)
    CE._add_equip(gid, uid, equipid, 1)
    equipinfo = get_equip_info_id(equipid)
    return equipinfo


# ========== 建筑相关方法 ==========
# 获取建筑情况
def check_build_counter(gid, uid, b_m: BuildModel):
    i_c = ItemCounter()
    return i_c._get_user_state(gid, uid, b_m.value['id'])


# 获取建筑情况
def check_technolog_counter(gid, uid, t_m: TechnologyModel):
    i_c = ItemCounter()
    return i_c._get_user_state(gid, uid, t_m.value['id'])


# ========== 道具相关方法 ==========
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
    if item['name'] == "蓬莱之药":
        # 蓬莱之药只能获取一次
        if get_user_counter(gid, uid, UserModel.PENG_LAI_GET):
            return
        else:
            save_user_counter(gid, uid, UserModel.PENG_LAI_GET, 1)
    i_c = ItemCounter()
    i_c._add_item(gid, uid, int(item['id']), num)


# 消耗道具
def use_item(gid, uid, item, num=1):
    i_c = ItemCounter()
    i_c._add_item(gid, uid, int(item['id']), num=-num)


# ========== 天气相关方法 ==========
# 获取天气情况
def get_weather(gid):
    ic = ItemCounter()
    id = ic._get_group_state(gid, GroupModel.WEATHER)
    return WeatherModel.get_by_id(id)


# 更新天气
def save_weather(gid, weather: WeatherModel):
    ic = ItemCounter()
    ic._save_group_state(gid, GroupModel.WEATHER, weather.value['id'])


# ========== 不明分类方法 ==========


# 抽卡
def get_gecha_equip(gid, uid, gechanum, xnum, dnum, unum, gechainfo):
    equip_list = ''
    CE = CECounter()
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
        equip_list = equip_list + f"\n{equip_info['model']}品质{equip_info['type']}:{equip_info['name']}"
    CE._add_gecha_num(gid, uid, xnum, dnum, unum)
    msg = f"{equip_list}\n"
    return msg


# 获取蛋池信息
def get_gecha_info(gechaname):
    gechalist = Gecha
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
    nowinfo = CE._get_bossinfo(gid)
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


# 查询单角色战斗能力
def get_card_battle_info(gid, uid, cid):
    # 基础属性
    atk = 100
    hp = 1000
    sp = 1
    # 技能
    skills = list(set(get_char_skill(cid)))

    # 等级加成
    CE = CECounter()
    level = CE._get_card_level(gid, uid, cid)
    if get_weather(gid) == WeatherModel.SHUYU:
        level = 100
    atk += 5 * (level + 1)
    hp += 50 * (level + 1)

    # 好感加成
    duel = DuelCounter()
    favor = duel._get_favor(gid, uid, cid)
    atk += int(favor / 100)

    # 时装加成
    # 获取角色时装穿戴信息
    up_info = duel._get_fashionup(gid, uid, cid, 0)
    if up_info:
        # 获取穿戴时装所加的战斗力
        fashion_info = get_fashion_info(up_info)
        hp += (fashion_info['add_ce'])

    # 星级加成
    cardstar = CE._get_cardstar(gid, uid, cid)
    hp += cardstar * 6 * level
    atk += int(cardstar * 0.6 * level)

    # rank加成
    rank = CE._get_rank(gid, uid, cid)
    sp += int(rank / 10)
    hp += 200 * rank
    atk += 30 * rank

    # 计算攻守偏移
    base = get_battle_style_value(cid)
    atk_pian = 1 + (50 - base) / 100
    hp_pian = 1 + (base - 50) / 100

    # 计算性格加成
    if check_have_character(cid, "勇敢"):
        atk_pian = atk_pian + 0.1
    if check_have_character(cid, "慎重"):
        hp_pian = hp_pian + 0.1
    if check_have_character(cid, "傲娇"):
        sp = sp + 1
    if duel._get_queen_owner(gid, cid) != 0:
        item = get_item_by_name("永恒爱恋")
        if check_have_item(gid, uid, item):
            atk_pian += 0.3
            hp_pian += 0.3
    hp = int(hp * hp_pian)
    atk = int(atk * atk_pian)

    # 装备加成
    dreeslist = CE._get_dress_list(gid, uid, cid)
    content = {
        "favor": favor,
        "level": level,
        "eids": dreeslist,
        "rank": rank,
        "star": cardstar,
        "hp": hp,
        "atk": atk,
        "sp": sp,
        "skills": skills,
        "hp_pian": hp_pian,
        "atk_pian": atk_pian
    }
    result = {}
    result["hp"] = hp
    result["atk"] = atk
    result["sp"] = sp
    result["skills"] = skills
    result["boost"] = 0
    result["crit"] = 0
    result["double"] = 0
    result["recover"] = 0
    result["dodge"] = 0
    for eid in dreeslist:
        effect = equip_info[str(eid)]['effect']
        for e in effect.keys():
            if e in ['hp', 'atk', 'sp', 'boost', 'crit', 'double', 'recover', 'dodge']:
                if effect[e]['type'] == "const":
                    result[e] += effect[e]['value']
                elif effect[e]['type'] == "exec":
                    result[e] += int(eval(effect[e]['value']), content)
            elif e == 'skill':
                if effect['skill']['type'] == "const":
                    result["skills"] = list(set(result["skills"].extend(effect['skill']['value'])))
                elif effect['skill']['type'] == "exec":
                    if eval(effect['skill']['condition']):
                        result["skills"] = list(set(result["skills"].extend(effect['skill']['value'])))
    return result


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
    CE = CECounter()
    girls = CE._get_cards_byrank(gid, 50)
    if len(girls) > 0:
        data = sorted(girls, key=lambda cus: cus[1], reverse=True)
        new_data = []
        for girl_data in data:
            gid1, rank, uid, cid = girl_data
            content = get_card_battle_info(gid1, uid, cid)
            hp, atk, sp, skills = content["hp"], content["atk"], content["sp"], content["skills"]
            gpower = hp + 10 * atk
            new_data.append((rank, gpower, uid, cid, hp, atk))
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


# 处理我方队伍增益 defen 为cid列表 z_atk与z_hp是经过buff后的原始攻击和hp
def duel_my_buff(gid, uid, defen):
    z_hp, z_atk, z_sp, z_skills = 0, 0, 0, []
    for i in defen:
        content = get_card_battle_info(gid, uid, i)
        hp, atk, sp, skills = content["hp"], content["atk"], content["sp"], content["skills"]
        # 羁绊加成
        if char_fetter_json.get(str(i)):
            rate = 1
            for j in char_fetter_json.get(str(i)):
                if j in defen:
                    rate += 0.05
            hp = int(hp * rate)
            atk = int(atk * rate)
        z_hp += hp
        z_atk += atk
        z_sp += sp
        z_skills.extend(skills)
        z_skills = list(set(z_skills))
    chara_map = count_char_character(defen)
    duel = DuelCounter()
    cidlist = duel._get_cards(gid, uid)
    changwai_li = [cid for cid in cidlist if cid not in defen]
    changwai_map = count_char_character(changwai_li)
    hp_buff = 1 + (chara_map["固执"] * 5 + changwai_map["固执"] + chara_map["冷静"]) / 100
    atk_buff = 1 + (chara_map["自大"] * 5 + changwai_map["自大"] + chara_map["冷静"]) / 100
    hp_gu = 0
    atk_gu = 0
    for i in changwai_li:
        if check_have_character(i, "弱气"):
            content = get_card_battle_info(gid, uid, i)
            hp = content["hp"]
            hp_gu += int(hp * 0.1)
        if check_have_character(i, "毒舌"):
            content = get_card_battle_info(gid, uid, i)
            atk = content["atk"]
            atk_gu += int(atk * 0.1)

    z_hp = int(z_hp * hp_buff)
    z_atk = int(z_atk * atk_buff)
    my_recover = chara_map["温柔"] * 5 + chara_map["冷静"] * 1 + changwai_map["温柔"]
    my_double = chara_map["淘气"] * 5 + chara_map["冷静"] * 1 + changwai_map["淘气"]
    my_crit = chara_map["天然"] * 5 + chara_map["冷静"] * 1 + changwai_map["天然"]
    my_boost = chara_map["病娇"] * 5 + chara_map["冷静"] * 1 + changwai_map["病娇"]
    my_dodge = chara_map["元气"] * 5 + chara_map["冷静"] * 1 + changwai_map["元气"]
    my = Attr(z_hp, z_hp, z_atk, z_sp)
    my.all_skill = z_skills
    my.skill = []
    my.boost = my_boost
    my.crit = my_crit
    my.double = my_double
    my.recover = my_recover
    my.dodge = my_dodge
    return my


# 处理敌方debuff
def duel_enemy_buff(defen, e_hp, e_sp, e_atk, e_buff_li, e_skills):
    chara_map = count_char_character(defen)
    hp_debuff = 1 - (chara_map["腹黑"] * 5) / 100
    atk_debuff = 1 - (chara_map["悠闲"] * 5) / 100
    e_hp = int(e_hp * hp_debuff)
    e_atk = int(e_atk * atk_debuff)
    debuff = 1 - chara_map["无口"] * 0.2
    e_buff_li = [int(i * debuff) for i in e_buff_li]
    if chara_map["弱气"]:
        e_buff_li[1] = 0
    if chara_map["毒舌"]:
        e_buff_li[3] = 0
    enemy = Attr(e_hp, e_hp, e_atk, 0)
    enemy.boost = e_buff_li[0]
    enemy.crit = e_buff_li[1]
    enemy.double = e_buff_li[2]
    enemy.recover = e_buff_li[3]
    enemy.dodge = e_buff_li[4]
    enemy.all_skill = e_skills
    enemy.skill = e_skills
    enemy.sp = e_sp
    return enemy


# 根据角色id获取性格
def get_char_character(cid):
    if char_character_json.get(str(cid)):
        return char_character_json.get(str(cid))
    else:
        return []


# 检查角色是否拥有某性格
def check_have_character(cid: int, type: str):
    return type in get_char_character(cid)


# 根据角色id列表和指定性格统计拥有该性格角色的数量
def sum_character(cid_li: list, type: str):
    count = 0
    for i in cid_li:
        li = get_char_character(i)
        if type in li:
            count += 1
    return count


# 聚合角色列表的性格信息
def count_char_character(cid_li):
    result = {}
    for i in character.keys():
        result[i] = 0
    for i in cid_li:
        li = get_char_character(i)
        for j in li:
            result[j] += 1
    return result


# 获取战斗风格数值
def get_battle_style_value(cid):
    # 有设置直接用设置
    base = char_style_json.get(str(cid))
    # 无设置取固定的哈希随机数
    if base is None:
        base = hashval(md5(str(cid)), 100)
    return base


# 获取战斗风格描述
def get_battle_style(cid):
    base = get_battle_style_value(cid)
    if base < 20:
        return "重攻"
    elif 20 <= base < 40:
        return "偏攻"
    elif 40 <= base <= 60:
        return "平衡"
    elif 60 < base <= 80:
        return "偏守"
    else:
        return "重守"


# 获取角色的基础技能
def get_char_skill(cid):
    if char_skill_json.get(str(cid)):
        return char_skill_json.get(str(cid));
    base = hashval(md5(str(cid)), len(self_skill_def))
    return [list(self_skill_def.keys())[base]]
