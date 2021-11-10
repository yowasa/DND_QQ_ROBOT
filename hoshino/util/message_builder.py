from hoshino.typing import MessageSegment
from hoshino import R
from typing import Union
from pathlib import Path
import os

IMAGE_PATH=R.get('img/ghs/cache/').path+'/'
def image(
    img_name: Union[str, Path] = None,
    path: str = None,
    abspath: str = None,
    b64: str = None,
) -> Union[MessageSegment, str]:
    """
    说明：
        生成一个 MessageSegment.image 消息
        生成顺序：绝对路径(abspath) > base64(b64) > img_name
    参数：
        :param img_name: 图片文件名称，默认在 resource/img 目录下
        :param path: 图片所在路径，默认在 resource/img 目录下
        :param abspath: 图片绝对路径
        :param b64: 图片base64
    """
    if abspath:
        return (
            MessageSegment.image("file:///" + abspath)
            if os.path.exists(abspath)
            else ""
        )
    elif isinstance(img_name, Path):
        if img_name.exists():
            return MessageSegment.image(f"file:///{img_name.absolute()}")
        return ""
    elif b64:
        return str(MessageSegment.image(b64 if "base64://" in b64 else "base64://" + b64))
    else:
        if "http" in img_name:
            return str(MessageSegment.image(img_name))
        if len(img_name.split(".")) == 1:
            img_name += ".jpg"
        file = (
            Path(IMAGE_PATH) / path / img_name if path else Path(IMAGE_PATH) / img_name
        )
        if file.exists():
            return str(MessageSegment.image(f"file:///{file.absolute()}"))
        else:
            return ""
