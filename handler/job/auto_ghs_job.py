# 1.导入模块
from handler.base_handler import ghs_handler as ghs
from tool.dnd_db import Subscribe, SubscribeSendLog

'''
自动ghs功能 提供定时扫描 扫描到的数据储存 然后定时发送的功能
'''


def bulid_context(user_id, user_type):
    context = {}
    context['message_type'] = user_type
    if user_type == 'group':
        context['group_id'] = user_id
        return context
    elif user_type == 'private':
        context['user_id'] = user_id
        return context
    elif user_type == 'discuss':
        context['discuss_id'] = user_id
        return context
    return None


def build_result(subscribe, illusts):
    mapping = {}
    ill_ids = []
    for illust in illusts:
        mapping[illust.get("id")] = illust
        ill_ids.append(illust.get("id"))
    logs = SubscribeSendLog.select().where(
        (SubscribeSendLog.user_id == subscribe.user_id) & (SubscribeSendLog.user_type == subscribe.user_type) & (
                    SubscribeSendLog.message_id in ill_ids))
    for log in logs:
        if log.message_id in ill_ids:
            ill_ids.remove(log.message_id)
    for i in ill_ids:
        illust = mapping.get(i)
        message = ghs.package_pixiv_img(illust, group=True)
        sublog = SubscribeSendLog()
        sublog.user_id = subscribe.user_id
        sublog.user_type = subscribe.user_type
        sublog.clazz = 'pixiv'
        sublog.message_id = i
        sublog.message_info = message
        sublog.send_flag = False
        sublog.save()


def scan_list():
    ghs.pixiv_login()
    # 每日前三十
    results = ghs.api.illust_ranking(mode='day', date=None, offset=None)
    results_r18 = ghs.api.illust_ranking(mode='day_r18', date=None, offset=None)
    result_public = ghs.api.illust_follow(restrict='public')
    result_private = ghs.api.illust_follow(restrict='private')
    query = Subscribe.select().where(Subscribe.clazz == 'pixiv')
    for each in query:
        if each.type == 'day':
            build_result(each, results.illusts)
        if each.type == 'day_r18':
            build_result(each, results_r18.illusts)
        if each.type == 'private':
            build_result(each, result_private.illusts)
        if each.type == 'public':
            build_result(each, result_public.illusts)
        if each.type == 'user':
            results_users = ghs.api.user_illusts(each.type_user)
            build_result(each, results_users.illusts)


def send_list():
    result = []
    query = SubscribeSendLog.select().where(SubscribeSendLog.send_flag == False)
    filter_mapping = []
    for e in query:
        if str(e.user_id) + e.user_type in filter_mapping:
            continue
        filter_mapping.append(str(e.user_id) + e.user_type)
        content = bulid_context(e.user_id, e.user_type)
        each = {}
        each['content'] = content
        each['message'] = e.message_info
        result.append(each)
        e.send_flag = True
        e.save()
    return result
