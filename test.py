import random
from PIL import Image
#得到正负10%的晃动比例，生成新size
def float_range(x,y):
    level = round(random.random() * 0.2 + 0.9, 2)
    return int(x * level),int(y * level)

im = Image.open('78132341_p0_master1200.jpg')
w, h = im.size
w_s,h_s=float_range(w,h)
im=im.resize((w_s, h_s))
im.save('test.png', "PNG")
