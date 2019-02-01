from aiocqhttp import CQHttp
import dice
import attribute_controller
import user_gen
import helper
import base_filter

bot = CQHttp(access_token='yowasaTest',
             enable_http_post=False)

def msg(func):
    def warpper(context):
        print(context)
        result=func(context)
        print(result)

@bot.on_message()
@msg()
async def handle_msg(context):
    print(context)
    base_filter.filter(context)
    commond = context['message']
    result = None
    # 骰点
    if commond.startswith('.r') and not commond.startswith('.race') and not commond.startswith('.reroll'):
        result = dice.dice_ex(context)
    # 属性鉴定
    if commond.startswith('.check'):
        result = dice.check(context)

    # 今日人品
    if commond.startswith('.jrrp'):
        result = dice.jrrp(context)
    # 指令说明
    if commond.startswith('.comm'):
        result = helper.comm_helper()
    # 帮助文档
    if commond.startswith('.help '):
        result = helper.helper(context)
    # 随机dnd属性
    if commond.startswith('!dnd'):
        result = dice.random_attribute()
    # 查看属性
    if commond == '.attr':
        result = attribute_controller.watch_attribute(context)
    # 生成角色
    if commond.startswith('.gen '):
        result = user_gen.gen(context)
    # 删除角色
    if commond.startswith('.drop '):
        result = user_gen.drop(context)
    # 重新骰点
    if commond == '.reroll':
        result = user_gen.reroll(context)
    # 自选属性
    if commond.startswith('.attrup '):
        result = attribute_controller.attr_up(context)
    # 自选语言
    if commond.startswith('.language '):
        result = attribute_controller.select_language(context)
    # 初始装备
    if commond.startswith('.init_equip '):
        result = attribute_controller.init_equip(context)
    # 熟练项选择
    if commond.startswith('.skilled_item '):
        result = attribute_controller.skilled_item(context)
    # 范型选择
    if commond.startswith('.style '):
        result = attribute_controller.select_style(context)
    # 查看角色列表
    if commond == '.ul':
        result = attribute_controller.get_user_list(context)
    # 选择使用哪一个人物
    if commond.startswith('.switch '):
        result = attribute_controller.switch_user(context)
    # 交换属性
    if commond.startswith('.swap'):
        result = user_gen.swap(context)
    # 选择种族
    if commond.startswith('.race '):
        result = user_gen.switch_race(context)
    # 选择亚种
    if commond.startswith('.subrace '):
        result = user_gen.switch_sub_race(context)
    # 选择职业
    if commond.startswith('.job '):
        result = user_gen.switch_job(context)
    # 统一发送消息
    if result != None:
        await bot.send(context, result)



# @bot.on_notice('group_increase')
# async def handle_group_increase(context):
#     await bot.send(context, message='欢迎新人～',
#                    at_sender=True, auto_escape=True)
#
#
# @bot.on_request('group', 'friend')
# async def handle_request(context):
#     return {'approve': True}

base_filter.init('plugins')

bot.run(host='127.0.0.1', port=8080)


