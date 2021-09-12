from enum import Enum
class WeatherModel(Enum):
    NONE = {"id": 0, "name": "无", "desc": "没有效果的天气"}
    KUAIQINGWUY = {"id": 1, "name": "快晴", "desc": "取消招募/购物花费金币，建造建筑消耗金币减少20%"}
    WUYU = {"id": 2, "name": "雾雨", "desc": "使用资源收益型道具的收益提高25%"}
    YUNTIAN = {"id": 3, "name": "云天", "desc": "提升rank时大概率得到1w金币的补偿金"}
    CANGTIAN = {"id": 4, "name": "苍天", "desc": "使用道具时1%概率获取随机道具"}
    BAO = {"id": 5, "name": "雹", "desc": "领取金币时会获得1w金币"}
    HUAYUN = {"id": 6, "name": "花云", "desc": "决斗失败损失声望降为0"}
    NONGWU = {"id": 7, "name": "浓雾", "desc": "狙击到对方妻子时抢夺对方1w金币 不足则扣除对方1000声望作为替代"}
    XUE = {"id": 8, "name": "雪", "desc": "决斗失败方额外损失2000金币 不足则扣除1000声望"}
    TAIYANGYU = {"id": 9, "name": "太阳雨", "desc": "决斗失败/副本失败时随机扣除一件装备/道具"}
    SHUYU = {"id": 10, "name": "疏雨", "desc": "女友计算战力时视为满级（200级）"}
    FENGYU = {"id": 11, "name": "风雨", "desc": "可以使用快速决斗指令，正常决斗时一次消耗所有的决斗次数，获胜/失败奖励/,惩罚变为消耗次数倍"}
    QINGLAN = {"id": 12, "name": "晴岚", "desc": "进入副本时无论选择什么难度都是随机难度"}
    CHUANWU = {"id": 13, "name": "川雾", "desc": "损失金币/声望时金币/声望越多的人损失越多，获取金币/声望时金币/声望越少的人获取越多"}
    TAIFENG = {"id": 14, "name": "台风", "desc": "拒绝决斗会随时1w金币,不足则损失1k声望"}
    ZHI = {"id": 15, "name": "凪", "desc": "决斗和副本指令无效"}
    ZUANSHICHEN = {"id": 16, "name": "钻石尘", "desc": "损失金币时额外损失5000 损失声望时额外损失500"}
    HUANGSHA = {"id": 17, "name": "黄砂", "desc": "进入副本时消耗5次副本次数可以掉落道具的副本一定会掉落道具"}
    LIERI = {"id": 18, "name": "烈日", "desc": "增加贵族乞讨功能，对金币排行榜第一位的人员使用可以获取其1w金币（限制使用一次）"}
    MEIYU = {"id": 19, "name": "梅雨", "desc": "梭哈失败后获取1w金币（限制触发一次）"}
    JIGUANG = {"id": 20, "name": "极光", "desc": "随机一个天气效果"}

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

import random

rd=random.choice([i for i in WeatherModel])
print(rd.value["id"])