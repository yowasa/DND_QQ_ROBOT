from hoshino import Service
from hoshino.typing import CommandSession
from .data_source import get_anime

sv = Service('搜番', help_='''
[搜番]
'''.strip(), bundle="图片功能")


@sv.on_command('搜番')
async def traceanime(session: CommandSession):
    bot = session.bot
    ev = session.event
    img = session.get('image', prompt='图呢？GKD')
    if type(img) == list:
        img = img[0]
    image_data_report = await get_anime(img)
    await bot.send(ev, image_data_report)


@traceanime.args_parser
async def _(session: CommandSession):
    image_arg = session.current_arg_images

    if session.is_first_run:
        if image_arg:
            session.state['image'] = image_arg[0]
        return

    if not image_arg:
        session.pause('图呢？GKD')

    session.state[session.current_key] = image_arg
