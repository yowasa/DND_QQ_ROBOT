# 所有转化相关函数

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
