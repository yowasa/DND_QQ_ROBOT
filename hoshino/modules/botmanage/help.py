from hoshino import Service, priv
from hoshino.typing import CQEvent

sv = Service('_help_', manage_priv=priv.SUPERUSER, visible=False)

'''
[!帮助] 会战管理v2
[怎么拆日和] 竞技场查询
[星乃来发十连] 转蛋模拟
[pcr速查] 常用网址
[官漫132] 四格漫画（日）
[切噜一下] 切噜语转换
[lssv] 查看功能模块的开关状态（群管理限定）
[来杯咖啡] 联系维护组

发送以下关键词查看更多：
[帮助pcr会战]
[帮助pcr查询]
[帮助pcr娱乐]
[帮助pcr订阅]
[帮助kancolle]
[帮助通用]
'''

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

- 用户常用 -

- 发送以下关键词查看更多 -
[帮助通用]
[帮助pcr订阅]
[帮助pcr娱乐]
[帮助贵族决斗]

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
