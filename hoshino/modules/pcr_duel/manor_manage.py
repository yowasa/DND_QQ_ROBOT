import asyncio
from hoshino import Service
from hoshino import priv
from hoshino.typing import CQEvent
from hoshino.typing import CommandSession
from . import duel_chara
from . import sv
from .ScoreCounter import ScoreCounter2
from .duelconfig import *

sv_manor = Service('领地管理', enable_on_default=False, manage_priv=priv.SUPERUSER, bundle='领地管理', help_=
"""[领地帮助]查看相关帮助
""")


@sv_manor.on_fullmatch(['领地帮助'])
async def manor_help(bot, ev: CQEvent):
    msg = '''
╔                                        ╗  
             领地系统帮助
[接受封地] 准男爵以上可以接受封地，开始管理自己的领地
[领地查询] 查询领地状态
[建筑列表] 查看城市可建设建筑列表
[建造建筑] 建造建筑
[领地结算] 领地指令结算，一天只能执行一次
[政策选择]:可选项：开垦林地，退耕还林，保持原样 结算时5%比例进行移动
[税率调整]:设置领地征税比例 默认10%
==建筑指令==
[购买道具] 商店指令，花费1w金币随机买一个道具

注：税收与耕地面积有关，声望与林地面积有关
领地面积为100*爵位
城市面积为领地的1/10
接受封地的第一天只能建造市政中心
初始耕地面积为10%林地为90%

╚                                        ╝
 '''
    await bot.send(ev, msg)


@sv_manor.on_fullmatch("接受封地")
async def manor_begin(bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    # 检查是否已经开启
    if get_user_counter(gid, uid, UserModel.MANOR_BEGIN):
        bot.finsh("你已经接受了封地，无需再次领封")
    # 判断是否是准男爵以上
    duel = DuelCounter()
    level = duel._get_level(gid, uid)
    if level == 0:
        msg = '您还未在本群创建过贵族，请发送 创建贵族 开始您的贵族之旅。'
        await bot.send(ev, msg, at_sender=True)
        return
    elif level < 3:
        msg = '必须达到准男爵以上才能接受封地'
        await bot.finsh(ev, msg, at_sender=True)

    # 初始化耕地比例
    geng = 10
    save_user_counter(gid, uid, UserModel.GENGDI, geng)
    # 初始化治安
    zhian = 80
    save_user_counter(gid, uid, UserModel.ZHI_AN, zhian)
    # 发送信息
    noblename = get_noblename(level)
    msg = f'''尊敬的{noblename}您好，您成功接受了册封，获得了封地
    城市面积xx
    领地面积xx
    拥有xx耕地
    当然治安状况xx
    请认真维护好自己的领地
    '''
    await bot.finsh(ev, msg, at_sender=True)


@sv_manor.on_fullmatch("领地查询")
async def manor_view(bot, ev: CQEvent):
    # 检查是否已经开启
    # 获取爵位and状态计算
    msg = f'''尊敬的xx您好，您的领地状态如下:
        城市面积xx
        领地面积xx
        拥有xx耕地
        当然治安状况xx
        '''
    pass


@sv_manor.on_fullmatch("建筑列表")
async def build_view(bot, ev: CQEvent):
    msg = f'''尊敬的xx您好，您的领地状态如下:
            城市面积xx
            领地面积xx
            拥有xx耕地
            当然治安状况xx
            '''
    pass


@sv_manor.on_prefix("建造建筑")
async def _build(bot, ev: CQEvent):
    # 检查是否已经开启
    # 检查土地大小是否够用
    # 检查建筑限制
    # 增加建筑状态
    msg = '''你大兴土木建造了xxx
    '''
    pass


@sv_manor.on_fullmatch("领地结算")
async def manor_sign(bot, ev: CQEvent):
    # 检查是否已经开启
    # 每日结算次数限制（是否已经结算）
    # 计算城市拥堵程度造成的治安损失
    # 计算税收状况造成的治安损失
    # 检查是否暴动
    # 检查治安状况造成的损失
    # 由于政策造成的耕地占比变化
    # 获取耕地面积计算税收
    # 获取林地面积计算声望
    # 计算建筑带来的收益
    # 建筑倒计时
    # 检查爵位所需上供
    msg = '''=== 领地结算 ===
    '''

    pass


@sv_manor.on_prefix("政策选择")
async def manor_policy(bot, ev: CQEvent):
    pass


@sv_manor.on_prefix("税率调整")
async def manor_policy(bot, ev: CQEvent):
    pass


@sv_manor.on_prefix("购买道具")
async def manor_policy(bot, ev: CQEvent):
    pass
