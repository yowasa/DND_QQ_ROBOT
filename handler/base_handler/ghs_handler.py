# 1.导入模块
from robobrowser import RoboBrowser
from filter import msg_route

'''
ghs相关功能(未实现)
本周奶子 获取本周月曜日的丰满图片
更多奶子 获取之前一段时间的月曜日的丰满图片
随机色图 随机获取pixiv上排名靠前的图片
'''

# 用于通用处理骰子指令
@msg_route(r'本周奶子')
def dice_ex(content):
    b = RoboBrowser(history=True)
    b.open('http://twitter.com/Strangestone/media')

    ls = b.find_all(class_='content')

    for each in ls:
        each_text = each.find(class_='TweetTextSize--normal')
        if '月曜日のたわわ' in each_text.text:
            pdiv = each.find(class_='AdaptiveMedia-photoContainer')
            return pdiv.img.attrs.get('src')


