# 条件校验


# 检验condition
def checkCondition(user, condition):
    conditions = parseCondition(condition);
    return checkParsedConditions(user, conditions);


# 解析condition字符串为condition列表
def parseCondition(condition: str):
    conditions = []
    length = len(condition)
    cursor = 0;

    def catch_string(index):
        result = condition[cursor:index].strip()
        if result:
            conditions.append(result)

    for i in range(length):
        if condition[i] == ' ':
            continue
        elif condition[i] == '(':
            catch_string(i + 1)
            cursor = i + 1
        elif condition[i] == ')':
            catch_string(i)
            cursor = i
            catch_string(i + 1)
            cursor = i + 1
        elif condition[i] in ['&', '|']:
            catch_string(i)
            cursor = i
            catch_string(i + 1)
            cursor = i + 1
    catch_string(length);
    return conditions;


# 执行引擎
def checkParsedConditions(user, conditions):
    length = len(conditions)
    if length == 0:
        return True
    if length == 1:
        return checkProp(user, conditions[0])
    result = []
    for i in conditions:
        if i not in ['|', "&", "(", ")"]:
            result.append(checkProp(user, i))
        else:
            result.append(i)
    eval_str = ''.join([str(i) for i in result])
    return eval(eval_str)


def checkProp(user, condition: str):
    if '!' in condition:
        condition = condition.replace('!', " in ")
        if 'TLT' in condition:
            for i in user.data['天赋']:
                judg = condition.replace('TLT', str(i))
                if eval(judg):
                    return False
            return True
        if 'EVT' in condition:
            for i in user.data['事件']:
                judg = condition.replace('EVT', str(i))
                if eval(judg):
                    return False
            return True
    if '?' in condition:
        condition = condition.replace('?', " in ")
        if 'TLT' in condition:
            for i in user.data['天赋']:
                judg = condition.replace('TLT', str(i))
                if eval(judg):
                    return True
            return False
        if 'EVT' in condition:
            for i in user.data['事件']:
                judg = condition.replace('EVT', str(i))
                if eval(judg):
                    return True
            return False
    eff_li = ["SPR", "MNY", "CHR", "STR", "INT", "AGE"]
    key_li = ["快乐", "家境", "颜值", "体质", "智力", "年龄"]
    judg = condition
    for i in eff_li:
        if i in condition:
            index = eff_li.index(i)
            judg = judg.replace(i, str(user.data[key_li[index]]))
    return eval(judg)
