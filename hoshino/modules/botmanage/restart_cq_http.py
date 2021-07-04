import asyncio

from hoshino.service import sucmd
from hoshino.typing import CommandSession, CQHttpError
import os
import threading
import time

# 重启bot 暂不支持 自写仅限自用的接口
@sucmd('cq重启', aliases=('朝日重启'), force_private=False)
async def cq_restart(session: CommandSession):
    # ev = session.event
    # su = session.event.user_id
    # bot = session.bot
    kill_exe("go-cqhttp.exe")
    main = 'start cmd /k "cd /d d:/workspace/bot/go-cqhttp_windows_amd64&&go-cqhttp.exe"'
    r_v = os.system(main)
    print(r_v)
    # ev = session.event
    # su = session.event.user_id
    # bot = session.bot
    # await bot.set_restart()
    # await bot.send_private_msg(self_id=ev.self_id, user_id=su, message='重启成功！')


def kill_exe(exe_name):
    os.system('taskkill /f /t /im '+exe_name)#MESMTPC.exe程序名字
    print("杀死进程{}".format(exe_name))
