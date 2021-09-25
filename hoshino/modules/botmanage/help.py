from hoshino import Service, priv
from hoshino.typing import CQEvent

sv = Service('_help_', manage_priv=priv.SUPERUSER, visible=False)

TOP_MANUAL = '''
=====================
- Bot使用说明 -
=====================
发送方括号[]内的关键词即可触发，{}内是要传入的自定义信息
※功能采取模块化管理，群管理可控制开关
- 管理指令 -
[功能列表] 查询功能列表
[启用] {功能名} 
[禁用] {功能名}
[订阅] {画师id} 订阅画师

- 用户常用 -
[今日人品]查看当天的人品
[抽签]pcr&原神抽签
[img]获取p站图片
[搜图]搜索图片

- 发送以下关键词查看更多 -
[帮助通用]
[帮助图片功能]
[帮助pcr订阅]
[帮助pcr娱乐]
[帮助贵族游戏]
[帮助跑团]
[帮助推特]

========
※本bot开源，可自行搭建
'''.strip()


def gen_bundle_manual(bundle_name, service_list, gid):
    manual = [bundle_name]
    service_list = sorted(service_list, key=lambda s: s.name)
    for sv in service_list:
        if sv.visible:
            spit_line = '=' * max(0, 18 - len(sv.name))
            manual.append(f"|{'○' if sv.check_enabled(gid) else '×'}| {sv.name} {spit_line}")
            if sv.help:
                manual.append(sv.help)
    return '\n'.join(manual)


@sv.on_prefix('help', '帮助')
async def send_help(bot, ev: CQEvent):
    bundle_name = ev.message.extract_plain_text().strip()
    bundles = Service.get_bundles()
    if not bundle_name:
        await bot.send(ev, TOP_MANUAL)
    elif bundle_name in bundles:
        msg = gen_bundle_manual(bundle_name, bundles[bundle_name], ev.group_id)
        await bot.send(ev, msg)
    # else: ignore
