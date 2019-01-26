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
    ex_msg=''
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
    dic=character.get_base_user_info(user_id)
    jrrp_date=dic.get('jrrp_date')
    date = time.strftime("%Y-%m-%d")
    if jrrp_date is None or jrrp_date!=date:
        dic['jrrp_date']=date
        value=diceUtil.range(101)-1
        dic['jrrp_value']=value
        character.update_base_user_info(user_id,dic)
    jrrp_value = dic.get('jrrp_value')
    return f'{nickname} 今天的人品是{jrrp_value}%！！！！！！！！！！'


