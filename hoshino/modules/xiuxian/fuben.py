from .xiuxian_config import *
from hoshino import util
import random
from .xiuxian_base import *
from .youli import _youli


@sv.on_prefix(["#探索秘境"])
async def start(bot, ev: CQEvent):
    name = str(ev.message).strip()
    if not name:
        await bot.finish(ev, "请选择要探索的秘境")
    mi_jing = FU_BEN[name]
    if not mi_jing:
        await bot.finish(ev, "该秘境不存在,请确认要探索的秘境", at_sender=True)
    gid = ev.group_id
    uid = ev.user_id
    in_fuben = get_user_counter(gid, uid, UserModel.FU_BEN)
    if in_fuben:
        await bot.finish(ev, f"你已在秘境之中", at_sender=True)
    user = await get_ev_user(bot, ev)
    mijing_map = mi_jing['name']
    user_adress = MAP.get(user.map)
    if mijing_map not in user_adress['able']:
        await bot.finish(ev, f"你当前所在的[{user.map}]只能前往 {'｜'.join(user_adress['able'])}")

    ## 检查是否有进入凭证
    access = mi_jing['access']
    item_info = ITEM_NAME_MAP.get(access)
    counter = ItemCounter()
    num = counter._get_item_num(gid, uid, int(item_info['id']))
    if num < 1:
        await bot.finish(ev, f"背包中没有道具{access}，无法探索秘境", at_sender=True)
    ## 消耗凭证 记录状态
    counter._add_item(gid, uid, int(item_info['id']), num=-1)
    save_user_counter(gid, uid, UserModel.FU_BEN, 1)
    save_user_counter(gid, uid, UserModel.FU_BEN_EVENT_TIME, 0)

    ct = XiuxianCounter()
    user.map = mijing_map
    ct._save_user_info(user)
    await bot.finish(ev, f"你已经进入{name}，可以开始你的探索之旅了", at_sender=True)


@sv.on_prefix(["#离开秘境"])
async def start(bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    in_fuben = get_user_counter(gid, uid, UserModel.FU_BEN)
    if not in_fuben:
        await bot.finish(ev, f"你并不在秘境之中", at_sender=True)
    save_user_counter(gid, uid, UserModel.FU_BEN, 0)
    user = await get_ev_user(bot, ev)
    user.map = FU_BEN[user.map]['map']
    ct = XiuxianCounter()
    ct._save_user_info(user)
    await bot.finish(ev, f"你已离开秘境", at_sender=True)

@sv.on_fullmatch(["#探索"])
async def start(bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    in_fuben = get_user_counter(gid, uid, UserModel.FU_BEN)
    if not in_fuben:
        await bot.finish(ev, f"你并不在秘境之中", at_sender=True)

    # todo
    user = await get_ev_user(bot, ev)
    mi_jing = FU_BEN[user.map]
    all_li = mi_jing['event']
    rn = random.randint(1, 100)
    total = 0
    msg = ""
    for i in all_li.keys():
        total += all_li[i]
        if rn <= total:
            msg = i
            break
    result = await _youli(msg, user, bot, ev)
    add_user_counter(gid, uid, UserModel.FU_BEN_EVENT_TIME, 1)
    await bot.send(ev, result, at_sender=True)
