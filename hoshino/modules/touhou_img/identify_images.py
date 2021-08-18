# from PIL import Image
# import tensorflow._api.v2.compat.v1 as tf
# import requests
# import hashlib
# from hoshino import Service, R
# from hoshino.typing import *
# import atexit
#
# tf.disable_v2_behavior()
# # 东方识图模块，输入图片返回人物
#
# OUTPUT_SIZE = 100  # 输出100 x 100
#
#
# # 图片地址->100*100的数组
# def extract_image(img):
#     if isinstance(img, str):
#         try:
#             img = Image.open(img, "r")
#         except:
#             return [[[]]]  # 返回空数据
#     img = img.resize(size=(OUTPUT_SIZE, OUTPUT_SIZE), resample=Image.BILINEAR)
#     pix = img.load()
#     w = img.size[0]
#     h = img.size[1]
#     data = []
#     for i in range(h):
#         row = []
#         for j in range(w):
#             try:
#                 c = pix[i, j]
#                 # 归一化
#                 row.append([c[0] / 255.0, c[1] / 255.0, c[2] / 255.0])
#             except:
#                 if isinstance(img, str):
#                     print("Error when extracting {}, maybe unsupported format".format(img))
#                 return [[[]]]
#         data.append(row)
#     return data
#
#
# CLASSES = ["Reimu", "Marisa", "Koishi", "Remilia", "Sakuya", "Cirno", "Clownpiece", "Flandre", "Patchouli",
#            "Yuyuko", "Hina", "Kaguya", "Yukari", "Yuuka", "Eirin", "Kogasa", "Youmu", "Sanae",
#            "Utsuho", "Satori"]
# CLASSES_NAME = ["博丽灵梦", "雾雨魔理沙", "古明地恋", "蕾米莉亚斯卡雷特", "十六夜咲夜", "琪露诺", "克劳恩皮丝", "芙兰朵露斯卡雷特", "帕秋莉诺雷姬",
#                 "西行寺幽幽子", "键山雏", "蓬莱山辉夜", "八云紫", "风见幽香", "八意永琳", "多多良小伞", "魂魄妖梦", "东风谷早苗",
#                 "灵乌路空", "古名地觉"]
#
#
# # 返回一个矩阵Variable
# def weight_variable(shape):
#     return tf.Variable(tf.truncated_normal(shape, stddev=0.1))
#
#
# # 返回一个向量Variable
# def bias_variable(shape):
#     return tf.Variable(tf.constant(0.1, shape=shape))
#
#
# # 神将网络的结构将在文档中说明
# InputImg = tf.placeholder(tf.float32, shape=[None, OUTPUT_SIZE, OUTPUT_SIZE, 3], name="PlaceHolder_InputImg")
# OutputAns = tf.placeholder(tf.float32, shape=[None, len(CLASSES)], name="PlaceHolder_OutputAns")
# KeepProb = tf.placeholder(tf.float32, name="KeepProb")
# TRAIN_KEEP_PROB = 0.5
# TEST_KEEP_PROB = 1.0
#
# conv1 = tf.layers.conv2d(inputs=InputImg, filters=32, kernel_size=[5, 5], padding="SAME", activation=tf.nn.relu)
# pool1 = tf.layers.max_pooling2d(inputs=conv1, pool_size=[2, 2], strides=2)
#
# conv2 = tf.layers.conv2d(inputs=pool1, filters=64, kernel_size=[5, 5], padding="SAME", activation=tf.nn.relu)
# pool2 = tf.layers.max_pooling2d(inputs=conv2, pool_size=[2, 2], strides=2)
#
# pool_flat = tf.reshape(pool2, [-1, int(OUTPUT_SIZE / 4) * int(OUTPUT_SIZE / 4) * 64])
#
# dense1 = tf.layers.dense(inputs=pool_flat, units=512, activation=tf.nn.relu,
#                          kernel_initializer=tf.truncated_normal_initializer(stddev=0.1))
# dense1_dropout = tf.nn.dropout(dense1, KeepProb)
#
# W_logistic = weight_variable([512, len(CLASSES)])
# B_logistic = bias_variable([len(CLASSES)])
# Predict = tf.nn.softmax(tf.matmul(dense1_dropout, W_logistic) + B_logistic)
#
# sv = Service('东方识图', enable_on_default=True, bundle='图片功能', help_=
# """[东方识图] {图片} 注意要加空格 或者直接输入[东方识图] 等待机器人响应后传入图片
# """)
#
# with tf.Session() as sess:
#     try:
#         saver = tf.train.Saver()
#         saver.restore(sess, '/Users/yowasa/Documents/gensokyo_model/trained_network')
#     except:
#         print("读取神经网络参数gensokyo_model失败")
#         sess.close()
# sess = tf.Session()
# try:
#     saver = tf.train.Saver()
#     saver.restore(sess, '/Users/yowasa/Documents/gensokyo_model/trained_network')
# except:
#     print("读取神经网络参数gensokyo_model失败")
#     sess.close()
#
#
# @atexit.register
# def f():
#     sess.close()
#
#
# @sv.on_command('东方识图')
# async def touhou_image(session: CommandSession):
#     bot = session.bot
#     ev = session.event
#     image_data = session.get('image', prompt='图呢？GKD')
#     if type(image_data) == list:
#         image_url = image_data[0]
#     name = image_url[image_url.rfind("/") + 1:]
#     hash_name = md5(name) + '.jpg'
#     r = requests.get(image_url, stream=True)
#     if r.status_code == 200:
#         open(R.img(f'touhou_img/{hash_name}').path, 'wb').write(r.content)
#     else:
#         await session.send("[ERROR]Download Error!")
#         return
#     img_data = extract_image(R.img(f'touhou_img/{hash_name}').path)
#     predict = list(
#         zip(sess.run(tf.reduce_sum(Predict, axis=0), feed_dict={InputImg: [img_data], KeepProb: TEST_KEEP_PROB}),
#             CLASSES_NAME))
#     # 按照概率从大到小排序
#     predict.sort(reverse=True)
#     await bot.send(ev, f"\n依据可能行排序:\n{predict[0][1]}[{int(predict[0][0]*100)}%]\n{predict[1][1]}[{int(predict[1][0]*100)}%]\n{predict[2][1]}[{int(predict[2][0]*100)}%]", at_sender=True)
#
#
# @touhou_image.args_parser
# async def _(session: CommandSession):
#     image_arg = session.current_arg_images
#
#     if session.is_first_run:
#         if image_arg:
#             session.state['image'] = image_arg[0]
#         return
#
#     if not image_arg:
#         session.pause('图呢？GKD')
#
#     session.state[session.current_key] = image_arg
#
#
# def md5(str):
#     m = hashlib.md5()
#     m.update(str.encode("utf8"))
#     print(m.hexdigest())
#     return m.hexdigest()
