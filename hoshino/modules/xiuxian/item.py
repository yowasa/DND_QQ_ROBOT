from .xiuxian_config import *


@sv.on_fullmatch(['#背包'])
async def my_item(bot, ev: CQEvent):
    counter = ItemCounter()
    gid = ev.group_id
    uid = ev.user_id
    items = counter._get_item(gid, uid)
    msg = "\n==== 道具列表 ===="
    item_li = []
    for i in items:
        ITEM_INFO[str(i[0])]['num'] = i[1]
        item_li.append(ITEM_INFO[str(i[0])])
    for i in item_li:
        msg += f"\n{i['name']} *{i['num']}"
    await bot.send(ev, msg, at_sender=True)


@sv.on_prefix(['#使用'])
async def consume_item(bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    msg = str(ev.message).strip().split()
    item_info = ITEM_NAME_MAP.get(msg[0])
    ct = XiuxianCounter()
    user = ct._get_user(gid, uid)
    if not user:
        await bot.finish(ev, "江湖上还没有过您的传说，请先注册账号")
    if not item_info:
        await bot.finish(ev, f"未找到名称为{msg[0]}的道具", at_sender=True)
    counter = ItemCounter()
    num = counter._get_item_num(gid, uid, int(item_info['id']))
    if num < 1:
        await bot.finish(ev, f"背包中道具{msg[0]}数量不足", at_sender=True)
    result = await _use_item(msg[0], msg[1:], bot, ev)
    suc_num = 0
    if result[0]:
        suc_num += 1
        counter._add_item(gid, uid, int(item_info['id']), num=-1)
    await bot.send(ev, result[1], at_sender=True)


@sv.on_prefix(['#丢弃'])
async def consume_item(bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    msg = str(ev.message).strip().split()
    item_info = ITEM_NAME_MAP.get(msg[0])
    ct = XiuxianCounter()
    user = ct._get_user(gid, uid)
    if not user:
        await bot.finish(ev, "江湖上还没有过您的传说，请先注册账号")
    if not item_info:
        await bot.finish(ev, f"未找到名称为{msg[0]}的道具", at_sender=True)
    counter = ItemCounter()
    num = counter._get_item_num(gid, uid, int(item_info['id']))
    if num < 1:
        await bot.finish(ev, f"背包中道具{msg[0]}数量不足", at_sender=True)
    counter._add_item(gid, uid, int(item_info['id']), num=-1)
    await bot.send(ev, f"你丢弃掉了一个「{msg[0]}」", at_sender=True)


register = dict()


async def _use_item(name, msg, bot, ev):
    func = register.get(name)
    if func:
        return await func(msg, bot, ev)
    return (False, "道具未实装")


# 注解msg 传入正则表达式进行匹配
def msg_route(item_name):
    def show(func):
        async def warpper(msg, bot, ev: CQEvent):
            return await func(msg, bot, ev)

        register[item_name] = warpper
        return warpper

    return show


@msg_route("造化丸")
async def choose_girl(msg, bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    ct = XiuxianCounter()
    user = ct._get_user(gid, uid)
    if not user:
        await bot.finish(ev, "江湖上还没有过您的传说，请先注册账号")
    user.exp += 50
    ct._save_user_info(user)
    return (True, f"你服用了造化丸，感觉到灵力喷涌而出，获得了50点EXP")


@msg_route("瞬息万里符")
async def change_weather(msg, bot, ev: CQEvent):
    return (False, f"符咒带在身上就能发挥效果")
