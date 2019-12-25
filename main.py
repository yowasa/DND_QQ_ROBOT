from cqhttp import CQHttp
import filter
# 读取环境变量，找不到情况下使用默认
import os
import request.invite_request as ir
import time,threading

env_dist = os.environ

api_root = env_dist.get("api_root")
if not api_root:
    api_root = "http://127.0.0.1:5700/"

bot = CQHttp(api_root=api_root,
             access_token="yowasaTest",
             secret="3909432")


@bot.on_message()
def handle_msg(context):
    content = context.copy()
    result = filter.filter(content)
    # 统一发送消息
    if result != None:
        msg =  bot.send(context, result)
        if content.get('call_back'):
            s=threading.Timer(60,call_back,(msg,))
            s.start()

def call_back(msg):
    bot.delete_msg(**msg)

@bot.on_request('group', 'friend')
def handle_request(context):
    content = context.copy()
    result = ir.handle_invite_request(content)
    return {'approve': result}

# @bot.on_notice('group_increase')
# async def handle_group_increase(context):
#     await bot.send(context, message='欢迎新人～',
#                    at_sender=True, auto_escape=True)
#
#
# @bot.on_request('group', 'friend')
# async def handle_request(context):
#     return {'approve': True}


bot.run(host='127.0.0.1', port=8080)
