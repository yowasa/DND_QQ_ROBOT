# 1.导入模块
from robobrowser import RoboBrowser
from filter import msg_route
import requests
import os
'''
ghs相关功能(未实现)
本周奶子 获取本周月曜日的丰满图片
更多奶子 获取之前一段时间的月曜日的丰满图片
随机色图 随机获取pixiv上排名靠前的图片
'''

env_dist = os.environ
cq_image_file = env_dist.get("cq_image_file")
if not cq_image_file:
    cq_image_file='F:\\workspace\\py\\CQP-xiaoi\\酷Q Pro\\data\\image\\'

@msg_route(r'本周奶子$')
def oppai_now(content):
    b = RoboBrowser(history=True)
    b.open('http://twitter.com/Strangestone/media')

    ls = b.find_all(class_='content')

    for each in ls:
        each_text = each.find(class_='TweetTextSize--normal')
        if '月曜日のたわわ' in each_text.text:
            pdiv = each.find(class_='AdaptiveMedia-photoContainer')
            print(pdiv.img.attrs.get('src'))
            return package_img(pdiv.img.attrs.get('src'))
# 用于通用处理骰子指令
@msg_route(r'更多奶子$')
def more_oppai(content):
    b = RoboBrowser(history=True)
    b.open('http://twitter.com/Strangestone/media')

    ls = b.find_all(class_='content')
    messagee=[]
    for each in ls:
        each_text = each.find(class_='TweetTextSize--normal')
        if '月曜日のたわわ' in each_text.text:
            pdiv = each.find(class_='AdaptiveMedia-photoContainer')
            print(pdiv.img.attrs.get('src'))
            messagee.append( package_img(pdiv.img.attrs.get('src')))
    return ','.join(messagee)

def package_img(url):
    name=url[url.rfind("/")+1:]
    str(url).split()
    r=requests.get(url,stream=True)
    if r.status_code==200:
        open(cq_image_file+name,'wb').write(r.content)
    return f'[CQ:image,file={name}]'