from hoshino.util.image_utils import CreateImg
from hoshino.util.message_builder import image

luxun_author = CreateImg(0, 0, plain_text="--鲁迅", font_size=30, font='msyh.ttf', font_color=(255, 255, 255))

def luxunshuo(text):
    content = text
    if content.startswith(",") or content.startswith("，"):
        content = content[1:]
    A = CreateImg(0, 0, font_size=37, background=f'./resources/img/other/luxun.jpg', font='msyh.ttf')
    x = ""
    if len(content) > 40:
        return '太长了，鲁迅说不完...'
    while A.getsize(content)[0] > A.w - 50:
        n = int(len(content) / 2)
        x += content[:n] + '\n'
        content = content[n:]
    x += content
    if len(x.split('\n')) > 2:
        return '太长了，鲁迅说不完...'
    A.text((int((480 - A.getsize(x.split("\n")[0])[0]) / 2), 300), x, (255, 255, 255))
    A.paste(luxun_author, (320, 400), True)
    return image(b64=A.pic2bs4())


