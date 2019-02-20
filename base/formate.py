# 所有转化相关函数
from tool.dnd_db import *


# 对象转字典
def obj_2_dic(obj):
    pr = {}
    for name in dir(obj):
        value = getattr(obj, name)
        seqs = tuple, list, set, frozenset, dict, str, int, float, bool, complex
        if not name.startswith('__') and not callable(value):
            if not isinstance(value, seqs) and value is not None:
                value = obj_2_dic(value)
            if value is not None:
                pr[name] = value
    return pr


# 输出字典
def formate_dic(attr):
    attr_msg = str(attr)
    attr_msg = attr_msg.replace('{', '')
    attr_msg = attr_msg.replace('}', '')
    attr_msg = attr_msg.replace('\'', '')
    return attr_msg


# 输出列表
def formate_list(attr):
    attr_msg = str(attr)
    attr_msg = attr_msg.replace('[', '')
    attr_msg = attr_msg.replace(']', '')
    attr_msg = attr_msg.replace('(', '')
    attr_msg = attr_msg.replace(')', '')
    attr_msg = attr_msg.replace('\'', '')
    return attr_msg


attr_ref = {
    'str': '力量',
    'dex': '敏捷',
    'con': '体质',
    'int': '智力',
    'wis': '感知',
    'cha': '魅力'
}
attr_dict_ref = {
    '力量': 'str',
    '敏捷': 'dex',
    '体质': 'con',
    '智力': 'int',
    '感知': 'wis',
    '魅力': 'cha'
}


def attr_key2des(key):
    return attr_ref.get(key)


def attr_des2key(key):
    return attr_dict_ref.get(key)


# 属性字典转对象
def dict2attr(attr_dict):
    attr = Attribute()
    for k, v in attr_dict.items():
        obj_attr = attr_dict_ref.get(k)
        setattr(attr, obj_attr, v)
    return attr


# 属性对象转字典
def attr2dict(attr):
    dict = {}
    for k, v in attr_ref.items():
        obj_value = getattr(attr, k)
        dict[v] = obj_value
    return dict


# 属性字典转描述
def attr_dict2str(attr):
    total = 0
    for v in attr.values():
        total += v
    return f'{formate_dic(attr)}, 属性和为{str(total)}{", SSR!" if total>90 else ""}{", RSS!" if total<55 else ""}'
