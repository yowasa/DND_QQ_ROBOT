import asyncio
import re
import time
from hoshino import priv
import nonebot
import pytz
from .battle import *

from hoshino.typing import CQEvent
from . import sv
from .ScoreCounter import ScoreCounter2
from .duelconfig import *


@sv.on_fullmatch(['战力榜', '女友战力榜', '战力排行榜', '战力排行'])
async def girl_power_rank(bot, ev: CQEvent):
    ranking_list = get_power_rank(ev.group_id)
    gid = ev.group_id
    CE = CECounter()
    msg = '本群女友战力排行榜(仅展示rank>0的)：\n'
    if len(ranking_list) > 0:
        rank = 1
        for girl in ranking_list:
            if rank <= 15:
                user_card_dict = await get_user_card_dict(bot, ev.group_id)
                rank1, power, uid, cid, hp, atk = girl
                user_card = uid2card(uid, user_card_dict)
                c = chara.fromid(cid)
                dengji = CE._get_card_level(gid, uid, cid)
                msg += f'第{rank}名: {user_card}的 {c.name}({dengji}级，rank{rank1})，hp:{hp} atk:{atk}\n'
            rank = rank + 1
    else:
        msg += '暂无女友上榜'
    await bot.send(ev, msg)
