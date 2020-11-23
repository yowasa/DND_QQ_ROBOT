import os
from pixivpy3 import *
# api = AppPixivAPI()
api = ByPassSniApi()


'''
ghs相关功能(未实现)
本周奶子 获取本周月曜日的丰满图片
更多奶子 获取之前一段时间的月曜日的丰满图片
随机色图 随机获取pixiv上排名靠前的图片
'''

env_dist = os.environ
cq_image_file = env_dist.get("cq_image_file")
if not cq_image_file:
    cq_image_file = 'D:\\workspace\\CQP-xiaoi\\酷Q Pro\\data\\image\\'

pixiv_user_name = env_dist.get("pixiv_user_name")
pixiv_password = env_dist.get("pixiv_password")

api.login(pixiv_user_name,pixiv_password)

result = api.user_illusts(8129277000)
result2=api.illust_follow(restrict='public')
result3=api.illust_follow(restrict='private')
print(result)
