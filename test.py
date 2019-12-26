from pixivpy3 import *

api = PixivAPI()

api.login("2508488843@qq.com","czqq872710284")

ill=api.works(72572092)

print(str(ill))

f'pixivID:{ill.response[0].get("id")}\n标题:{ill.response[0].get("title")}\n作者:{ill.response[0].get("user").get("name")}({ill.response[0].get("user").get("id")})\nTags:{" ".join([x for x in ill.response[0].get("tags")])}\n图片'
