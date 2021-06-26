# 用户行为处理器
from filter import msg_route
from tool.rich_man_db import *


# 群开启游戏
@msg_route(r'\s*\.gamestart', need_user=True)
def richman_start(content):
    msg = content.get('message_type')
    if msg != 'group':
        return "仅在群组中可以开启游戏"
    group_id = content.get('group_id')
    user = content.get('sys_user')
    # 校验权限
    if user.level < 10:
        return "仅管理可以开始游戏"
    # 检查游戏是否已经存在

    # 初始化地图

    return "开启游戏成功"


# 加入游戏
@msg_route(r'\s*\.join', need_user=True)
def richman_join(content):
    user = content.get('sys_user')
    # 游戏是否存在
    msg = content.get('message_type')
    if msg != 'group':
        return "仅在群组中可以开启游戏"

    # 初始化人物信息
    user_name = content.get('cmd_msg').strip()
    #

    return f"初始化完成 \n初始金钱：\n初始位置:\n"


