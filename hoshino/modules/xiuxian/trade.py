from .xiuxian_config import *
from hoshino.util.utils import get_message_text


@sv.on_prefix(["#上架"])
async def shangjia(bot, ev: CQEvent):
    user = await get_ev_user(bot, ev)
    msg = get_message_text(ev)
    cmd_msg = msg.split()
    if len(cmd_msg) != 2:
        await bot.finish(ev, f"指令解析错误 请使用 #上架[物品名] [价格] 中间用空格隔开")
    item_name = cmd_msg[0]
    price = cmd_msg[1]
    item = get_item_by_name(item_name)
    if not item:
        await bot.finish(ev, f'未找到名为[{item_name}]的物品', at_sender=True)
    if not price.isdecimal():
        await bot.finish(ev, '请输入数字价格', at_sender=True)
    price = int(price)
    if price < 50:
        await bot.finish(ev, '交易行要求最低价格不能低于50灵石', at_sender=True)
    it = ItemCounter()
    exist = it._get_trade_item(user.gid, user.uid)
    if exist:
        item_shangjia = ITEM_INFO[str(exist[2])]
        await bot.finish(ev, f"你已经上架了物品[{item_shangjia['name']}]，不可上架多个物品")
    if not check_have_item(user.gid, user.uid, item):
        await bot.finish(ev, f'你背包中没有「{item_name}」', at_sender=True)
    # 检查灵石
    shui = int(0.1 * price)
    if user.lingshi < shui:
        await bot.finish(ev, f'上架「{item_name}」需要预先缴纳10%售价的税款，你的灵石不足。', at_sender=True)
    # 扣减灵石
    add_user_counter(user.gid, user.uid, UserModel.LINGSHI, num=-shui)
    # 上架物品
    it._save_trade_item(user.gid, user.uid, int(item['id']), price)
    # 损耗物品
    use_item(user.gid, user.uid, item)
    await bot.finish(ev, f'你支付了{shui}灵石的税款，以{price}灵石的价格成功上架物品「{item_name}」', at_sender=True)


@sv.on_fullmatch(["#下架"])
async def shangjia(bot, ev: CQEvent):
    user = await get_ev_user(bot, ev)
    it = ItemCounter()
    exist = it._get_trade_item(user.gid, user.uid)
    if not exist:
        await bot.finish(ev, f"你没有上架任何物品")
    item_shangjia = ITEM_INFO[str(exist[2])]
    if not add_item(user.gid, user.uid, item_shangjia):
        await bot.finish(ev, f"你的背包已满，无法下架物品")
    it._del_trade_info(user.gid, user.uid)
    await bot.finish(ev, f"你成功下架了[{item_shangjia['name']}]")


@sv.on_prefix(["#查价"])
async def shangjia(bot, ev: CQEvent):
    user = await get_ev_user(bot, ev)
    item_name = get_message_text(ev)
    item = get_item_by_name(item_name)
    if not item:
        await bot.finish(ev, f'未找到名为[{item_name}]的物品', at_sender=True)
    it = ItemCounter()
    rsp = it._get_low_3_trade_item(user.gid, int(item['id']))
    if not rsp:
        await bot.finish(ev, f'当前没有人上架过[{item_name}]', at_sender=True)
    msg_li = []
    ct = XiuxianCounter()
    for i in rsp:
        sale_user = ct._get_user(user.gid, i[1])
        if sale_user:
            un = sale_user.name
        else:
            un = "未知"
        msg_li.append(f"{un}上架的[{item_name}]售价{i[3]}")
    await bot.finish(ev, '\n'.join(msg_li))


@sv.on_prefix(["#购买"])
async def shangjia(bot, ev: CQEvent):
    user = await get_ev_user(bot, ev)
    item_name = get_message_text(ev)
    item = get_item_by_name(item_name)
    if not item:
        await bot.finish(ev, f'未找到名为[{item_name}]的物品', at_sender=True)
    it = ItemCounter()
    rsp = it._get_low_3_trade_item(user.gid, int(item['id']))
    if not rsp:
        await bot.finish(ev, f'当前没有人上架过[{item_name}]', at_sender=True)
    sale_user = rsp[0][1]
    sale_price = rsp[0][3]
    if user.lingshi < sale_price:
        await bot.finish(ev, f'购买[{item_name}]需要{sale_price}灵石，你的灵石不足', at_sender=True)
    if not add_item(user.gid, user.uid, item):
        await bot.finish(ev, f'你没有足够的背包空间', at_sender=True)
    # 删除上架物品
    it._del_trade_info(user.gid, sale_user)
    # 扣减灵石
    add_user_counter(user.gid, user.uid, UserModel.LINGSHI, num=-sale_price)
    # 增加灵石
    add_user_counter(user.gid, sale_user, UserModel.LINGSHI, num=sale_price)
    await bot.finish(ev,
                     f'你花费了{sale_price}灵石购买了{item_name}\n[CQ:at,qq={sale_user}]你上架的{item_name}成功卖出,获得了{sale_price}灵石',
                     at_sender=True)
