

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