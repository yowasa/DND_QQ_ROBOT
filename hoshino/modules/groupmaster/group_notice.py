import hoshino
from hoshino import Service, util
from hoshino.typing import NoticeSession, CQHttpError

sv1 = Service('退群通知', help_='退群通知群友\n')


@sv1.on_notice('group_decrease.leave')
async def leave_notice(session: NoticeSession):
    ev = session.event
    name = ev.user_id
    if ev.user_id == ev.self_id:
        return
    try:
        info = await session.bot.get_stranger_info(self_id=ev.self_id, user_id=ev.user_id)
        name = info['nickname'] or name
        name = util.filt_message(name)
    except CQHttpError as e:
        sv1.logger.exception(e)
    await session.send(f"{name}({ev.user_id})退群了。")


sv2 = Service('入群欢迎', help_='欢迎新入群的群友\n')


@sv2.on_notice('group_increase')
async def increace_welcome(session: NoticeSession):
    if session.event.user_id == session.event.self_id:
        return

    welcomes = hoshino.config.groupmaster.increase_welcome
    gid = session.event.group_id
    if gid in welcomes:
        await session.send(welcomes[gid], at_sender=True)
    else:
        await session.send(welcomes["default"], at_sender=True)
