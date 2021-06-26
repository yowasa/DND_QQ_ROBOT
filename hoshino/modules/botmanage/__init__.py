# do nothing
import hoshino
from hoshino.typing import CommandSession

TOP_MANUAL = '''
=====================
- 管理帮助说明 -
=====================
发送方括号[]内的关键词即可触发，{}内是要传入的自定义信息

[bc] {内容} 机器人广播，将内容广播到所有群
[清理数据] 清理机器人图片缓存
[取码] {非文本内容} 获取cq码
[退群] {群号} 退群
[ls] {-g查询群, -f查询好友, -b查询骰娘自己, -s {服务名} 查询服务开启情况}

========
'''.strip()


# 管理员帮助信息
@hoshino.sucmd('帮助管理')
async def send_help(session: CommandSession):
    await session.send(TOP_MANUAL)
