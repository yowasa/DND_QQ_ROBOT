import argparse

from filter import msg_route
from tool.dnd_db import User,Subscribe
from handler.base_handler import ghs_handler as ghs

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
            if user.level >= 50:
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
    try:
        args = admin_parser.parse_args(msg.split())
        return args.func(args, content)
    except SystemExit:
        return '解析指令失败'


def trance_2_name(level):
    if level == 0:
        return '普通用户'
    if level == 10:
        return '管理员'
    if level == 50:
        return '超管'
    if level == 100:
        return '你在看谁？'

def add_subscribe(content,ttype,Auth_User=0):
    msg=content.get('message_type')
    if msg=='group':
        user_id=content.get('group_id')
    elif msg=='private':
        user_id=content.get('user_id')
    elif msg == 'discuss':
        user_id = content.get('discuss_id')
    else:
        return '不支持群/私聊/讨论组以外的订阅方式'

    if Auth_User !=0:
        results_users = ghs.api.user_illusts(Auth_User)
        if len(results_users.illusts)==0:
            return '此id不存在作品'
        ttype = 'user'

    old = Subscribe.get_or_none(
        (Subscribe.user_id == user_id) & (Subscribe.user_type == msg) & (Subscribe.clazz == 'pixiv') & (Subscribe.type == ttype) &(Subscribe.type_user==Auth_User))
    if not old:
        newSub = Subscribe()
        newSub.user_type = msg
        newSub.user_id = user_id
        newSub.clazz = 'pixiv'
        newSub.type = ttype
        newSub.type_user = Auth_User
        newSub.save()
        return '订阅成功'
    else:
        return '已经订阅 无需重复操作'


# 为个人或群开启自动ghs功能
@msg_route(r'(\.|。)auto', need_user=True)
def open_auto_ghs(content):
    admin = content.get('sys_user')
    if admin.level < 10:
        return '用户权限不足,仅管理可以使用'
    msg = content.get('cmd_msg').strip()
    if msg =='日榜':
        return add_subscribe(content,'day')
    elif msg=='r18日榜':
        return add_subscribe(content,'day_r18')
    elif msg=='自动订阅':
        return add_subscribe(content,'public')
    elif msg=='r18自动订阅':
        return add_subscribe(content,'private')
    else:
        return '无此指令 请输入:日榜 r18日榜 自动订阅 r18自动订阅'

@msg_route(r'(\.|。)subscribe', need_user=True)
def subscribe(content):
    admin = content.get('sys_user')
    if admin.level < 10:
        return '用户权限不足,仅管理可以使用'
    msg = content.get('cmd_msg').strip()
    return add_subscribe(content,'user',Auth_User=msg)


#.checksub  <作者id>:检查是否订阅某作者作品
@msg_route(r'(\.|。)checksub', need_user=True)
def checksub(content):
    admin = content.get('sys_user')
    if admin.level < 10:
        return '用户权限不足,仅管理可以使用'
    comm = content.get('cmd_msg').strip()
    msg = content.get('message_type')
    if msg == 'group':
        user_id = content.get('group_id')
    elif msg == 'private':
        user_id = content.get('user_id')
    elif msg == 'discuss':
        user_id = content.get('discuss_id')
    else:
        return '不支持群/私聊/讨论组以外的订阅方式'
    old = Subscribe.get_or_none(
        (Subscribe.user_id == user_id) & (Subscribe.user_type == msg) & (Subscribe.clazz == 'pixiv') & (
                    Subscribe.type == 'user') & (Subscribe.type_user == comm))
    if not old:
        return '未订阅'
    else:
        return '订阅中'

def trancetype(msg):
    if msg =='day':
        return '日榜'
    elif msg=='day_r18':
        return 'r18日榜'
    elif msg=='public':
        return '自动订阅'
    elif msg=='private':
        return 'r18自动订阅'

#.sublist:订阅列表
@msg_route(r'(\.|。)sublist', need_user=True)
def checksub(content):
    admin = content.get('sys_user')
    if admin.level < 10:
        return '用户权限不足,仅管理可以使用'
    comm = content.get('cmd_msg').strip()
    msg = content.get('message_type')
    if msg == 'group':
        user_id = content.get('group_id')
    elif msg == 'private':
        user_id = content.get('user_id')
    elif msg == 'discuss':
        user_id = content.get('discuss_id')
    else:
        return '不支持群/私聊/讨论组以外的订阅方式'
    pack_info = [trancetype(str(sub.type)) for sub in
                  Subscribe.select().where(
                      (Subscribe.user_id == user_id) & (Subscribe.user_type == msg) & (Subscribe.clazz == 'pixiv') & (
                                  Subscribe.type != 'user'))]
    user_infos = [str(sub.type_user) for sub in
             Subscribe.select().where(
        (Subscribe.user_id == user_id) & (Subscribe.user_type == msg) & (Subscribe.clazz == 'pixiv') & (Subscribe.type == 'user'))]
    return_msg=''
    if pack_info:
        return_msg+='套餐\n'+'\n'.join(pack_info)+'\n\n'

    if user_infos:
        return_msg+='画师id\n'+'\n'.join(user_infos)
    return return_msg


#.unsubscribe <作者id>:取消订阅某一作者（在库存中待发送的图片不会取消）
@msg_route(r'(\.|。)unsubscribe', need_user=True)
def unsubscribe(content):
    admin = content.get('sys_user')
    if admin.level < 10:
        return '用户权限不足,仅管理可以使用'
    comm = content.get('cmd_msg').strip()
    msg = content.get('message_type')
    if msg == 'group':
        user_id = content.get('group_id')
    elif msg == 'private':
        user_id = content.get('user_id')
    elif msg == 'discuss':
        user_id = content.get('discuss_id')
    else:
        return '不支持群/私聊/讨论组以外的订阅方式'
    old = Subscribe.get_or_none(
        (Subscribe.user_id == user_id) & (Subscribe.user_type == msg) & (Subscribe.clazz == 'pixiv') & (
                    Subscribe.type == 'user') & (Subscribe.type_user == comm))
    if not old:
        return '未订阅过该作者作品'
    else:
        old.delete_instance()
        return '取消订阅成功'