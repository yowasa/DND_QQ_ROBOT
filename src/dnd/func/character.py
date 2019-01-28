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
    refresh(user_id,content)
    return f'生成角色 {name} 成功\n初始属性为 {formateUtil.formate_dic(attr)}\n可重roll次数为{re_roll_time}'


# def swap(user_id,attr1,attr2):


# 更新人物信息 user_name=None更新当前用户信息，set_current=True 设置user_name为当前用户
def update_user(user_id, content, user_name=None, set_current=True):
    user_id = str(user_id)
    y_path = data_path + user_id + '.yaml'
    if not os.path.exists(y_path):  # 判断当前路径是否存在，没有则创建new文件夹
        file = open(y_path, 'w')
        file.close()
    a = open(y_path, "r",encoding='utf-8')
    dic = yaml.load(a.read(), Loader=yaml.Loader)
    print(dic)
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
        yaml.dump(dic, f, Dumper=yaml.RoundTripDumper,allow_unicode=True)


# 获取人物信息
def get_user_info(user_id, user_name):
    try:
        user_id = str(user_id)
        y_path = data_path + user_id + '.yaml'
        a = open(y_path, "r",encoding='utf-8')
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
        a = open(y_path, "r",encoding='utf-8')
        dic = yaml.load(a.read(), Loader=yaml.Loader)
        return dic
    except:
        return None


def update_base_user_info(user_id, content):
    user_id = str(user_id)
    y_path = data_path + user_id + '.yaml'
    if not os.path.exists(y_path):  # 判断当前路径是否存在，没有则创建new文件夹
        file = open(y_path, 'w')
        file.close()
    dic = content
    with open(y_path, "w", encoding="utf-8") as f:
        yaml.dump(dic, f, Dumper=yaml.RoundTripDumper,allow_unicode=True)


# 刷新属性
def refresh(user_id, user):
    user_race = user.get('race')
    user_sub_race = user.get('sub_race')
    user_job = user.get('race')
    current_attr = user.get('attribute').copy()
    race_skill = []
    skilled_weapon = []
    skilled_eq = []
    pc_op = {}
    # 种族基础属性解析
    if user_race is not None:
        race_des = RACE_DESCRIBE.get(user_race)
        user['speed'] = race_des.get('speed')
        base_attr_up = race_des.get('attr')
        print(current_attr)
        for k, v in base_attr_up.items():
            if k =='random':
                sb = f'你可以使用.attrup选择{v}项属性进行提升'
                pc_op['attr_up'] = {'num':2,'reason':'种族特性','msg':sb}
                pass
            else:
                current_attr[k] = current_attr.get(k) + v
        print(current_attr)
        user['language'] = race_des.get('language')
        base_race_skill = race_des.get('ex_skill')
        race_skill += base_race_skill
        race_skilled_skilled_weapon = race_des.get('skilled_weapon')
        skilled_weapon += race_skilled_skilled_weapon if race_skilled_skilled_weapon is not None else []
        if user_sub_race is not None:
            ex_race = race_des.get('ex_race')
            if ex_race is None:
                user.pop('sub_race')
            else:
                # 亚种属性解析
                if user_sub_race in ex_race:
                    sub_race = ex_race.get(user_sub_race)
                    sub_race_attr_up = sub_race.get('attr')
                    for k, v in sub_race_attr_up.items():
                        current_attr[k] = current_attr.get(k) + v
                    sub_race_skill = sub_race.get('ex_skill')
                    race_skill += sub_race_skill
                    sub_race_skilled_weapon = sub_race.get('skilled_weapon')
                    skilled_weapon += sub_race_skilled_weapon if sub_race_skilled_weapon is not None else []
                else:
                    user.pop('sub_race')
        else:
            ex_race = race_des.get('ex_race')
            if ex_race is not None:
                pc_op['select_sub_job'] = True
                sb = f'你可以使用.subrace选择{user_race}的亚种：'
                for k, v in ex_race.items():
                    sb += k + ' '
                pc_op['select_sub_job'] = {'status':True,'msg':sb}
    # 鉴定属性生成
    check_list=refresh_check_list(current_attr)
    # 技能解析
    for s in race_skill:
        if s=='额外语言':
            pc_op['select_language']={'num':1,'msg':'你可以使用.language 请选择1门额外语言'}
        if s=='矮人的盔甲训练':
            skilled_eq+=['轻甲','中甲']
        if s=='轻捷步伐':
            user['speed']+=5

    # 可执行变更动作解析
    # 存储数据
    user['cur_attr'] = current_attr
    user['race_skill'] = race_skill
    user['skilled_weapon'] = skilled_weapon
    user['skilled_eq'] = skilled_eq
    user['check_attr'] = check_list
    user['pc_op'] = pc_op
    update_user(user_id, user)

#刷新鉴定属性
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
