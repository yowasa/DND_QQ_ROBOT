# 已经在资源目录的name转为cq码的工具类


# 包装图片名称为cq码
def package_img_2_cq_code(img_name):
    return f'[CQ:image,file={img_name}]'


# 包装图片名称为cq码(list数据)
def package_img_2_cq_code_list(img_name_list):
    cq_code_list = [package_img_2_cq_code(img) for img in img_name_list]
    return ''.join(cq_code_list)
