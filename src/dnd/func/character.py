import os
from os import path
from ruamel import yaml
import diceUtil
from config import *
import formateUtil

# 预定路径
data_path = path.dirname(path.dirname(path.dirname(__file__))) + '/dataSource/'


# 初始化一组属性
def init_attribute():
    attribute = {}
    for name in ATTRIBUTE:
        attr = gen_one_attribute()
        attribute[name] = attr
    return attribute


# 随机生成一个属性值4d6取3
def gen_one_attribute():
    test = [diceUtil.range(6), diceUtil.range(6), diceUtil.range(6), diceUtil.range(6)]
    test.sort(reverse=True)
    print(test)
    return test[0] + test[1] + test[2]


# 生成一个人物 todo 后续增加其他属性功能，现阶段只有骰属性
def gen_user(user_id, name):
    user = get_user_info(user_id, name)
    if user is not None:
        return f'角色 {name} 已存在，请先删除'
    content = {'name': name, 'status': 'gen'}
    attr = init_attribute()
    content['attribute'] = attr
    re_roll_time = 4
    content['re_roll_time'] = re_roll_time
    msg = update_user(user_id, content, user_name=name)
    return f'生成角色 {name} 成功\n初始属性为 {formateUtil.formate_dic(attr)}\n可重roll次数为{re_roll_time}'


# def swap(user_id,attr1,attr2):


# 更新人物信息 user_name=None更新当前用户信息，set_current=True 设置user_name为当前用户
def update_user(user_id, content, user_name=None, set_current=True):
    user_id = str(user_id)
    y_path = data_path + user_id + '.yaml'
    if not os.path.exists(y_path):  # 判断当前路径是否存在，没有则创建new文件夹
        file = open(y_path, 'w', encoding='utf-8')
        file.close()
    a = open(y_path, "r", encoding='utf-8')
    dic = yaml.load(a.read(), Loader=yaml.Loader)
    if dic is None:
        dic = {}
        dic['current_user'] = user_name
        dic['user_list'] = []
        dic['user_list'].append(user_name)
    if user_name is None:
        user_name = dic['current_user']
    if set_current:
        dic['current_user'] = user_name
    user_list = dic.get('user_list')
    if user_list is None:
        user_list = []
        dic['user_list'] = user_list
    if user_name is not None and user_name not in user_list:
        dic['user_list'].append(user_name)
    dic[user_name] = content
    with open(y_path, "w", encoding="utf-8") as f:
        yaml.dump(dic, f, Dumper=yaml.RoundTripDumper, encoding="utf-8", default_flow_style=False, allow_unicode=True)


# 获取人物信息
def get_user_info(user_id, user_name):
    try:
        user_id = str(user_id)
        y_path = data_path + user_id + '.yaml'
        a = open(y_path, "r", encoding='utf-8')
        dic = yaml.load(a.read(), Loader=yaml.Loader)
        if user_name is not None:
            return dic.get(user_name)
        return dic.get(dic.get('current_user'))
    except:
        return None


# 获取当前人物信息
def get_current_user_info(user_id):
    return get_user_info(user_id, None)


def get_base_user_info(user_id):
    try:
        user_id = str(user_id)
        y_path = data_path + user_id + '.yaml'
        a = open(y_path, "r", encoding='utf-8')
        dic = yaml.load(a.read(), Loader=yaml.Loader)
        return dic
    except:
        return None


def update_base_user_info(user_id, content):
    user_id = str(user_id)
    y_path = data_path + user_id + '.yaml'
    if not os.path.exists(y_path):  # 判断当前路径是否存在，没有则创建new文件夹
        file = open(y_path, 'w', encoding='utf-8')
        file.close()
    dic = content
    with open(y_path, "w", encoding="utf-8") as f:
        yaml.dump(dic, f, Dumper=yaml.RoundTripDumper)
