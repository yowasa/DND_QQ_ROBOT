# 获得属性加值
def get_check_plus(attr):
    attr = int(attr)
    if attr - 10 >= 0:
        return int((attr - 10) / 2)
    if attr - 10 < 0:
        return int((attr - 11) / 2)
