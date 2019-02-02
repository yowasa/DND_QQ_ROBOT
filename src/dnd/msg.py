import re
import user_controller
import character_controller


# 注解msg 传入正则表达式进行匹配
def filter(re_msg, need_user=False, need_character=False):
    def show(func):

        def warpper(content):
            # 原始入参打印
            print(content)
            # 获得命令参数
            cmd_msg = content['message']
            # 替换掉指令部分
            sub_msg = re.sub(re_msg, lambda m: '', cmd_msg)
            # 新增命令属性
            content['cmd_msg'] = sub_msg
            sender = content['sender']
            user_id = sender['user_id']
            # 获得用户
            if need_user:
                user = user_controller.get_user(user_id)
                content['sys_user'] = user
            if need_character:
                user = user_controller.get_user(user_id)
                content['sys_user'] = user
                character_name = user.current_character
                character = character_controller.get_charater(user_id, character_name)
                content['sys_character'] = character
            result = func(content)
            # 打印输出结果
            print(result)
            return result

        warpper.re_msg = re_msg
        return warpper

    return show

# for name in filter.__dir__():
#     print(name,str(getattr(filter,name,None)))
