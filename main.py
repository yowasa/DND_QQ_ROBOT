from cqhttp import CQHttp
import filter
# 读取环境变量，找不到情况下使用默认
import os
import request.invite_request as ir
import threading
from flask_apscheduler import APScheduler
import time

env_dist = os.environ

api_root = env_dist.get("api_root")
if not api_root:
    api_root = "http://127.0.0.1:5700/"

bot = CQHttp(api_root=api_root)


@bot.on_message()
def handle_msg(context):
    content = context.copy()
    result = filter.filter(content)
    # 统一发送消息
    if result != None:
        msg = bot.send(context, result)
        if content.get('call_back') and context.get('group_id') not in [324760552, 1078759936]:
            global timer
            timer = threading.Timer(60, call_back, (msg,))
            timer.start()


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

import handler.job.auto_ghs_job as job


def scan_job():
    try:
        job.scan_list()
    except:
        pass


def send_job():
    try:
        need_send_list = job.send_list()
        for each in need_send_list:
            context = each.get('content')
            if not context:
                continue
            message = each.get('message')
            bot.send(context, message)
    except:
        pass


# 任务配置类
class Config(object):
    # 配置执行job
    JOBS = [
        {
            'id': 'scan_job',
            'func': scan_job,
            'args': None,
            'trigger': 'interval',
            'seconds': 60 * 60
        }, {
            'id': 'send_job',
            'func': send_job,
            'args': None,
            'trigger': 'interval',
            'seconds': 60 * 30
        }
    ]

while True:
    try:
        bot.server_app.config.from_object(Config())
        scheduler = APScheduler()
        scheduler.init_app(bot.server_app)
        scheduler.start()
        bot.run(host='127.0.0.1', port=8080)
    except SystemExit:
        continue


