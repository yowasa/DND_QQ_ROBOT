import os
from os import path
from ruamel import yaml
from user_dto import *
import formate

# 预定路径
data_path = path.dirname(path.dirname(path.dirname(__file__))) + '/dataSource/user/'


# 获取用户信息
def get_user(user_id):
    try:
        user_id = str(user_id)
        y_path = data_path + user_id + '.yaml'
        dic={}
        with open(y_path, "r", encoding='utf-8') as a:
            dic = yaml.load(a.read(), Loader=yaml.Loader)
        if dic is None or not dic:
            return None
        return User(dic)
    except:
        return None


# 保存用户信息
def save_user(user):
    user_id = str(user.user_id)
    y_path = data_path + user_id + '.yaml'
    dic = formate.obj_2_dic(user)
    with open(y_path, "w", encoding="utf-8") as f:
        yaml.dump(dic, f, Dumper=yaml.RoundTripDumper, allow_unicode=True)
