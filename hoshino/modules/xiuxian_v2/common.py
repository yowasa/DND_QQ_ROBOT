import random

from .config import *
from .counter.HistoryCounter import *
from .counter.XiuXianCounter import *


class UserAttr():
    def __init__(self, attr=None):
        if attr:
            dic = eval(attr)
            # 寿元 -> 归0即死
            self.age_max = dic['age_max']
            # 基础属性
            # 悟性->学习速度和要求
            self.comprehension = dic['comprehension']
            # 体质->血量物攻物防
            self.constitution = dic['constitution']
            # 灵力->蓝量魔攻魔防
            self.magic_power = dic['magic_power']
            # 气感->注灵效率 炼丹练宝
            self.perception = dic['perception']
            # 神识->潜在能力 驾驭功法法宝的能力
            self.spiritual = dic['spiritual']

            # 战斗属性
            self.hp = dic['hp']
            self.mp = dic['mp']
            self.atk1 = dic['atk1']
            self.atk2 = dic['atk2']
            self.defend1 = dic['defend1']
            self.defend2 = dic['defend1']
            # 特殊属性
            self.boost = dic.get("boost", 0)
            self.double = dic.get("double", 0)
            self.dodge = dic.get("dodge", 0)

    def get_json_str(self):
        dic = dict()
        dic["age_max"] = self.age_max
        dic["comprehension"] = self.comprehension
        dic["constitution"] = self.constitution
        dic["magic_power"] = self.magic_power
        dic["perception"] = self.perception
        dic["spiritual"] = self.spiritual
        dic["hp"] = self.hp
        dic["mp"] = self.mp
        dic["atk1"] = self.atk1
        dic["atk2"] = self.atk2
        dic["defend1"] = self.defend1
        dic["defend2"] = self.defend2
        dic["boost"] = self.boost
        dic["double"] = self.double
        dic["dodge"] = self.dodge
        return json.dumps(dic)

    @staticmethod
    def init_attr():
        attr = UserAttr()
        attr.age_max = random.randint(60, 100)
        attr.comprehension = random.randint(1, 100)
        attr.constitution = random.randint(1, 100)
        attr.magic_power = random.randint(1, 100)
        attr.perception = random.randint(1, 100)
        attr.spiritual = random.randint(10, 20)
        attr.hp = random.randint(80, 100)
        attr.mp = random.randint(40, 50)
        attr.atk1 = random.randint(10, 20)
        attr.atk2 = random.randint(10, 20)
        attr.defend1 = random.randint(10, 20)
        attr.defend2 = random.randint(10, 20)
        attr.boost = 0
        attr.double = 0
        attr.dodge = 0
        return attr


class AllUserInfo():
    def __init__(self, user: UserInfo):
        self.org = user
        self.uid = user.uid
        self.name = user.name
        self.magic_root = user.magic_root
        self.exp = user.exp
        self.grade = user.grade
        self.level = user.level
        self.local = user.local
        self.belong = user.belong
        self.arms = user.arms
        self.armor = user.armor
        self.magic_weapon = user.magic_weapon
        self.attr = UserAttr(user.attr)
        self.build_ability(user.ability)
        # 处理其他数据
        self.other_info(user.other)
        # 处理战斗数据
        self.duel_battle_info()
        # 处理userModel
        self.duel_user_model()
        # 大罗洞观触发标识
        self.flag = 0

    def build_ability(self, ability):
        self.ability = eval(ability)
        self.use_spiritual = 0

    def duel_battle_info(self):  # 标签库
        attr = self.attr
        # 基础属性
        self.battle_hp = attr.hp
        self.battle_mp = attr.mp
        # 物理攻击力
        self.battle_atk1 = attr.atk1
        # 术法攻击力
        self.battle_atk2 = attr.atk2
        # 物理攻击力
        self.battle_defend1 = attr.defend1
        # 术法攻击力
        self.battle_defend2 = attr.defend2

        self.battle_boost = attr.boost
        self.battle_double = attr.double
        self.battle_dodge = attr.dodge

        num = len(self.magic_root)
        buff_rate = 1 + (50 / num) / 100
        low_buff_rate = 1 + ((50 / num) * 0.7) / 100

        # 灵根加成
        if '金' in self.magic_root:
            self.battle_atk1 = int(self.battle_atk1 * low_buff_rate)
        if '木' in self.magic_root:
            self.battle_hp = int(self.battle_hp * buff_rate)
            self.battle_mp = int(self.battle_mp * buff_rate)
        if '水' in self.magic_root:
            self.battle_defen2 = int(self.battle_defend2 * buff_rate)
        if '火' in self.magic_root:
            self.battle_atk2 = int(self.battle_atk2 * low_buff_rate)
        if '土' in self.magic_root:
            self.battle_defen1 = int(self.battle_defend1 * buff_rate)

        # 武器加成
        arm_eff = get_equip_by_name(self.arms)
        if arm_eff:
            buff = arm_eff['buff']
            self.cal_buff(buff)
        # 武器加成
        armor_eff = get_equip_by_name(self.armor)
        if armor_eff:
            buff = armor_eff['buff']
            self.cal_buff(buff)
        # 能力加成
        for i in self.ability:
            ab = get_ability_by_name(i)
            if ab:
                buff = ab.get('buff')
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
        if buff.get('defend1'):
            self.battle_defen1 += buff.get('defend1')
        if buff.get('defend2'):
            self.battle_defen2 += buff.get('defend2')
        if buff.get('boost'):
            self.battle_boost += buff.get('boost')
        if buff.get('double'):
            self.battle_double += buff.get('double')
        if buff.get('dodge'):
            self.battle_dodge += buff.get('dodge')
        attr = self.attr
        content = {"age_max": attr.age_max, "magic_root": self.magic_root, "atk1": self.battle_atk1,
                   "atk2": self.battle_atk2, "defend1": self.battle_defend1, "defend2": self.battle_defend2,
                   "hp": self.battle_hp, "mp": self.battle_mp, "grade": self.grade, "level": self.level,
                   "comprehension": attr.comprehension, "constitution": attr.constitution,
                   "magic_power": attr.magic_power, "perception": attr.perception, "spiritual": attr.spiritual}
        if buff.get('hp_exec'):
            self.battle_hp = int(eval(buff.get('hp_exec'), content))
        if buff.get('mp_exec'):
            self.battle_mp = int(eval(buff.get('mp_exec'), content))
        if buff.get('atk1_exec'):
            self.battle_atk1 = int(eval(buff.get('atk1_exec'), content))
        if buff.get('atk2_exec'):
            self.battle_atk2 = int(eval(buff.get('atk2_exec'), content))
        if buff.get('defend1_exec'):
            self.battle_defend1 = int(eval(buff.get('defend1_exec'), content))
        if buff.get('defend2_exec'):
            self.battle_defend2 = int(eval(buff.get('defend2_exec'), content))

    def duel_other_info(self, other):
        pass

    def build_other_info(self):
        return "{}"

    def duel_user_model(self):
        flags = UserModel.get_all_user_flag(self.uid)
        self.flags = flags
        # 伤势
        self.shangshi = flags.get(UserModel.SHANGSHI)
        shangshi_li = ["无", "轻伤", "重伤", "濒死"]
        # 伤势描述
        self.shangshi_desc = shangshi_li[self.shangshi]
        # 持有道具数
        self.have_item_count = ItemDao.count_item(self.uid)
        # 最大持有道具数
        self.max_item_count = ItemDao.get_max_count(self.uid)
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
        item_id = self.flags.get(UserModel.LIANBAO_ITEM)
        if item_id:
            item = ITEM_INFO[str(item_id)]
            need = LIANBAO_NEED_LINGQI[item['level']]
            have = self.flags.get(UserModel.LIANBAO_LINGQI)
            if have >= need:
                await bot.send(ev, "炼宝灵气已经充足，请使用#练宝 指令获取炼制完成的法宝")
        await self.check_cd_ignore_other(bot, ev)
        # 扣减躲避时间
        if "缩地成寸" in self.ability:
            if self.flags.get(UserModel.SUODI) > 0:
                UserModelDao.add_user_counter(self.uid, UserModel.SUODI, num=-1)
        if "大罗洞观" in self.ability:
            if random.randint(1, 10) == 1:
                self.daluo = 1
                await bot.send(ev, "大罗入世，窥晓阴阳，观测天机，规避天道，此次行动取消CD")

    async def check_cd_ignore_other(self, bot, ev):
        act_times = self.flags.get(UserModel.ACT_TIMES)
        if act_times > (self.attr.age_max * 10):
            UserDao.delete_user(self)
            await bot.finish(ev, f"寿元耗尽，你已死亡", at_sender=True)
        if not flmt.check(self.uid):
            await bot.finish(ev, None)

    def start_cd(self):
        # 练宝相关
        item_id = self.flags.get(UserModel.LIANBAO_ITEM)
        if item_id:
            address = MAP.get(self.map)
            min = address["lingqi_min"]
            max = address["lingqi_max"]
            lingqi = int(random.randint(min, max) * 0.1)
            if "天灵地动" in self.ability:
                lingqi = 2 * lingqi
            UserModelDao.add_user_counter(self.uid, UserModel.LIANBAO_LINGQI, lingqi)
        if not self.daluo:
            flmt.start_cd(self.uid)

    def save_user(self):
        user = UserInfo()
        user.uid = self.uid
        user.name = self.name
        user.magic_root = self.magic_root
        user.exp = self.exp
        user.grade = self.grade
        user.level = self.level
        user.local = self.local
        user.belong = self.belong
        user.arms = self.arms
        user.armor = self.armor
        user.magic_weapon = self.magic_weapon
        user.attr = self.attr.get_json_str()
        user.ability = str(self.ability)
        user.other = self.build_other_info()
        ct = XiuXianCounter()
        ct._save_user_info(user)

    def have_item(self, item_name):
        item = ItemDao.get_item_by_name(item_name)
        return ItemDao.check_have_item(self.uid, item)

    def use_item(self, item_name, num=1):
        item = ItemDao.get_item_by_name(item_name)
        ItemDao.use_item(self.uid, item, num=num)

    def check_and_use_item(self, item_name, num=1):
        num = self.have_item(item_name)
        if num < num:
            return False
        self.use_item(item_name, num=num)
        return True

    def check_and_add_item(self, item_name, num=1):
        count = ItemDao.count_item(self.uid)
        max = ItemDao.get_max_count(self.uid)
        if (count + num) > max:
            return False
        item = ItemDao.get_item_by_name(item_name)
        ItemDao.add_item(self.uid, item, num=num)
        return True


# 道具操作方法集
class ItemDao():
    # 根据名字获取道具
    @staticmethod
    def get_item_by_name(name):
        return ITEM_NAME_MAP.get(name)

    # 检查是否持有道具
    @staticmethod
    def check_have_item(uid, item):
        i_c = XiuXianCounter()
        num = i_c._get_item_num(uid, int(item['id']))
        return num

    # 添加道具
    @staticmethod
    def add_item(uid, item, num=1):
        i_c = XiuXianCounter()
        if ItemDao.count_item(uid) >= ItemDao.get_max_count(uid):
            return 0
        i_c._add_item(uid, int(item['id']), num)
        return 1

    # 获取角色最大持有物品数量
    @staticmethod
    def get_max_count(uid):
        ct = XiuXianCounter()
        user = ct._get_user(uid)
        max = ITEM_CARRY[str(user.level)]
        return max

    # 无视上限添加道具
    @staticmethod
    def add_item_ignore_limit(uid, item, num=1):
        i_c = XiuXianCounter()
        i_c._add_item(uid, int(item['id']), num)

    # 检查背包空间是否足够
    @staticmethod
    def check_have_space(uid):
        if ItemDao.count_item(uid) >= ItemDao.get_max_count(uid):
            return 0
        return 1

    # 消耗道具
    @staticmethod
    def use_item(uid, item, num=1):
        i_c = XiuXianCounter()
        i_c._add_item(uid, int(item['id']), num=-num)

    # 获取道具总数
    @staticmethod
    def count_item(uid):
        i_c = XiuXianCounter()
        return i_c._count_item_num(uid)


# 群组操作集合
class GroupDao():
    # 获取指定群组状态
    @staticmethod
    def get_group_counter(gid, state: GroupModel):
        i_c = XiuXianCounter()
        return i_c._get_group_state(gid, state)

    # 获取指定群组状态
    @staticmethod
    def save_group_counter(gid, state: GroupModel, num):
        i_c = XiuXianCounter()
        return i_c._save_group_state(gid, state, num)


class UserModelDao():

    # 获取指定用户状态
    @staticmethod
    def get_user_counter(uid, state: UserModel):
        i_c = XiuXianCounter()
        return i_c._get_user_model(uid, state)

    # 获取全部用户状态
    @staticmethod
    def get_all_user_flag(uid):
        i_c = XiuXianCounter()
        li = i_c._query_user_model(uid)
        map = {i[0]: i[1] for i in li}
        result_map = {}
        for i in UserModel:
            result_map[i] = 0
            if map.get(i.value[0]):
                result_map[i] = map.get(i.value[0])
        return result_map

    # 存储指定用户状态
    @staticmethod
    def save_user_counter(uid, state: UserModel, num):
        i_c = XiuXianCounter()
        i_c._save_user_model(uid, state, num)

    # 指定用户状态+1
    @staticmethod
    def add_user_counter(uid, state: UserModel, num=1):
        i_c = XiuXianCounter()
        base = i_c._get_user_model(uid, state)
        i_c._save_user_model(uid, state, base + num)


class UserHistoryModelDao():

    # 获取指定用户历史状态
    @staticmethod
    def get_user_history(uid, state: UserHistory):
        i_c = HistoryCounter()
        return i_c._get_user_info(uid, state)

    # 获取用户全部历史状态
    @staticmethod
    def get_all_user_history(uid):
        i_c = HistoryCounter()
        li = i_c._query_user_info(uid)
        map = {i[0]: i[1] for i in li}
        result_map = {}
        for i in UserHistory:
            result_map[i] = 0
            if map.get(i.value[0]):
                result_map[i] = map.get(i.value[0])
        return result_map

    # 存储指定用户历史状态
    @staticmethod
    def save_user_history(uid, state: UserHistory, num):
        i_c = HistoryCounter()
        i_c._save_user_info(uid, state, num)

    # 指定用户历史状态+num
    @staticmethod
    def add_user_history(uid, state: UserHistory, num=1):
        i_c = HistoryCounter()
        base = i_c._get_user_info(uid, state)
        i_c._save_user_info(uid, state, base + num)

    # 留存历史
    @staticmethod
    def cal_history(user: AllUserInfo):
        # 记录最大等级
        his_map = UserHistoryModelDao.get_all_user_history(user.uid)
        if his_map.get(UserHistory.MAX_GRADE) < user.grade:
            UserHistoryModelDao.save_user_history(user.uid, UserHistory.MAX_GRADE, user.level)
        # 留存灵石
        UserHistoryModelDao.save_user_history(user.uid, UserHistory.RESTART_LINGSHI, int(user.lingshi / 2))
        # 随机留存一个身上的道具
        counter = XiuXianCounter()
        items = counter._get_item(user.gid, user.uid)
        if items:
            i = random.choice(items)
            item = ITEM_INFO[str(i[0])]
            UserHistoryModelDao.save_user_history(user.uid, UserHistory.RESTART_ITEM, int(item['id']))
        else:
            UserHistoryModelDao.save_user_history(user.uid, UserHistory.RESTART_ITEM, 0)
        # 更新历史最高血量
        if his_map.get(UserHistory.MAX_HP) < user.battle_hp:
            UserHistoryModelDao.save_user_history(user.uid, UserHistory.MAX_HP, user.battle_hp)
        # 更新历史最高蓝量
        if his_map.get(UserHistory.MAX_MP) < user.battle_mp:
            UserHistoryModelDao.save_user_history(user.uid, UserHistory.MAX_MP, user.battle_mp)
        # 更新历史最高物攻
        if his_map.get(UserHistory.MAX_ATK1) < user.battle_atk1:
            UserHistoryModelDao.save_user_history(user.uid, UserHistory.MAX_ATK1, user.battle_atk1)
        # 更新历史最高魔攻
        if his_map.get(UserHistory.MAX_ATK2) < user.battle_atk2:
            UserHistoryModelDao.save_user_history(user.uid, UserHistory.MAX_ATK2, user.battle_atk2)
        # 更新历史最高物防
        if his_map.get(UserHistory.MAX_DEFEND1) < user.battle_defen1:
            UserHistoryModelDao.save_user_history(user.uid, UserHistory.MAX_DEFEND1, user.battle_defen1)
        # 更新历史最高术防
        if his_map.get(UserHistory.MAX_DEFEND2) < user.battle_defen2:
            UserHistoryModelDao.save_user_history(user.uid, UserHistory.MAX_DEFEND2, user.battle_defen2)
        # 留存的能力
        ability_name = random.choice(user.ability)
        ability = get_ability_by_name(ability_name)
        UserHistoryModelDao.save_user_history(user.uid, UserHistory.RESTART_ABILITY, int(ability['id']))


class UserDao():
    # 角色死亡
    @staticmethod
    def delete_user(user):
        # 储存历史信息
        UserHistoryModelDao.cal_history(user)
        ct = XiuXianCounter()
        # 删除角色基本信息
        ct._del_user(user.uid)
        # 删除角色状态
        for i in UserModel:
            UserModelDao.save_user_counter(user.uid, i, 0)
        # 删除角色物品
        counter = XiuXianCounter()
        items = counter._get_item(user.gid, user.uid)
        for i in items:
            item = ITEM_INFO[str(i[0])]
            num = i[1]
            ItemDao.use_item(user.uid, item, num)
        # 删除上架物品
        it = XiuXianCounter()
        it._del_trade_info(user.uid)
        # 进入死亡cd
        die_flmt.start_cd(user.uid)

    # 获取角色信息
    @staticmethod
    def get_full_user(uid):
        ct = XiuXianCounter()
        user = ct._get_user(uid)
        if not user:
            return None
        return AllUserInfo(user)

    # 获取当前环境下的角色信息
    @staticmethod
    async def get_ev_user(bot, ev):
        uid = ev.user_id
        user = UserDao.get_full_user(uid)
        if not user:
            await bot.finish(ev, "江湖上还没有过您的传说，请先注册账号")
        return user

    @staticmethod
    def init_user(uid, name):
        from .engine.reincarnation import his_buff
        user = UserInfo()
        user.uid = uid  # qq号
        user.name = name  # 名称
        user.magic_root = random_magic_root()  # 灵根
        user.exp = 0  # 经验
        user.grade = 1  # 大境界
        user.level = 1  # 小境界
        user.local = "新手村"  # 所在地点
        user.belong = "散修"  # 门派
        user.arms = "无"  # 武器
        user.armor = "无"  # 防具
        user.magic_weapon = "无"  # 法宝
        user.attr = UserAttr.init_attr()  # 初始化属性
        user.ability = "[]"  # 能力
        user.other = "{}"  # 其他
        ct = XiuXianCounter()
        ct._save_user_info(user)
        user = AllUserInfo(user)
        spec = his_buff(user)
        user.save_user()
        return user, spec


# 随机获得灵根
def random_magic_root():
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


# 获取法宝
def get_fabao_by_name(name):
    return FABAO_INFO.get(name)


# 依据名称获取能力
def get_ability_by_name(name):
    return ABILITY_NAME_MAP.get(name)

# 依据id获取能力
def get_ability_by_id(id):
    return ABILITY_INFO.get(str(id))

# 筛选道具名称
def filter_item_name(type=[], level=[]):
    result = [i for i in ITEM_NAME_MAP.keys()]
    if type:
        result = [i for i in result if ITEM_NAME_MAP[i]['type'] in type]
    if level:
        result = [i for i in result if ITEM_NAME_MAP[i]['level'] in level]
    return result
