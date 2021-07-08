import json
import os
import random
import re
import time
from enum import Enum
from peewee import *
from hoshino.modules.dnd.DndSearchCounter import *
from PIL import Image, ImageDraw, ImageFont
from hoshino.typing import CommandSession
from hoshino import R
from hoshino import Service
from hoshino.config.__bot__ import BASE_DB_PATH
from hoshino.typing import CQEvent, MessageSegment as Seg

sv = Service('DND', enable_on_default=True, bundle='跑团', help_=
'''
[!dnd] {数量} 生成指定个数的dnd5e规则下的6维属性 不超过20
[.dr] {搜索内容} dnd5e信息查询
[.name] {数量} 随机名称 最多不超过20个

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


@sv.on_prefix(['.name', '。name'])
async def random_name(bot, ev: CQEvent):
    cmd_msg = str(ev.message).strip()
    num = 1
    if cmd_msg:
        if not cmd_msg.isdigit():
            await bot.finish(ev, f'[CQ:at,qq={ev.user_id}]请输入一个数字')
        num = int(cmd_msg)
        if num > 20:
            await bot.finish(ev, f'[CQ:at,qq={ev.user_id}]单次生成不得高于20次')

    n1 = random.randint(0, num)
    n2 = random.randint(0, num - n1)
    n3 = num - n1 - n2
    li = [n1, n2, n3]
    random.shuffle(li)
    ds = DndSearchCounter()
    result_li = []
    result_li.extend(ds._radom_cn_name(li[0]))
    result_li.extend(ds._radom_en_name(li[1]))
    result_li.extend(ds._radom_jp_name(li[2]))
    sb = '[CQ:at,qq={ev.user_id}] 生成的名称为：\n'
    sb += '\n'.join(result_li)
    await bot.send(ev, sb)


@sv.on_prefix(['.dr', '。dr'])
async def dnd_search(session: CommandSession):
    bot = session.bot
    ev = session.event
    cmd_msg = str(ev.message).strip()
    ds = DndSearchCounter()
    result_li = []
    result_li.extend(ds._search_skill(cmd_msg))
    result_li.extend(ds._search_armor(cmd_msg))
    result_li.extend(ds._search_classes(cmd_msg))
    result_li.extend(ds._search_feat(cmd_msg))
    result_li.extend(ds._search_races(cmd_msg))
    result_li.extend(ds._search_rule(cmd_msg))
    result_li.extend(ds._search_tools(cmd_msg))
    result_li.extend(ds._search_spell_list(cmd_msg))
    result_li.extend(ds._search_magic_items(cmd_msg))
    result_li.extend(ds._search_rule_dmg(cmd_msg))
    result_li.extend(ds._search_background(cmd_msg))
    result_li.extend(ds._search_mm(cmd_msg))
    if len(result_li) > 1:
        msg = '查询结果存在多个，请在3分钟以内回复清单的数字来查阅内容:'
        if len(result_li) > 20:
            msg += "最多显示20条数据。如果需要查询更多信息，请前往网站查询：https://eiriksgata.github.io/rulateday-dnd5e-wiki/#/"
        for i in range(20):
            msg += f'\n{i + 1}. {result_li[i][1]}'
        aliases_str = session.get('number', prompt=msg)
        if not str(aliases_str).strip().isdigit():
            await bot.finish(ev, "无法识别输入内容")
        num = int(str(aliases_str).strip()) - 1
        # TODO 匹配前五个字符为怪物图鉴: 做额外下载图片展示的处理
        detail = result_li[num][2].replace('\n\n', '\n')
        msg = f"{result_li[num][1]}:\n{detail}"
        await bot.finish(ev, msg)
    else:
        if len(result_li) == 0:
            await bot.finish(ev, "未搜索到结果")
        # TODO 匹配前五个字符为怪物图鉴: 做额外下载图片展示的处理
        detail = result_li[0][2].replace('\n\n', '\n')
        msg = f"{result_li[0][1]}:\n{detail}"
        await bot.finish(ev, msg)


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
