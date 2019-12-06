from filter import msg_route
from tool.dnd_db import User

'''
管理类
人员分为master,超管,管理
master写死 value=100
超管可以增加管理员value=50
管理员可以加骰子好友，拉骰子进群 value=10
普通人员 value=0
'''

#增加管理功能
@msg_route(r'\.admin',need_user=True)
def admin(content):
    admin = content.get('sys_user')
    msg = content.get('cmd_msg')
    if "addsuper" in msg:
        if admin.level < 100:
            return '用户权限不足'
        msg = msg.replace("addsuper","")
        msg=msg.strip()
        user_id = msg
        user = User.get_or_none(User.qq_number == int(user_id))
        if not user:
            return f'未查询到用户{msg},请让你至少使用过一次.jrrp功能'
        user.level = 50
        user.save()
        return '增加超管成功'
    if "add" in msg:
        if admin.level < 50:
            return '用户权限不足'
        msg=msg.replace("add","")
        msg=msg.strip()
        user_id = msg
        user = User.get_or_none(User.qq_number == int(user_id))
        if not user:
            return f'未查询到用户{msg},请让你至少使用过一次.jrrp功能'
        user.level = 10
        user.save()
        return '增加管理成功'
    if "del" in msg:
        msg=msg.replace("del","")
        msg=msg.strip()
        user_id = msg
        user = User.get_or_none(User.qq_number == int(user_id))
        if not user:
            return f'未查询到用户{msg},请让你至少使用过一次.jrrp功能'
        if user.level==0:
            return '对方不是管理员，无需删除'
        if user.level>=admin.level:
            return '对方权限比你大，无法删除'
        user.level = 0
        user.save()
        return '删除管理成功'
    return f'查无此命令{msg}'
