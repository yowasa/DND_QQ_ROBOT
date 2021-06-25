import nonebot
from nonebot import RequestSession, on_request
from hoshino import util


# 邀请信息处理 仅超管可以邀请入群
@on_request('group.invite')
async def handle_group_invite(session: RequestSession):
    if session.ctx['user_id'] in nonebot.get_bot().config.SUPERUSERS:
        await session.approve()
    else:
        await session.reject(reason='邀请入群请联系维护组')
