import diceUtil
import character
import re
import time

from config import *


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
        result += diceUtil.range(dice)
    return result


# 用于通用处理骰子指令
def dice_ex(content):
    # 获得用户
    sender = content['sender']
    nickname = sender['nickname']
    user_id = sender['user_id']
    user_name = nickname
    user_info = character.get_current_user_info(user_id)
    print(user_info)
    if user_info is not None:
        user_name = user_info['name']

    cmd_msg = content['message']
    cmd_msg = cmd_msg.replace('.r', '')
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
    patt = re.compile(r'\d*d\d{1,100}')
    if count == 1:
        result = re.sub(patt, lambda m: str(replace_dice(m.group(0))), cmd_msg)
        dice_result = eval(result)
        return f'{user_name} 骰点 {ex_msg} {all_msg}=({result}) = {dice_result}'
    else:
        result_list = []
        for i in range(0, int(count)):
            patt = re.compile(r'\d*d\d{1,100}')
            result = re.sub(patt, lambda m: str(replace_dice(m.group(0))), cmd_msg)
            dice_result = eval(result)
            print(dice_result)
            result_list.append(dice_result)
        return f'{user_name} 骰点 {ex_msg} {all_msg} = {result_list}'


def jrrp(content):
    sender = content['sender']
    nickname = sender['nickname']
    user_id = sender['user_id']
    dic = character.get_base_user_info(user_id)
    if dic is None:
        dic = {}
    jrrp_date = dic.get('jrrp_date')
    date = time.strftime("%Y-%m-%d")
    if jrrp_date is None or jrrp_date != date:
        dic['jrrp_date'] = date
        value = diceUtil.range(101) - 1
        dic['jrrp_value'] = value
        character.update_base_user_info(user_id, dic)
    jrrp_value = dic.get('jrrp_value')
    return f'{nickname} 今天的运势是{jrrp_value}%！！！！！！！！！！'


def check(content):
    sender = content['sender']
    nickname = sender['nickname']
    user_id = sender['user_id']
    user = character.get_current_user_info(user_id)
    if user is None:
        return f'{nickname} 请先创建角色'
    user_name = user.get('name')
    check_attr = user.get('check_attr')
    cmd_msg = content['message']
    cmd_msg = cmd_msg.replace('.check', '')
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

    print('doubleflag',double_flag)
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
    print(work_msg)
    if '#' in work_msg.strip():
        msgs = work_msg.split('#')
        print(msgs)
        count = msgs[0].strip()
        work_msg = msgs[1].strip()
    patt = re.compile(r'\d*d\d{1,100}')
    if count == 1:
        result = re.sub(patt, lambda m: str(replace_dice(m.group(0))), work_msg)
        dice_result = eval(result)
        return f'{user_name} 检定 {checked_attr} {all_msg}=({result}) = {dice_result}'
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

        return f'{user_name} 检定 {checked_attr} {all_msg} = {result_list} {best_msg}'
