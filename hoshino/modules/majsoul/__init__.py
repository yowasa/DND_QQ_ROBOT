# coding=utf-8
from hoshino import Service

sv = Service("雀魂帮助", enable_on_default=True, bundle='麻将功能', help_="""
[雀魂帮助] 查询详细指令
""".strip())

help_txt = '''
==== 雀魂查询 ====
查询指令：
雀魂信息/雀魂查询 昵称：查询该ID的雀魂基本对局数据(包含金场以上所有)
三麻信息/三麻查询 昵称：查询该ID雀魂三麻的基本对局数据(包含金场以上所有)
雀魂信息/雀魂查询 (金/金之间/金场/玉/王座) 昵称：查询该ID在金/玉/王座之间的详细数据
三麻信息/三麻查询 (金/金之间/金场/玉/王座) 昵称：查询该ID在三麻金/玉/王座之间的详细数据
雀魂牌谱 昵称：查询该ID下最近五场的对局信息
三麻牌谱 昵称：查询该ID下最近五场的三麻对局信息

对局订阅指令：
雀魂订阅 昵称：订阅该昵称在金之间以上的四麻对局信息 
三麻订阅 昵称：订阅该昵称在金之间以上的三麻对局信息 
(取消/关闭)雀魂订阅 昵称：将该昵称在本群的订阅暂时关闭 
(取消/关闭)三麻订阅 昵称：将该昵称在本群的三麻订阅暂时关闭 
开启雀魂订阅 昵称：将该昵称在本群的订阅开启 
开启三麻订阅 昵称：将该昵称在本群的三麻订阅开启 
删除雀魂订阅 昵称：将该昵称在本群的订阅删除
删除三麻订阅 昵称：将该昵称在本群的三麻订阅删除
雀魂订阅状态：查询本群的雀魂订阅信息的开启状态 
三麻订阅状态：查询本群的雀魂订阅信息的开启状态 
'''.strip()


@sv.on_fullmatch("雀魂帮助")
async def help(bot, ev):
    await bot.send(ev, help_txt)