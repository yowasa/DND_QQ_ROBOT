import json
import os
import random
import re
import time
from enum import Enum
from peewee import *

from PIL import Image, ImageDraw, ImageFont

from hoshino import R
from hoshino import Service
from hoshino.config.__bot__ import BASE_DB_PATH
from hoshino.typing import CQEvent, MessageSegment as Seg

sv = Service('DND', enable_on_default=True, bundle='跑团', help_=
'''
[!dnd] {数量} 生成指定个数的dnd5e规则下的6维属性 不超过20
[.dr] {搜索内容} dnd5e信息查询

''')
ATTRIBUTE = ['力量', '体质', '敏捷', '智力', '感知', '魅力']


# 生成属性并展示
@sv.on_prefix(['!dnd', '！dnd'])
async def random_attribute(bot, ev: CQEvent):
    cmd_msg = str(ev.message).strip()
    num = 1
    if cmd_msg:
        if not cmd_msg.isdigit():
            await bot.finish(ev, f'[CQ:at,qq={ev.user_id}]请输入一个数字')
        num = int(cmd_msg)
        if num > 20:
            await bot.finish(ev, f'[CQ:at,qq={ev.user_id}]单次生成不得高于20次')
    sb = '[CQ:at,qq={ev.user_id}] 生成的属性为：\n'
    for _ in range(num):
        attr = init_attribute()
        sb += attr_dict2str(attr) + '\n'
    await bot.send(ev, sb[:-1])


# 初始化一组属性
def init_attribute():
    attribute = {}
    for name in ATTRIBUTE:
        attr = gen_one_attribute()
        attribute[name] = attr
    return attribute


# 随机生成一个属性值4d6取3
def gen_one_attribute():
    test = [random_value(6), random_value(6), random_value(6), random_value(6)]
    test.sort(reverse=True)
    return test[0] + test[1] + test[2]


# 1-n随机值
def random_value(num):
    return random.randint(1, num)


# 属性字典转描述
def attr_dict2str(attr):
    total = 0
    for v in attr.values():
        total += v
    return f'{formate_dic(attr)}, 属性和为{str(total)}{", SSR!" if total > 90 else ""}{", RSS!" if total < 55 else ""}'


# 输出字典
def formate_dic(attr):
    attr_msg = str(attr)
    attr_msg = attr_msg.replace('{', '')
    attr_msg = attr_msg.replace('}', '')
    attr_msg = attr_msg.replace('\'', '')
    return attr_msg
