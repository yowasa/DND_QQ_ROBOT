import json
from bilibili_api import user, sync

# 实例化
u = user.User(24724312)
def resolve_origin_msg(type, origin_dic):
    msg = ""
    if type == 2:
        msg += f"{origin_dic['user']['name']}({origin_dic['user']['uid']}:\n)"
        msg += origin_dic['item']['description']
        pics = origin_dic['item']['pictures']
        for pic in pics:
            pic_img = pic['img_src']
        msg += f"\n[CQ:image,file={pic_img}]"
    elif type == 4:
        name = origin_dic["user"]["uname"]
        uid = origin_dic["user"]["uid"]
        msg += f'{name}({uid}):\n'
        msg += origin_dic['item']['content']
    elif type == 8:
        name = origin_dic["owner"]["name"]
        uid = origin_dic["owner"]["mid"]
        msg += f'{name}({uid}):\n'
        msg += origin_dic["desc"]
        msg += f"\n" + origin_dic['short_link'].replace('\\', '')
        pic = origin_dic['pic'].replace('\\', '')
        msg += f"\n[CQ:image,file={pic}]"
    elif type == 4098:
        msg += origin_dic["apiSeasonInfo"]["type_name"] + ":" + origin_dic["apiSeasonInfo"]["title"]
        cover = origin_dic['cover'].replace('\\', '')
        url = origin_dic['url'].replace('\\', '')
        msg += f"\n[CQ:image,file={cover}]"
        msg += f"\n{url}"
    else:
        msg += "未解析的回复类型，请联系开发人员!"
    return msg

async def main():
      # 用于记录下一次起点
    offset = 0

    page = await u.get_dynamics(offset)

    ori=eval(page['cards'][0]['card']['origin'].replace("null","None"))
    type=2
    result=resolve_origin_msg(type,ori)

    print("test")

# 入口
sync(main())