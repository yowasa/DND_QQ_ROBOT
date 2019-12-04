from pixivpy3 import *

api = AppPixivAPI()

api.login("2508488843@qq.com","czqq872710284")

results=api.illust_ranking( mode='day_r18', date=None, offset=None)


api.download(results.illusts[20].image_urls.square_medium)

