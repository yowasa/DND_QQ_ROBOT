import argparse

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


def add(args, content):
    admin = content.get('sys_user')
    if args.super:
        if admin.level < 100:
            return '你在想peach'
        user = User.get_or_none(User.qq_number == args.user)
        if not user:
            return f'未查询到用户{args.user},请让你其少使用过一次.jrrp功能'
        if user.level >= admin.level:
            return '无法对权限高于或等于你的角色使用权限命令'
        if not args.force:
            user.level >= 50
            return f'用户已经是超管,无需再次添加'
        user.level = 50
        user.save()
        return '增加超管成功'
    else:
        if admin.level < 50:
            return '用户权限不足,仅超管可以使用'
        user = User.get_or_none(User.qq_number == args.user)
        if not user:
            return f'未查询到用户{args.user},请让其至少使用过一次.jrrp功能'
        if not args.force:
            if user.level >= 10:
                return f'用户已经是管理,无需再次添加'
        user.level = 10
        user.save()
        return '增加管理成功'


def delete(args, content):
    admin = content.get('sys_user')
    if admin.level < 50:
        return '用户权限不足,仅超管可以使用'
    user = User.get_or_none(User.qq_number == args.user)
    if not user:
        return f'未查询到用户{args.user},请让其至少使用过一次.jrrp功能'
    if user.level >= admin.level:
        return '无法对权限高于或等于你的角色使用命令'
    if not args.force:
        if user.level >= 50:
            return "超管无法被删除"

    if args.account:
        user.delete()
        return '删除用户数据成功'
    else:
        user.level = 0
        user.save()
        return '删除管理成功'


def ls(args, content):
    admin = content.get('sys_user')
    if admin.level < 10:
        return '用户权限不足,仅管理可以使用'
    limit = 10
    if args.all:
        limit = 0
    admin = content.get('sys_user')
    users = [str(user.qq_number) + ':' + trance_2_name(user.level) for user in
             User.select().where((User.level <= admin.level) & (User.level < 100) & (User.level >= limit))]

    return '\n'.join(users)


def check(args, content):
    admin = content.get('sys_user')
    if admin.level < 10:
        return '用户权限不足,仅管理可以使用'
    user = User.get_or_none(User.qq_number == args.user)
    if not user:
        return f'未查询到用户{args.user},请让其至少使用过一次.jrrp功能'
    return trance_2_name(user.level)

def common(args,content):
    admin = content.get('sys_user')
    if admin.level < 10:
        return '用户权限不足,仅管理可以使用'
    if args.help:
        return admin_parser.format_help()
    elif args.version:
        return '你TM是程序员吧，看这种东西'

# admin指令解析器
admin_parser = argparse.ArgumentParser(
    prog='admin',  # 解析的是哪个指令
    usage='%(prog)s [options]',  # 用法说明 会显示在help里
    description='管理员指令',  # 指令描述 会显示在help里
    epilog="用这些指令管理成员的权限",  # help显示完，最后的文案
    add_help=False,  # 是否添加默认的-h 和--help指令显示内容
)
admin_parser.add_argument('--version', '-v', nargs='?', default=False, const=True, help='版本号')
admin_parser.add_argument('--help', '-h', nargs='?', default=False, const=True, help='帮助')
admin_parser.set_defaults(func=common)

subparsers = admin_parser.add_subparsers(help='指令列表')

admin_add = subparsers.add_parser('add', help='增加管理员')
admin_add.add_argument('-f', '--force', nargs='?', default=False, const=True, help='强制增加，可能导致人员权限降级')
admin_add.add_argument('-s', '--super', nargs='?', default=False, const=True, help="增加超管")
admin_add.add_argument('user', nargs=1, type=int, help="设置为管理的用户qq号", metavar="qq号")
admin_add.set_defaults(func=add)

admin_del = subparsers.add_parser('del', help='删除管理员')
admin_del.add_argument('-f', '--force', nargs='?', default=False, const=True, help='强制删除，可以删除超管，非管理员也不会报错')
admin_del.add_argument('-a', '--account', nargs='?', default=False, const=True, help='删除用户所信息')
admin_del.add_argument('user', nargs=1, type=int, help="删除管理的用户qq号", metavar="qq号")
admin_del.set_defaults(func=delete)

admin_ls = subparsers.add_parser('ls', help='查看管理员列表')
admin_ls.add_argument('-a', '--all', nargs='?', default=False, const=True, help='查看所有可查询人员信息（包含普通用户）')
admin_ls.set_defaults(func=ls)

admin_check = subparsers.add_parser('check', help='检查人员级别')
admin_check.add_argument('user', nargs=1, type=int, help="要检查的用户qq号", metavar="qq号")
admin_check.set_defaults(func=check)


# 增加管理功能
@msg_route(r'(\.|。)admin', need_user=True)
def admin_exec(content):
    msg = content.get('cmd_msg')
    args = admin_parser.parse_args(msg.split())
    return args.func(args, content)


def trance_2_name(level):
    if level == 0:
        return '普通用户'
    if level == 10:
        return '管理员'
    if level == 50:
        return '超管'
    if level == 100:
        return '你在看谁？'
