# 1.导入模块
import os,zipfile
from pixivpy3 import *
import imageio

def unzip_single(src_file, dest_dir):
    zf = zipfile.ZipFile(src_file)
    try:
        zf.extractall(path=dest_dir)
    except RuntimeError as e:
        print(e)
    zf.close()

api = AppPixivAPI()

api.login("2508488843@qq.com", "czqq872710284")

result = api.ugoira_metadata(65123727)

url=result.get('ugoira_metadata').get('zip_urls').get('medium')
name = url[url.rfind("/") + 1:]
api.download(url)

path=name.replace('.zip','')
unzip_single(name,path)

path+='/'
filenames=sorted((fn for fn in os.listdir(path)))

images=[]
for filename in filenames:
    images.append(imageio.imread(path+filename))
imageio.mimsave('gif.gif', images,fps=10)






