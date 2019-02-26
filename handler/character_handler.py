from filter import msg_route
from tool.dnd_db import *
from handler.dice_handler import init_attribute
import base.formate as fmt
import re
import base.tool as tool

ATTRIBUTE = ['力量', '体质', '敏捷', '智力', '感知', '魅力']

attr_type = {
    '可选': 1,
    '基础': 2,
    '当前': 3,
    '临时': 4
}

character_status = {
    10: '选择属性',
    20: '选择种族',
    21: '半精灵选择属性',
    22: '矮人选择工匠工具',
    23: '半精灵选择技能熟练项',
    25: '选择亚种',
    26: '选择额外语言',
    30: '选择职业',

}


# 生成角色
@msg_route(r'\s*\.gen ', need_user=True)
def gen(content):
    # 获得用户
    cmd_msg = content['cmd_msg']
    user = content.get('sys_user')

    if not cmd_msg or cmd_msg == '':
        return '请输入名称'

    character = Character.get_or_none(Character.user_id == int(user.id), Character.name == cmd_msg)
    if character:
        return f'角色{cmd_msg}已存在'
    character = Character(name=cmd_msg)
    character.user_id = user.id
    character.status = 10
    character.save()
    user.cur_character_id = character.id
    user.save()
    for _ in range(5):
        attr_dict = init_attribute()
        attr = fmt.dict2attr(attr_dict)
        attr.character_id = character.id
        attr.attr_type = 1
        attr.save()

    return f'生成角色 {character.name} 成功 使用.guid 操作查看创建指引\n'


@msg_route(r'\s*\.guid', need_character=True)
def guid_gen(content):
    user = content.get('sys_user')
    character = content.get('sys_character')
    if not character:
        return '当前没有角色'
    sb = f'角色：{character.name}'
    if character.status == 10:
        sb += '\n从以下属性中根据编号选择一组属性使用 .choose + 编号 选择一组属性使用'
        query = Attribute.select().where(Attribute.character_id == character.id, Attribute.attr_type == 1)
        inx = 0
        for s in query:
            inx += 1
            attr_dict = fmt.attr2dict(s)
            msg = fmt.attr_dict2str(attr_dict)
            sb += f'\n{inx} : {msg}'
    if character.status == 20:
        sb += '\n从以下种族中选择一个种族 .choose + 编号'
        query = Race.select().where(Race.type == 1)
        inx = 0
        for s in query:
            inx += 1
            sb += f'\n{inx} : {s.name}'
    if character.status == 21:
        sb += '\n由于半精灵特性,从以下属性中选择两个属性 .choose + 编号1 编号2'
        inx = 0
        for s in ['力量', '敏捷', '体质', '智力', '感知']:
            inx += 1
            sb += f'\n{inx} : {s}'
    if character.status == 22:
        sb += '\n由于矮人特性,从以下三个工匠工具中中选择一个工具熟练项 .choose + 编号'
        inx = 0
        for s in ['铁匠工具', '酿酒工具', '石匠工具']:
            inx += 1
            sb += f'\n{inx} : {s}'
    if character.status == 23:
        sb += '\n由于半精灵特性,从以下技能熟练项中选择两个熟练项 .choose + 编号1 编号2'
        query = Skilled.select().where(Skilled.type.in_((31, 32, 33, 34, 35)))
        inx = 0
        for s in query:
            inx += 1
            sb += f'\n{inx} : {s.name}'
    if character.status == 25:
        query = Race.select().where(Race.parent_race_id == character.race, Race.type == 2)
        sb += '\n从以下亚种中选择一个亚种 .choose + 编号'
        inx = 0
        for s in query:
            inx += 1
            sb += f'\n{inx} : {s.name}'
    if character.status == 26:
        sb += '\n由于种族额外语言的特性,从以下语言中选择一个语言 .choose + 编号'
        pre_query = CharacterLanguage.select().where(CharacterLanguage.character_id == character.id)
        ll = {s.id for s in pre_query}
        query = Language.select() \
            .where(Language.id.not_in(ll))
        inx = 0
        for s in query:
            inx += 1
            sb += f'\n{inx} : {s.name}'
    if character.status == 30:
        query = Job.select()
        sb += '\n从以下职业中选择一个职业 .choose + 编号'
        inx = 0
        for s in query:
            inx += 1
            sb += f'\n{inx} : {s.name}'
    if character.status == 35:
        job = Job.get(id=character.job)
        query = Skilled.select(Skilled, JobSkilledSelectAble) \
            .join(JobSkilledSelectAble, on=(JobSkilledSelectAble.skilled_id == Skilled.id)) \
            .where(JobSkilledSelectAble.job_id == character.job)
        sb += f'\n从以下技能熟练项中选择{job.limit}个熟练项习得 .choose + 编号1 编号2 ..'
        inx = 0
        for s in query:
            inx += 1
            sb += f'\n{inx} : {s.name}'
    if character.status == 70:
        sb += '\n从以下背景中选择一个背景 .choose + 编号（未完成尽请期待）'
    return sb


@msg_route(r'\s*\.choose ', need_character=True)
def guid_choose(content):
    user = content.get('sys_user')
    character = content.get('sys_character')
    cmd_msg = content.get('cmd_msg')
    if character.status == 10:
        choose_num = int(cmd_msg)
        query = Attribute.select().where(Attribute.character_id == character.id, Attribute.attr_type == 1)
        flag = False
        inx = 0
        for s in query:
            inx += 1
            if inx == choose_num:
                flag = True
                s.attr_type = 2
                s.save()
            s.delete()
        if flag:
            character.status = 20
            character.save()
            return '选择属性成功,在选择种族之前可以任意调用.swap 属性a 属性b 交换你的属性值'
        return '请选择正确的数字'
    if character.status == 20:
        choose_num = int(cmd_msg)
        query = Race.select().where(Race.type == 1)
        inx = 0
        for s in query:
            inx += 1
            if inx == choose_num:
                update_race_info(character, s)
                if s.name == '半精灵':
                    character.status = 21
                    character.save()
                    return f"选择种族 {s.name} 成功"
                if s.name == '矮人':
                    character.status = 22
                    character.save()
                    return f"选择种族 {s.name} 成功"
                if s.name == '人类':
                    character.status = 26
                    character.save()
                    return f"选择种族 {s.name} 成功"
                # 亚种判断
                num = Race.select().where(Race.parent_race_id == s.id).count()
                if num > 0:
                    character.status = 25
                else:
                    character.status = 30
                character.save()
                return f"选择种族 {s.name} 成功"
        return '请选择正确的数字'
    if character.status == 21:
        msg_m = re.compile(r'[1-5]').findall(cmd_msg)
        if len(msg_m) != 2:
            return '请输入1-5的两个数字'
        num1 = int(msg_m[0])
        num2 = int(msg_m[1])
        if num1 == num2:
            return '请选择两种不同的属性'
        attr = ['力量', '敏捷', '体质', '智力', '感知']
        key1 = fmt.attr_des2key(attr[num1 - 1])
        key2 = fmt.attr_des2key(attr[num2 - 1])
        attrobj = Attribute.get(Attribute.character_id == character.id, Attribute.attr_type == 3)
        setattr(attrobj, key1, getattr(attrobj, key1) + 1)
        setattr(attrobj, key2, getattr(attrobj, key2) + 1)
        attrobj.save()
        character.status = 23
        character.save()
        return f'选择属性 {attr[num1 - 1]} {attr[num2 - 1]}成功'

    if character.status == 22:
        choose_num = int(cmd_msg)
        inx = 0
        for s in ['铁匠工具', '酿酒工具', '石匠工具']:
            inx += 1
            if inx == choose_num:
                skilled = Skilled.get(Skilled.name == s)
                CharacterSkilled(character_id=character.id, skilled_id=skilled.id).save()
                # 亚种判断
                num = Race.select().where(Race.parent_race_id == character.race).count()
                if num > 0:
                    character.status = 25
                else:
                    character.status = 30
                character.save()
                return f'选择工具 {s} 成功'
        return '请选择正确的数字'
    if character.status == 23:
        msg_m = re.compile(r'1[1-8]|[1-9]').findall(cmd_msg)
        if len(msg_m) != 2:
            return '请输入1-18的两个数字'
        query = Skilled.select().where(Skilled.type.in_((31, 32, 33, 34, 35)))
        inx = 0
        for s in query:
            inx += 1
            if str(inx) in msg_m:
                CharacterSkilled(character_id=character.id, skilled_id=s.id).save()
        character.status = 26
        character.save()
        return '选择技能熟练项成功'

    if character.status == 25:
        choose_num = int(cmd_msg)
        query = Race.select().where(Race.parent_race_id == character.race, Race.type == 2)
        inx = 0
        for s in query:
            inx += 1
            if inx == choose_num:
                update_sub_race_info(character, s)
                if s.name == '高等精灵':
                    character.status = 26
                else:
                    character.status = 30
                character.save()
                return f"选择亚种 {s.name} 成功"
        return '请选择正确的数字'
    if character.status == 26:
        choose_num = int(cmd_msg)
        pre_query = CharacterLanguage.select().where(CharacterLanguage.character_id == character.id)
        ll = {s.id for s in pre_query}
        query = Language.select() \
            .where(Language.id.not_in(ll))
        inx = 0
        for s in query:
            inx += 1
            if inx == choose_num:
                CharacterLanguage(character_id=character.id, language_id=s.id).save()
                character.status = 30
                character.save()
                return f'选择语言 {s.name} 成功'
        return '请选择正确的数字'
    if character.status == 30:
        choose_num = int(cmd_msg)
        query = Job.select()
        inx = 0
        for s in query:
            inx += 1
            if inx == choose_num:
                update_job_info(character, s)
                character.status = 35
                character.save()
                return f'选择职业 {s.name} 成功'
        return '请选择正确的数字'
    if character.status == 35:
        job = Job.get(id=character.job)
        msg_m = re.compile(r'1[1-8]|[1-9]').findall(cmd_msg)
        if len(msg_m) != job.limit:
            return f'请输入{job.limit}数字'
        query = Skilled.select(Skilled, JobSkilledSelectAble) \
            .join(JobSkilledSelectAble, on=(JobSkilledSelectAble.skilled_id == Skilled.id)) \
            .where(JobSkilledSelectAble.job_id == character.job)
        inx = 0
        for s in query:
            inx += 1
            if str(inx) in msg_m:
                CharacterSkilled(character_id=character.id, skilled_id=s.id).save()
        character.status = 70
        character.save()
        return '选择熟练项成功'


# 交换属性
@msg_route('\s*\.swap ', need_character=True)
def swap(content):
    # 交换属性
    comm = content.get('cmd_msg')
    attr_list = comm.split(' ')
    attr1 = attr_list[0]
    if attr1 not in ATTRIBUTE:
        return f'不存在 {attr1} 这种属性'
    attr2 = attr_list[1]
    if attr2 not in ATTRIBUTE:
        return f'不存在 {attr2} 这种属性'
    if attr1 == attr2:
        return '请输入两种不同的属性'
    user = content.get('sys_user')
    character = content.get('sys_character')

    if character.status > 20:
        return '不可变更属性'
    attr = Attribute.get(Attribute.character_id == character.id, Attribute.attr_type == 2)

    cache = getattr(attr, fmt.attr_des2key(attr1))
    setattr(attr, fmt.attr_des2key(attr1), getattr(attr, fmt.attr_des2key(attr2)))
    setattr(attr, fmt.attr_des2key(attr2), cache)
    attr.save()
    return '交换属性成功'


def update_race_info(character, race):
    character.race = race.id
    character.speed = race.speed
    # 增加属性
    attr = Attribute.get(Attribute.character_id == character.id, Attribute.attr_type == 2)
    dict = fmt.attr2dict(attr)
    dict_buffer = fmt.attr2dict(race)
    for k, v in dict_buffer.items():
        base_v = dict.get(k)
        dict_buffer[k] = base_v + v
    cur_attr = fmt.dict2attr(dict_buffer)
    cur_attr.character_id = character.id
    cur_attr.attr_type = 3
    cur_attr.save()
    # 增加语言
    query = RaceLanguage.select().where(RaceLanguage.race_id == race.id)
    for rl in query:
        CharacterLanguage.create(character_id=character.id, language_id=rl.language_id)
    # 增加技能
    query_skill = RaceSkill.select().where(RaceSkill.race_id == race.id)
    for rs in query_skill:
        CharacterSkill.create(character_id=character.id, skill_id=rs.skill_id)


def update_sub_race_info(character, race):
    character.sub_race = race.id
    character.speed = race.speed
    # 增加属性
    attr = Attribute.get(Attribute.character_id == character.id, Attribute.attr_type == 3)
    dict = fmt.attr2dict(attr)
    dict_buffer = fmt.attr2dict(race)
    for k, v in dict_buffer.items():
        base_v = dict.get(k)
        dict_buffer[k] = base_v + v
    cur_attr = fmt.dict2attr(dict_buffer)
    cur_attr.id = attr.id
    cur_attr.character_id = character.id
    cur_attr.attr_type = 3
    cur_attr.save()
    # 增加技能
    query_skill = RaceSkill.select().where(RaceSkill.race_id == race.id)
    for rs in query_skill:
        CharacterSkill.create(character_id=character.id, skill_id=rs.skill_id)


def update_job_info(character, job):
    character.job = job.id
    life_dice = job.life_dice
    # 更新角色hp
    character.hp = int(life_dice.replace('d', ''))
    # 判断矮人刚毅
    query = Skill.select(Skill, CharacterSkill) \
        .join(CharacterSkill, on=(CharacterSkill.skill_id == Skill.id)) \
        .where(CharacterSkill.character_id == character.id, Skill.name == '矮人刚毅')
    if query.count():
        character.hp += 1
    # 获得体质调整值加值
    attr = Attribute.get(Attribute.character_id == character.id, Attribute.attr_type == 3)
    plus = tool.get_check_plus(attr.con)
    character.hp += plus
    # 获得熟练项
    query = JobSkilled.select().where(JobSkilled.job_id == job.id)
    for s in query:
        if not CharacterSkilled.select().where(CharacterSkilled.skilled_id == s.skilled_id).count():
            CharacterSkilled(character_id=character.id, skilled_id=s.skilled_id).save()
    # 获得技能
    query2 = JobSkill.select().where(JobSkill.subjob_id == character.job, JobSkill.limit_lv == 1)
    for s in query2:
        if not CharacterSkill.select().where(CharacterSkill.skill_id == s.skill_id).count():
            CharacterSkill(character_id=character.id, skill_id=s.skill_id).save()
    # 初始化经验值
    character.level = 0
    character.exp = 0


@msg_route(r'\s*\.attr', need_character=True)
def watch_attribute(content):
    user = content.get('sys_user')
    character = content.get('sys_character')
    if not character:
        return '当前没有角色'
    sb = f'角色：{character.name}'
    if character.race:
        race = Race.get(Race.id == character.race)
        sb += f"\n种族:{race.name}"
    if character.sub_race:
        race = Race.get(Race.id == character.sub_race)
        sb += f"\n亚种:{race.name}"
    if character.job:
        job = Job.get(Job.id == character.race)
        sb += f"\n种族:{job.name}"

    if character.status > 10:
        attr = Attribute.get(Attribute.character_id == character.id, Attribute.attr_type == 2)
        attr_dict = fmt.attr2dict(attr)
        msg = fmt.attr_dict2str(attr_dict)
        sb += "\n基础属性为:"
        sb += "\n" + msg
    if character.status > 20:
        attr = Attribute.get(Attribute.character_id == character.id, Attribute.attr_type == 3)
        attr_dict = fmt.attr2dict(attr)
        msg = fmt.attr_dict2str(attr_dict)
        sb += "\n当前属性为:"
        sb += "\n" + msg
    if character.speed:
        sb += f"\n速度: {character.speed}"
    if character.level:
        sb += f"\n等级: {character.level}"
    if character.exp:
        sb += f"\n经验值: {character.exp}"
    if character.hp:
        sb += f"\nhp: {character.hp}"
    # 语言列表
    query1 = Language.select(Language, CharacterLanguage) \
        .join(CharacterLanguage, on=(CharacterLanguage.language_id == Language.id)) \
        .where(CharacterLanguage.character_id == character.id)
    if query1.count():
        sb += "\n语言列表:"
        sb += '\n' + ' '.join(([s.name for s in query1]))
    # 技能列表
    query2 = Skill.select(Skill,CharacterSkill)\
        .join(CharacterSkill,on=(CharacterSkill.skill_id==Skill.id)).where(CharacterSkill.character_id == character.id)
    if query2.count():
        sb += "\n技能列表:"
        sb += '\n' + ' '.join(([s.name for s in query2]))
    # 熟练工具列表
    query3 = Skilled.select(Skilled, CharacterSkilled) \
        .join(CharacterSkilled, on=(CharacterSkilled.skilled_id == Skilled.id)) \
        .where(CharacterSkilled.character_id == character.id)
    if query3.count():
        sb += "\n工具熟练项:"
        craftsman = {s.name for s in query3 if s.type == 2}
        if craftsman:
            sb += f"工匠工具:{craftsman} "
        gambling = {s.name for s in query3 if s.type == 3}
        if gambling:
            sb += f"赌博工具:{gambling} "
        music = {s.name for s in query3 if s.type == 4}
        if music:
            sb += f"乐器:{music} "
        other = {s.name for s in query3 if s.type == 1}
        sb += ' '.join(other)
        weapon = {s.name for s in query3 if s.type in (10, 11, 12)}
        if weapon:
            sb += "\n武器熟练项:"
            sb += ' '.join(weapon)
        arm = {s.name for s in query3 if s.type in (20, 21)}
        if arm:
            sb += "\n护甲熟练项:"
            sb += ' '.join(arm)
        immune = {s.name for s in query3 if s.type == 30}
        if arm:
            sb += "\n豁免熟练项:"
            sb += ' '.join(immune)
        sk_item = {s.name for s in query3 if s.type in (31, 32, 33, 34, 35)}
        if sk_item:
            sb += "\n技能熟练项:"
            sb += ' '.join(sk_item)
    return sb

# 查看简版人物卡
