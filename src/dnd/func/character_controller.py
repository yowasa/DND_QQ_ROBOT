import os
from os import path
from ruamel import yaml
import dice
from config.config import *
import user_controller
from user_dto import *
from character_dto import *

# 预定路径
data_path = path.dirname(path.dirname(path.dirname(__file__))) + '/dataSource/character/'


# 初始化一组属性
def init_attribute():
    attribute = {}
    for name in ATTRIBUTE:
        attr = gen_one_attribute()
        attribute[name] = attr
    return attribute


# 随机生成一个属性值4d6取3
def gen_one_attribute():
    test = [dice.range(6), dice.range(6), dice.range(6), dice.range(6)]
    test.sort(reverse=True)
    print(test)
    return test[0] + test[1] + test[2]


# 生成一个角色
def gen_user(user_id, name):
    user = user_controller.get_user(user_id)
    if user is None:
        user = User({})
        user.user_id = user_id
    if name in user.user_list:
        return f'角色 {name} 已存在，请先删除'
    user.current_character = name
    user.user_list = list(user.user_list).append(name) if user.user_list else [name]

    cha = Charater({})
    cha.name = name
    cha.base_attr = init_attribute()
    cha.re_roll_time = 4
    cha.refresh()
    user_controller.save_user(user)
    save_charater(user_id, cha)
    return f'生成角色 {name} 成功\n初始属性为 {formateUtil.formate_dic(attr)}\n可重roll次数为{re_roll_time}'


# 保存角色
def save_charater(user_id, cha):
    user_id = str(user_id)
    name = str(cha.name)
    y_path = data_path + user_id + name + '.yaml'
    dic = formate.obj_2_dic(cha)
    with open(y_path, "w", encoding="utf-8") as f:
        yaml.dump(dic, f, Dumper=yaml.RoundTripDumper, allow_unicode=True)


# 获取角色
def get_charater(user_id, character_name):
    try:
        user_id = str(user_id)
        character_name = str(character_name)
        y_path = data_path + user_id + character_name + '.yaml'
        a = open(y_path, "r", encoding='utf-8')
        dic = yaml.load(a.read(), Loader=yaml.Loader)
        if dic is None or dic:
            return None
        return Charater(dic)
    except:
        return None
