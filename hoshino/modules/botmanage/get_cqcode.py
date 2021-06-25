from hoshino import sucmd
from hoshino.typing import CommandSession
from hoshino.util import escape

# 图片获取cq码
@sucmd('取码')
async def get_cqcode(session: CommandSession):
    await session.send(escape(str(session.current_arg)))
