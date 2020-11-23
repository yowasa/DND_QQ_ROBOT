import re
from werkzeug.utils import cached_property
from tool.dnd_db import User, Character

register = dict()


def filter(content):
    cmd_msg = content['message']
    for key in dict(register).keys():
        if re.match(key, cmd_msg,flags=re.IGNORECASE):
            func = register.get(key)
            return func(content)


# 注解msg 传入正则表达式进行匹配
def msg_route(re_msg, need_user=False, need_character=False):
    def show(func):
        def warpper(content):
            # 原始入参打印
            print(content)
            # 获得命令参数
            cmd_msg = content['message']
            # 替换掉指令部分
            sub_msg = re.sub(re_msg, lambda m: '', cmd_msg,flags=re.IGNORECASE)
            # 新增命令属性
            content['cmd_msg'] = sub_msg
            sender = content['sender']
            user_id = sender['user_id']
            # 获得用户
            if need_user:
                user = get_user(user_id)
                content['sys_user'] = user
            if need_character:
                if not need_user:
                    user = get_user(user_id)
                    content['sys_user'] = user
                character_id = user.cur_character_id
                character = Character.get_or_none(Character.id == character_id)
                if character:
                    content['sys_character'] = character
            result = func(content)
            # 打印输出结果
            print(result)
            return result

        register[re_msg] = warpper
        return warpper

    return show


def get_user(user_id):
    user_id = int(user_id)
    user = User.get_or_none(User.qq_number == int(user_id))
    if not user:
        user = User(qq_number=user_id)
        user.save()
    return user

#识别加载装饰器 勿删
from handler import *
from handler.dnd_handler import *
from handler.touhou_handler import *
from handler.base_handler import *