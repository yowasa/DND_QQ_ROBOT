from . import comm
from .condition import checkCondition

import random


def do_event(user):
    # 获取当前年龄可以执行的event
    events = comm.age_config[str(user.data['年龄'])]
    # 过滤不可执行的event
    matches = [x for x in events.get('event') if check_event(x, user)]
    # 依据权重选取执行的event
    ev_id = choose_ev_id(matches)
    # 执行记录
    desc_li = []
    next = ev_id
    # 如果包含分支则执行分支
    while next:
        effect, next, desc, post = exec_event(user, next)
        # 添加执行记录
        desc_li.append(desc)
        # 如果不包含分支且有post 则加入
        if not next:
            if post:
                desc_li.append(post)
        # 影响角色属性
        comm.buff_user(user, effect)
        # 添加事件经历
        user.data['事件'].append(int(ev_id))
    return '\n'.join(desc_li)


# 检查事件是否可以被执行
def check_event(event_msg, user):
    if "*" in str(event_msg):
        msg_li = event_msg.split("*")
        event_id = int(msg_li[0])
    else:
        event_id = int(event_msg)

    if comm.event_config[str(event_id)].get("NoRandom"):
        return False

    if comm.event_config[str(event_id)].get("exclude"):
        if checkCondition(user, comm.event_config[str(event_id)].get("exclude")):
            return False
    if comm.event_config[str(event_id)].get("include"):
        return checkCondition(user, comm.event_config[str(event_id)].get("include"))
    return True


# 选取事件
def choose_ev_id(matches):
    total_weight = 0
    match_li = []
    for e in matches:
        if "*" in str(e):
            msg_li = e.split("*")
            match_li.append([int(msg_li[0]), float(msg_li[1])])
        else:
            match_li.append([int(e), 1])
    for e in match_li:
        total_weight += e[1]
    rd = random.random()* total_weight
    for e in match_li:
        rd -= e[1]
        if rd <= 0:
            return e[0]
    return matches[len(matches) - 1][0]


def exec_event(user, ev_id):
    event = comm.event_config[str(ev_id)]
    if event.get('branch'):
        for i in event.get('branch'):
            i_li = str(i).split(":")
            condition = i_li[0]
            next = i_li[1]
            if checkCondition(user, condition):
                return event.get('effect'), int(next), event.get('event'), event.get('postEvent')
    return event.get('effect'), None, event.get('event'), event.get('postEvent')
