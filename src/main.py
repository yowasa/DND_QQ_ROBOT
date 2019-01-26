from aiocqhttp import CQHttp
import dice
import attribute_controller
import user_gen
import helper
bot = CQHttp(access_token='yowasaTest',
             enable_http_post=False)


@bot.on_message()
async def handle_msg(context):
    print(context)
    commond = context['message']
    result = None
    # 骰点
    if commond.startswith('.r') and not commond.startswith('.race') and not commond.startswith('.reroll'):
        result = dice.dice_ex(context)
    # 今日人品
    if commond.startswith('.jrrp'):
        return
    # 指令说明
    if commond.startswith('.comm'):
        result = helper.comm_helper()
    # 帮助文档
    if commond.startswith('.help '):
        result=helper.helper(context)
    # 随机dnd属性
    if commond.startswith('!dnd'):
        result = attribute_controller.random_attribute()
    # 查看属性
    if commond.startswith('.attr'):
        result = attribute_controller.watch_attribute(context)
    # 生成人物
    if commond.startswith('.gen '):
        result = user_gen.gen(context)
    # 重新骰点
    if commond.startswith('.reroll'):
        result = user_gen.reroll(context)
    # 查看角色列表
    if commond.startswith('.ul'):
        result = attribute_controller.get_user_list(context)
    # 选择使用哪一个人物
    if commond.startswith('.switch '):
        result = attribute_controller.switch_user(context)

    # 交换属性
    if commond.startswith('.swap'):
        result = user_gen.swap(context)
    # todo
    if commond.startswith('.race '):
        result = user_gen.switch_race(context)
    if commond.startswith('.subrace '):
        result = user_gen.switch_sub_race(context)
    if commond.startswith('.job '):
        result = user_gen.switch_job(context)

    # 统一发送消息
    if result != None or result == '':
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


bot.run(host='127.0.0.1', port=8080)
