from .sauce_nao import get_image_data
from hoshino import Service, log
from hoshino.typing import *

sv = Service('搜图', enable_on_default=True, help_=
"""[搜图] {图片} 注意要加空格
""")

logger = log.new_logger('image')


@sv.on_command('image', aliases=('image', '搜图', '识图', '搜圖', '識圖'))
async def image(session: CommandSession):
    image_data = session.get('image', prompt='图呢？GKD')
    image_data_report = await get_image_data(image_data)

    if image_data_report:
        await session.send(image_data_report)
    else:
        logger.error("Not found imageInfo")
        await session.send("[ERROR]Not found imageInfo")


@image.args_parser
async def _(session: CommandSession):
    image_arg = session.current_arg_images

    if session.is_first_run:
        if image_arg:
            session.state['image'] = image_arg[0]
        return

    if not image_arg:
        session.pause('图呢？GKD')

    session.state[session.current_key] = image_arg
