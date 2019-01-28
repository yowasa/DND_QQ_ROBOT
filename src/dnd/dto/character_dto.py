import formate
from config.character_config import *
from config.base_config import *


# 角色实体类
class Charater:
    def __init__(self, context):
        # ###基础信息###
        # 姓名
        self.name = context.get('name')
        # 性别
        self.sex = context.get('sex')
        # 阵营
        self.camp = context.get('camp')
        # 语言
        self.language = context.get('language')
        # 状态
        self.status = context.get('status')
        # 允许重新roll点次数
        self.re_roll_time = context.get('re_roll_time')
        # 种族
        self.race = Race(context.get('race'))
        # 职业 todo 职业未实现
        self.job = Job(context.get('job'))
        # 背景
        self.background = Background(context.get('background'))
        # 等级信息
        self.level_info = LevelInfo(context.get('level_info'))
        # 熟练项
        self.skilled_item = context.get('skilled_item')
        # 熟练工具
        self.skilled_tool = context.get('skilled_tool')
        # 熟练武器
        self.skilled_weapon = context.get('skilled_weapon')
        # 熟练盔甲
        self.skilled_armour = context.get('skilled_armour')
        # 基础属性
        self.base_attr = context.get('base_attr')
        # 当前属性（受升级影响）
        self.cur_attr = context.get('cur_attr')
        # 基础检定
        self.base_check = context.get('base_check')
        # 当前检定（受状态影响）
        self.cur_check = context.get('cur_check')
        # 速度
        self.speed = context.get('speed')
        # 临时状态
        self.ex_status = context.get('ex_status')
        # 金钱
        self.fortune = Fortune(context.get('gold'))
        # 物品
        # 装备
        # 通知
        self.notice = context.get('notice')
        # log
        self.log = context.get('log')

    def refresh(self):
        self.refresh_base()
        self.refresh_race()
        self.refresh_job()
        self.refresh_background()
        self.refresh_check()

    # 同步基本信息
    def refresh_base(self):
        self.cur_attr = self.base_attr.copy()
        self.cur_check = self.base_check.copy()

    # 同步种族信息
    def refresh_race(self):
        if self.race is None:
            return
        race_des = RACE_DESCRIBE.get(self.race)
        self.speed = race_des.get('speed')
        base_attr_up = race_des.get('attr')
        for k, v in base_attr_up.items():
            if k == 'random':
                sb = f'你可以使用.attrup选择{v}项属性进行提升'
                self.notice['attr_up'] = {'num': v, 'reason': '种族特性', 'msg': sb}
                pass
            else:
                self.cur_attr[k] += v
        self.language = race_des.get('language')
        self.race.race_skill = list(self.race.race_skill).append(
            race_des.get('ex_skill')) if self.race.race_skill else race_des.get('ex_skill')
        self.skilled_weapon = list(self.skilled_weapon).append(
            race_des.get('skilled_weapon')) if self.skilled_weapon else race_des.get('skilled_weapon')
        if self.race.sub_race is not None:
            ex_race = race_des.get('ex_race')
            if ex_race is None:
                self.race.sub_race = None
            else:
                # 亚种属性解析
                if self.race.sub_race in ex_race:
                    sub_race = ex_race.get(self.race.sub_race)
                    sub_race_attr_up = sub_race.get('attr')
                    for k, v in sub_race_attr_up.items():
                        self.cur_attr[k] += v
                    sub_race_skill = sub_race.get('ex_skill')
                    self.race.race_skill += sub_race_skill
                    sub_race_skilled_weapon = sub_race.get('skilled_weapon')
                    self.skilled_weapon = list(self.skilled_weapon).append(
                        sub_race_skilled_weapon) if self.skilled_weapon else sub_race_skilled_weapon
                else:
                    self.race.sub_race = None
        else:
            ex_race = race_des.get('ex_race')
            if ex_race is not None:
                sb = f'你可以使用.subrace选择{self.race}的亚种：'
                for k, v in ex_race.items():
                    sb += k + ' '
                self.notice['select_sub_job'] = {'status': True, 'msg': sb}
        for s in self.race.race_skill:
            if s == '额外语言':
                self.notice['select_language'] = {'num': 1, 'msg': '你可以使用.language 请选择1门额外语言'}
            if s == '矮人的盔甲训练':
                self.skilled_armour += ['轻甲', '中甲']
            if s == '轻捷步伐':
                self.speed += 5

    # 同步职业信息
    def refresh_job(self):
        pass

    # 同步背景信息
    def refresh_background(self):
        pass

    # 刷新检定值
    def refresh_check(self):
        self.base_check = refresh_check_list(self.cur_attr)


# 种族
class Race:
    def __init__(self, context):
        # 种族名称
        self.name = context.get('name')
        # 亚种名称
        self.sub_race = context.get('sub_race')
        # 种族技能
        self.race_skill = context.get('race_skill')


class Job:
    def __init__(self, context):
        # 职业名称
        self.name = context.get('name')


# 背景
class Background:
    def __init__(self, context):
        self.name = context.get('name')


# 等级信息
class LevelInfo:
    def __init__(self, context):
        self.level = context.get('level')
        self.exp = context.get('exp')
        self.skilled_up = context.get('skilled_up')


class Fortune:
    def __init__(self, context):
        self.cp = context.get('cp')
        self.sp = context.get('sp')
        self.ep = context.get('ep')
        self.gp = context.get('gp')
        self.pp = context.get('pp')


context = {'name': '桃毒', 'base_attr': {'力量': 16, '体质': 16, '敏捷': 15, '智力': 10, '感知': 11, '魅力': 8}}
c = Charater(context)

print(formate.obj_2_dic(c))


# 刷新鉴定属性
def refresh_check_list(current_attr):
    check_list = {}
    for att in ATTRIBUTE:
        cur_value = current_attr.get(att)
        check_list[att + '豁免'] = gen_check(cur_value)
    for che in CHECK_CONFIG:
        att = CHECK_REF.get(che)
        cur_value = current_attr.get(att)
        check_list[che] = gen_check(cur_value)
    return check_list


# 生成鉴定属性
def gen_check(attr):
    attr = int(attr)
    if attr - 10 >= 0:
        return int((attr - 10) / 2)
    if attr - 10 < 0:
        return int((attr - 11) / 2)
