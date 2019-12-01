from aiocqhttp import CQHttp
import filter

bot = CQHttp(api_root="http://127.0.0.1:5700/",
             access_token="yowasaTest",
             secret="3909432")


@bot.on_message()
async def handle_msg(context):
    content = context.copy()
    result = filter.filter(content)
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


bot.run(host='127.0.0.1', port=8080)
