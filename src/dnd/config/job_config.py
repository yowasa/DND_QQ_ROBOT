# 职业
JOB = ['野蛮人', '吟游诗人', '牧师', '德鲁伊', '战士', '武僧', '圣武士', '游侠', '游荡者', '术士', '邪术师', '法师']
JOB_DESCRIBE = {
    '战士': {
        'name': '战士',
        'hit_points': {
            'life_dice': 10,
            'base_hp': 10,
            'coordinate_attr': '体质',
            'upgrade_hp': '1d10'
        },
        'proficiencies': {
            'main_attr': ['力量', '敏捷'],
            'exemption': ['力量', '体质'],
            'skilled_weapon': ['简易武器', '军用武器'],
            'skilled_armor': ['全部护甲', '盾牌'],
            'skilled_tool': ['测试工具'],
            'skilled_item': ['杂技', '驯兽', '运动', '历史', '洞悉', '威吓', '察觉', '求生'],
            'base_skill_count': 2
        },
        'equipment': {
            '1a': ['链甲'],
            '1b': ['皮甲', '长弓', '箭(20)'],
            '2a': ['军用武器', '盾牌'],
            '2b': ['军用武器(2)'],
            '3a': ['轻弩', '弩矢(20)'],
            '3b': ['手斧(2)'],
            '4a': ['地城探险家套装'],
            '4b': ['探索者套装'],
        },
        'performance': {
            '1': ['战斗风格', '回气'],
            '2': '动作如潮(1)',
            '3': '武术范型*',
            '4': '属性值提升!',
            '5': '额外攻击',
            '6': '属性值提升!',
            '7': '范型特性*',
            '8': '属性值提升!',
            '9': '不屈(1)',
            '10': '范型特性*',
            '11': '额外攻击(2)',
            '12': '属性值提升!',
            '13': '不屈(2)',
            '14': '属性值提升!',
            '15': '范型特性*',
            '16': '属性值提升!',
            '17': ['动作如潮(2)', '不屈(3)'],
            '18': '范型特性*',
            '19': '属性值提升!',
            '20': '额外攻击(3)',
        },
    }
}
