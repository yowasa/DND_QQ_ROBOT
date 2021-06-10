import re
import time
import random
from filter import msg_route
from base.formate import *
from tool.dnd_db import *

'''
骰子相关功能
!dnd 随机生成dnd5e规则下的6维属性，可以指定次数 不得超过20次
.rd20 骰一个20面骰子，支持自定义骰子面数，及指定鉴定加成，例:.r4#d30+4 骰4次30面骰，每次结果加4
.jrrp 今日人品功能，检查今天的人品
.check 过鉴定 鉴定某项属性
'''

# 人物属性
ATTRIBUTE = ['力量', '体质', '敏捷', '智力', '感知', '魅力']


# 1-n随机值
def random_value(num):
    return random.randint(1, num)


# 随机生成一个属性值4d6取3
def gen_one_attribute():
    test = [random_value(6), random_value(6), random_value(6), random_value(6)]
    test.sort(reverse=True)
    return test[0] + test[1] + test[2]


# 初始化一组属性
def init_attribute():
    attribute = {}
    for name in ATTRIBUTE:
        attr = gen_one_attribute()
        attribute[name] = attr
    return attribute


# 替换骰子命令为具体的值
def replace_dice(str):
    list = str.split('d')
    count = 1
    if list[0] != '':
        count = int(list[0])
    dice = 20
    if list[1] != '':
        dice = int(list[1])

    result = 0
    for i in range(0, count):
        result += random_value(dice)
    return result


# 生成属性并展示
@msg_route(r'(!|！)dnd')
def random_attribute(content):
    cmd_msg = content['cmd_msg']
    num = 1
    if cmd_msg:
        if not cmd_msg.isdigit():
            return '请输入一个数字'
        num = int(cmd_msg)
        if num > 20:
            return '单次生成不得高于20次'
    sb = ''
    for _ in range(num):
        attr = init_attribute()
        sb += attr_dict2str(attr) + '\n'
    return sb[:-1]


# 用于通用处理骰子指令
@msg_route(r'\s*\.r(?=\d*d|\d*#)', need_character=True)
def dice_ex(content):
    # 获得用户
    nickname = content['sender']['nickname']
    character = content.get('sys_character')
    user_name = character.name if character else nickname
    cmd_msg = content['cmd_msg']
    # 获得骰子后命令说明
    ex_msg = ''
    if ' ' in cmd_msg.strip():
        msgs = cmd_msg.split(' ')
        ex_msg = msgs[1].strip()
        cmd_msg = msgs[0].strip()
    count = 1
    all_msg = cmd_msg
    if '#' in cmd_msg.strip():
        msgs = cmd_msg.split('#')
        count = msgs[0].strip()
        cmd_msg = msgs[1].strip()
    patt = re.compile(r'\d*d\d*')
    if count == 1:
        result = re.sub(patt, lambda m: str(replace_dice(m.group(0))), cmd_msg)
        dice_result = eval(result)
        return f'{user_name} 骰点 {ex_msg} {all_msg}=({result}) = {dice_result}'
    else:
        result_list = []
        for i in range(0, int(count)):
            result = re.sub(patt, lambda m: str(replace_dice(m.group(0))), cmd_msg)
            dice_result = eval(result)
            result_list.append(dice_result)
        return f'{user_name} 骰点 {ex_msg} {all_msg} = {result_list}'


# 检定功能
@msg_route(r'\s*\.check ', need_character=True)
def check(content):
    nickname = content['sender']['nickname']
    user = content.get('sys_user')
    character = content.get('sys_character')
    if not character:
        return f'{nickname} 请先创建角色'
    if character.status < 100:
        return f'{nickname} 请先创建完成{character.name}角色,使用.guide查看创建指引'

    check_attr = character.cur_check
    cmd_msg = content['cmd_msg']
    if ' ' in cmd_msg:
        c_list = cmd_msg.split(' ')
        checked_attr = c_list[1]
        if checked_attr not in check_attr:
            return f'检定项 {checked_attr} 不存在'
    else:
        return f'请输入检定项'

    cmd_msg = c_list[0]
    double_flag = 0
    if '*' in cmd_msg:
        patt1 = re.compile(r'(?<=\*)\d*')
        patt2 = re.compile(r'\*\d*')
        match = re.findall(patt1, cmd_msg)[0]
        match = 0 if match is None or match == '' else match
        double_flag = int(match)
        cmd_msg = re.sub(patt2, '', cmd_msg)
    elif '/' in cmd_msg:
        patt1 = re.compile(r'(?<=\/)\d*')
        patt2 = re.compile(r'\/\d*')
        match = re.findall(patt1, cmd_msg)[0]
        match = 0 if match is None or match == '' else match
        double_flag = -int(match)
        cmd_msg = re.sub(patt2, '', cmd_msg)
    # 得到加值
    add_value = int(check_attr.get(checked_attr))

    pre_msg = ''
    low_flag = False
    if double_flag == 0 or double_flag == 1 or double_flag == -1:
        pass
    elif double_flag > 1:
        pre_msg = f'{double_flag}#'
    elif double_flag < -1:
        pre_msg = f'{-int(double_flag)}#'
        low_flag = True
    all_msg = f'{pre_msg}d20+({add_value})' + cmd_msg

    work_msg = all_msg
    count = 1
    if '#' in work_msg.strip():
        msgs = work_msg.split('#')
        count = msgs[0].strip()
        work_msg = msgs[1].strip()
    patt = re.compile(r'\d*d\d{1,100}')
    if count == 1:
        result = re.sub(patt, lambda m: str(replace_dice(m.group(0))), work_msg)
        dice_result = eval(result)
        return f'{character.name} 检定 {checked_attr} {all_msg}=({result}) = {dice_result}'
    else:
        result_list = []
        for i in range(0, int(count)):
            patt = re.compile(r'\d*d\d{1,100}')
            result = re.sub(patt, lambda m: str(replace_dice(m.group(0))), work_msg)
            dice_result = eval(result)
            result_list.append(dice_result)
        print(result_list)
        if low_flag:
            result_list.sort()
            best_msg = '取最低值' + str(result_list[0])
        else:
            result_list.sort()
            sort_list = result_list[::-1]
            print(sort_list)
            best_msg = '取最高值' + str(sort_list[0])

        return f'{character_name} 检定 {checked_attr} {all_msg} = {result_list} {best_msg}'
