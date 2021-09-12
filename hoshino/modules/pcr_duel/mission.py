from hoshino.typing import CQEvent
from . import sv
from .duelconfig import *


@sv.on_fullmatch(['任务帮助'])
async def manor_help(bot, ev: CQEvent):
    msg = '''
╔                                        ╗  
             任务帮助
[领取任务] [完成任务]
[当前任务]
╚                                        ╝
 '''
    await bot.send(ev, msg)

# 领取任务

# 完成任务
