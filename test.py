from PIL import Image
import imageio
import os
from pygifsicle import optimize
# filestreams = []
# filedir = r'D:\Resources\img\ghs\gif\91068471_ugoira600x600'
# filenames = sorted((os.path.join(filedir,fn)  for fn in os.listdir(filedir)))
# images = []
# for filename in filenames:
#     images.append(imageio.imread(filename))
# imageio.mimsave('D:\Resources\img\ghs\gif\\test3.gif', images, duration = 0.03)
# img=Image.open('D:\Resources\img\ghs\gif\91068471_ugoira600x600.webp')
# filestreams[0].save(os.path.join('D:\Resources\img\ghs\gif','test.gif'), "gif", save_all=True, append_images=filestreams[1:],duration=30,optimize=True,loop=0)

# optimize('D:\Resources\img\ghs\gif\\test3_opt.gif', options=["--lossy"])
optimize('D:\Resources\img\ghs\gif\\91068471_ugoira600x600 - 副本.gif', options=["--lossy","--scale=0.9"])