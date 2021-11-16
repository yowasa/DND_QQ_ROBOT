from hoshino import Service
from hoshino.typing import CQEvent
from .data_source import get_bt_info
from hoshino.util.utils import get_message_text

sv = Service('bt搜索', bundle="bt搜索", help_=
'''[bt搜索] 关键词''')


@sv.on_prefix(['bt搜索'])
async def bt_search(bot, ev: CQEvent):
    msg = get_message_text(ev)
    async for title, itype, create_time, file_size, link in get_bt_info(
            msg, 1
    ):
        msg = f"标题：{title}\n类型：{itype}\n创建时间：{create_time}\n文件大小：{file_size}\n种子：{link}"
        await bot.send(ev, msg)
