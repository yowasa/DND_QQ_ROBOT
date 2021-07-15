'''公主连接Re:dive的游戏数据'''
OLD_CHARA_NAME = {
    1001: ["日和", "ヒヨリ", "Hiyori", "日和莉", "猫拳", "🐱👊","日和", "ヒヨリ", "Hiyori", "日和莉", "猫拳", "🐱👊b"],
    1002: ["优衣", "ユイ", "Yui", "种田", "普田", "由衣", "结衣", "ue", "↗↘↗↘","优衣", "ユイ", "Yui", "种田", "普田", "由衣", "结衣", "ue", "↗↘↗↘b"],
    1003: ["怜", "レイ", "Rei", "剑圣", "普怜", "伶","怜", "レイ", "Rei", "剑圣", "普怜", "伶b"],
    1004: ["禊", "ミソギ", "Misogi", "未奏希", "炸弹", "炸弹人", "💣","禊", "ミソギ", "Misogi", "未奏希", "炸弹", "炸弹人", "💣b"],
    1005: ["茉莉", "マツリ", "Matsuri", "跳跳虎", "老虎", "虎", "🐅","茉莉", "マツリ", "Matsuri", "跳跳虎", "老虎", "虎", "🐅b"],
    1006: ["茜里", "アカリ", "Akari", "妹法", "妹妹法","茜里", "アカリ", "Akari", "妹法", "妹妹法b"],
    1007: ["宫子", "ミヤコ", "Miyako", "布丁", "布", "🍮","宫子", "ミヤコ", "Miyako", "布丁", "布", "🍮b"],
    1008: ["雪", "ユキ", "Yuki", "小雪", "镜子", "镜法", "伪娘", "男孩子", "男孩纸","雪", "ユキ", "Yuki", "小雪", "镜子", "镜法", "伪娘", "男孩子", "男孩纸b"],
    1009: ["杏奈", "アンナ", "Anna", "中二", "煤气罐","杏奈", "アンナ", "Anna", "中二", "煤气罐b"],
    1010: ["真步", "マホ", "Maho", "狐狸", "真扎", "咕噜灵波", "真布", "🦊","真步", "マホ", "Maho", "狐狸", "真扎", "咕噜灵波", "真布", "🦊b"],
    1011: ["璃乃", "リノ", "Rino", "妹弓","璃乃", "リノ", "Rino", "妹弓b"],
    1012: ["初音", "ハツネ", "Hatsune", "hego", "星法", "星星法", "⭐法", "睡法","初音", "ハツネ", "Hatsune", "hego", "星法", "星星法", "⭐法", "睡法b"],
    1013: ["七七香", "ナナカ", "Nanaka", "娜娜卡", "77k", "77香","七七香", "ナナカ", "Nanaka", "娜娜卡", "77k", "77香b"],
    1014: ["霞", "カスミ", "Kasumi", "香澄", "侦探", "杜宾犬", "驴", "驴子", "🔍","霞", "カスミ", "Kasumi", "香澄", "侦探", "杜宾犬", "驴", "驴子", "🔍b"],
    1015: ["美里", "ミサト", "Misato", "圣母","美里", "ミサト", "Misato", "圣母b"],
    1016: ["铃奈", "スズナ", "Suzuna", "暴击弓", "暴弓", "爆击弓", "爆弓", "政委","铃奈", "スズナ", "Suzuna", "暴击弓", "暴弓", "爆击弓", "爆弓", "政委b"],
    1017: ["香织", "カオリ", "Kaori", "琉球犬", "狗子", "狗", "狗拳", "🐶", "🐕", "🐶👊🏻", "🐶👊","香织", "カオリ", "Kaori", "琉球犬", "狗子", "狗", "狗拳", "🐶", "🐕", "🐶👊🏻", "🐶👊b"],
    1018: ["伊绪", "イオ", "Io", "老师", "魅魔","伊绪", "イオ", "Io", "老师", "魅魔b"],

    1020: ["美美", "ミミ", "Mimi", "兔子", "兔兔", "兔剑", "萝卜霸断剑", "人参霸断剑", "天兔霸断剑", "🐇", "🐰","美美", "ミミ", "Mimi", "兔子", "兔兔", "兔剑", "萝卜霸断剑", "人参霸断剑", "天兔霸断剑", "🐇", "🐰b"],
    1021: ["胡桃", "クルミ", "Kurumi", "铃铛", "🔔","胡桃", "クルミ", "Kurumi", "铃铛", "🔔b"],
    1022: ["依里", "ヨリ", "Yori", "姐法", "姐姐法","依里", "ヨリ", "Yori", "姐法", "姐姐法b"],
    1023: ["绫音", "アヤネ", "Ayane", "熊锤", "🐻🔨", "🐻","绫音", "アヤネ", "Ayane", "熊锤", "🐻🔨", "🐻b"],

    1025: ["铃莓", "スズメ", "Suzume", "女仆", "妹抖","铃莓", "スズメ", "Suzume", "女仆", "妹抖b"],
    1026: ["铃", "リン", "Rin", "松鼠", "🐿", "🐿️","铃", "リン", "Rin", "松鼠", "🐿", "🐿️b"],
    1027: ["惠理子", "エリコ", "Eriko", "病娇","惠理子", "エリコ", "Eriko", "病娇b"],
    1028: ["咲恋", "サレン", "Saren", "充电宝", "青梅竹马", "幼驯染", "院长", "园长", "🔋", "普电","咲恋", "サレン", "Saren", "充电宝", "青梅竹马", "幼驯染", "院长", "园长", "🔋", "普电b"],
    1029: ["望", "ノゾミ", "Nozomi", "偶像", "小望", "🎤","望", "ノゾミ", "Nozomi", "偶像", "小望", "🎤b"],
    1030: ["妮诺", "ニノン", "Ninon", "妮侬", "扇子","妮诺", "ニノン", "Ninon", "妮侬", "扇子b"],
    1031: ["忍", "シノブ", "Shinobu", "普忍", "鬼父", "💀","忍", "シノブ", "Shinobu", "普忍", "鬼父", "💀b"],
    1032: ["秋乃", "アキノ", "Akino", "哈哈剑","秋乃", "アキノ", "Akino", "哈哈剑b"],
    1033: ["真阳", "マヒル", "Mahiru", "奶牛", "🐄", "🐮", "真☀","真阳", "マヒル", "Mahiru", "奶牛", "🐄", "🐮", "真☀b"],
    1034: ["优花梨", "ユカリ", "Yukari", "由加莉", "黄骑", "酒鬼", "奶骑", "圣骑", "🍺", "🍺👻","优花梨", "ユカリ", "Yukari", "由加莉", "黄骑", "酒鬼", "奶骑", "圣骑", "🍺", "🍺👻b"],

    1036: ["镜华", "キョウカ", "Kyouka", "小仓唯", "xcw", "小苍唯", "8岁", "八岁", "喷水萝", "八岁喷水萝", "8岁喷水萝","镜华", "キョウカ", "Kyouka", "小仓唯", "xcw", "小苍唯", "8岁", "八岁", "喷水萝", "八岁喷水萝", "8岁喷水萝b"],
    1037: ["智", "トモ", "Tomo", "卜毛","智", "トモ", "Tomo", "卜毛b"],
    1038: ["栞", "シオリ", "Shiori", "tp弓", "小栞", "白虎弓", "白虎妹","栞", "シオリ", "Shiori", "tp弓", "小栞", "白虎弓", "白虎妹b"],

    1040: ["碧", "アオイ", "Aoi", "香菜", "香菜弓", "绿毛弓", "毒弓", "绿帽弓", "绿帽","碧", "アオイ", "Aoi", "香菜", "香菜弓", "绿毛弓", "毒弓", "绿帽弓", "绿帽b"],

    1042: ["千歌", "チカ", "Chika", "绿毛奶","千歌", "チカ", "Chika", "绿毛奶b"],
    1043: ["真琴", "マコト", "Makoto", "狼", "🐺", "月月", "朋", "狼姐","真琴", "マコト", "Makoto", "狼", "🐺", "月月", "朋", "狼姐b"],
    1044: ["伊莉亚", "イリヤ", "Iriya", "伊利亚", "伊莉雅", "伊利雅", "yly", "吸血鬼", "那个女人","伊莉亚", "イリヤ", "Iriya", "伊利亚", "伊莉雅", "伊利雅", "yly", "吸血鬼", "那个女人b"],
    1045: ["空花", "クウカ", "Kuuka", "抖m", "抖","空花", "クウカ", "Kuuka", "抖m", "抖b"],
    1046: ["珠希", "タマキ", "Tamaki", "猫剑", "🐱剑", "🐱🗡️","珠希", "タマキ", "Tamaki", "猫剑", "🐱剑", "🐱🗡️b"],
    1047: ["纯", "ジュン", "Jun", "黑骑", "saber","纯", "ジュン", "Jun", "黑骑", "saberb"],
    1048: ["美冬", "ミフユ", "Mifuyu", "子龙", "赵子龙","美冬", "ミフユ", "Mifuyu", "子龙", "赵子龙b"],
    1049: ["静流", "シズル", "Shizuru", "姐姐","静流", "シズル", "Shizuru", "姐姐b"],
    1050: ["美咲", "ミサキ", "Misaki", "大眼", "👀", "👁️", "👁","美咲", "ミサキ", "Misaki", "大眼", "👀", "👁️", "👁b"],
    1051: ["深月", "ミツキ", "Mitsuki", "眼罩", "抖s","深月", "ミツキ", "Mitsuki", "眼罩", "抖sb"],
    1052: ["莉玛", "リマ", "Rima", "Lima", "草泥马", "羊驼", "🦙", "🐐","莉玛", "リマ", "Rima", "Lima", "草泥马", "羊驼", "🦙", "🐐b"],
    1053: ["莫妮卡", "モニカ", "Monika", "毛二力","莫妮卡", "モニカ", "Monika", "毛二力b"],
    1054: ["纺希", "ツムギ", "Tsumugi", "裁缝", "蜘蛛侠", "🕷️", "🕸️","纺希", "ツムギ", "Tsumugi", "裁缝", "蜘蛛侠", "🕷️", "🕸️b"],
    1055: ["步未", "アユミ", "Ayumi", "步美", "路人", "路人妹","步未", "アユミ", "Ayumi", "步美", "路人", "路人妹b"],
    1056: ["流夏", "ルカ", "Ruka", "大姐", "大姐头", "儿力", "luka", "刘夏","流夏", "ルカ", "Ruka", "大姐", "大姐头", "儿力", "luka", "刘夏b"],
    1057: ["吉塔", "ジータ", "Jiita", "姬塔", "团长", "吉他", "🎸", "骑空士", "qks","吉塔", "ジータ", "Jiita", "姬塔", "团长", "吉他", "🎸", "骑空士", "qksb"],
    1058: ["贪吃佩可", "ペコリーヌ", "Pecoriinu", "佩可莉姆", "吃货", "佩可", "公主", "饭团", "🍙","贪吃佩可", "ペコリーヌ", "Pecoriinu", "佩可莉姆", "吃货", "佩可", "公主", "饭团", "🍙b"],
    1059: ["可可萝", "コッコロ", "Kokkoro", "可可罗", "妈", "普白","可可萝", "コッコロ", "Kokkoro", "可可罗", "妈", "普白b"],
    1060: ["凯留", "キャル", "Kyaru", "凯露", "百地希留耶", "希留耶", "Kiruya", "黑猫", "臭鼬", "普黑", "接头霸王", "街头霸王","凯留", "キャル", "Kyaru", "凯露", "百地希留耶", "希留耶", "Kiruya", "黑猫", "臭鼬", "普黑", "接头霸王", "街头霸王b"],
    1061: ["矛依未", "ムイミ", "Muimi", "诺维姆", "Noemu","511", "无意义", "天楼霸断剑","矛依未", "ムイミ", "Muimi", "诺维姆", "Noemu", "511", "无意义", "天楼霸断剑b"],

    1063: ["亚里莎", "アリサ", "Arisa", "鸭梨瞎", "瞎子", "亚里沙", "鸭梨傻", "亚丽莎", "亚莉莎", "瞎子弓", "🍐🦐", "yls","亚里莎", "アリサ", "Arisa", "鸭梨瞎", "瞎子", "亚里沙", "鸭梨傻", "亚丽莎", "亚莉莎", "瞎子弓", "🍐🦐", "ylsb"],
    1064: ["雪菲","シェフィ","冰龙","小蓝龙"],
    1065: ["嘉夜", "カヤ", "Kaya", "憨憨龙", "龙拳", "🐲👊🏻", "🐉👊🏻", "接龙笨比","嘉夜", "カヤ", "Kaya", "憨憨龙", "龙拳", "🐲👊🏻", "🐉👊🏻", "接龙笨比b"],
    1066: ["祈梨", "イノリ", "Inori", "梨老八", "李老八","祈梨", "イノリ", "Inori", "梨老八", "李老八b"],
    1067: ["穗希", "ホマレ", "Homare","穗希", "ホマレ", "Homareb"],
    1068: ["拉比林斯达", "ラビリスタ", "Rabirisuta", "迷宫女王", "模索路晶", "模索路", "晶", "王晶","拉比林斯达", "ラビリスタ", "Rabirisuta", "迷宫女王", "模索路晶", "模索路", "晶", "王晶b"],
    1069: ["真那", "マナ", "Mana", "霸瞳皇帝", "千里真那", "千里", "霸瞳", "霸铜","真那", "マナ", "Mana", "霸瞳皇帝", "千里真那", "千里", "霸瞳", "霸铜b"],
    1070: ["似似花", "ネネカ", "Neneka", "变貌大妃", "现士实似似花", "現士実似々花", "現士実", "现士实", "nnk", "448", "捏捏卡", "变貌", "大妃","似似花", "ネネカ", "Neneka", "变貌大妃", "现士实似似花", "現士実似々花", "現士実", "现士实", "nnk", "448", "捏捏卡", "变貌", "大妃b"],
    1071: ["克莉丝提娜", "クリスティーナ", "Kurisutiina", "誓约女君", "克莉丝提娜·摩根", "Christina", "Cristina", "克总", "女帝", "克", "摩根","克莉丝提娜", "クリスティーナ", "Kurisutiina", "誓约女君", "克莉丝提娜·摩根", "Christina", "Cristina", "克总", "女帝", "克", "摩根b"],
    1072: ["可萝爹", "長老", "Chourou", "岳父", "爷爷","可萝爹", "長老", "Chourou", "岳父", "爷爷b"],
    1073: ["拉基拉基", "ラジニカーント", "Rajinigaanto", "跳跃王", "Rajiraji", "Lajilaji", "垃圾垃圾", "教授","拉基拉基", "ラジニカーント", "Rajinigaanto", "跳跃王", "Rajiraji", "Lajilaji", "垃圾垃圾", "教授b"],

    1075: ["贪吃佩可(夏日)", "ペコリーヌ(サマー)", "Pekoriinu(Summer)", "佩可莉姆(夏日)", "水吃", "水饭", "水吃货", "水佩可", "水公主", "水饭团", "水🍙", "泳吃", "泳饭", "泳吃货", "泳佩可", "泳公主", "泳饭团", "泳🍙", "泳装吃货", "泳装公主", "泳装饭团", "泳装🍙", "佩可(夏日)", "🥡", "👙🍙", "泼妇","贪吃佩可(夏日)", "ペコリーヌ(サマー)", "Pekoriinu(Summer)", "佩可莉姆(夏日)", "水吃", "水饭", "水吃货", "水佩可", "水公主", "水饭团", "水🍙", "泳吃", "泳饭", "泳吃货", "泳佩可", "泳公主", "泳饭团", "泳🍙", "泳装吃货", "泳装公主", "泳装饭团", "泳装🍙", "佩可(夏日)", "🥡", "👙🍙", "泼妇b"],
    1076: ["可可萝(夏日)", "コッコロ(サマー)", "Kokkoro(Summer)", "水白", "水妈", "水可", "水可可", "水可可萝", "水可可罗", "泳装妈", "泳装可可萝", "泳装可可罗","可可萝(夏日)", "コッコロ(サマー)", "Kokkoro(Summer)", "水白", "水妈", "水可", "水可可", "水可可萝", "水可可罗", "泳装妈", "泳装可可萝", "泳装可可罗b"],
    1077: ["铃莓(夏日)", "スズメ(サマー)", "Suzume(Summer)", "水女仆", "水妹抖","铃莓(夏日)", "スズメ(サマー)", "Suzume(Summer)", "水女仆", "水妹抖b"],
    1078: ["凯留(夏日)", "キャル(サマー)", "Kyaru(Summer)", "水黑", "水黑猫", "水臭鼬", "泳装黑猫", "泳装臭鼬", "潶", "溴", "💧黑","凯留(夏日)", "キャル(サマー)", "Kyaru(Summer)", "水黑", "水黑猫", "水臭鼬", "泳装黑猫", "泳装臭鼬", "潶", "溴", "💧黑b"],
    1079: ["珠希(夏日)", "タマキ(サマー)", "Tamaki(Summer)", "水猫剑", "水猫", "渵", "💧🐱🗡️", "水🐱🗡️","珠希(夏日)", "タマキ(サマー)", "Tamaki(Summer)", "水猫剑", "水猫", "渵", "💧🐱🗡️", "水🐱🗡️b"],
    1080: ["美冬(夏日)", "ミフユ(サマー)", "Mifuyu(Summer)", "水子龙", "水美冬","美冬(夏日)", "ミフユ(サマー)", "Mifuyu(Summer)", "水子龙", "水美冬b"],
    1081: ["忍(万圣节)", "シノブ(ハロウィン)", "Shinobu(Halloween)", "万圣忍", "瓜忍", "🎃忍", "🎃💀","忍(万圣节)", "シノブ(ハロウィン)", "Shinobu(Halloween)", "万圣忍", "瓜忍", "🎃忍", "🎃💀b"],
    1082: ["宫子(万圣节)", "ミヤコ(ハロウィン)", "Miyako(Halloween)", "万圣宫子", "万圣布丁", "狼丁", "狼布丁", "万圣🍮", "🐺🍮", "🎃🍮", "👻🍮","宫子(万圣节)", "ミヤコ(ハロウィン)", "Miyako(Halloween)", "万圣宫子", "万圣布丁", "狼丁", "狼布丁", "万圣🍮", "🐺🍮", "🎃🍮", "👻🍮b"],
    1083: ["美咲(万圣节)", "ミサキ(ハロウィン)", "Misaki(Halloween)", "万圣美咲", "万圣大眼", "瓜眼", "🎃眼", "🎃👀", "🎃👁️", "🎃👁","美咲(万圣节)", "ミサキ(ハロウィン)", "Misaki(Halloween)", "万圣美咲", "万圣大眼", "瓜眼", "🎃眼", "🎃👀", "🎃👁️", "🎃👁b"],
    1084: ["千歌(圣诞节)", "チカ(クリスマス)", "Chika(Xmas)", "圣诞千歌", "圣千", "蛋鸽", "🎄💰🎶", "🎄千🎶", "🎄1000🎶","千歌(圣诞节)", "チカ(クリスマス)", "Chika(Xmas)", "圣诞千歌", "圣千", "蛋鸽", "🎄💰🎶", "🎄千🎶", "🎄1000🎶b"],
    1085: ["胡桃(圣诞节)", "クルミ(クリスマス)", "Kurumi(Xmas)", "圣诞胡桃", "圣诞铃铛","胡桃(圣诞节)", "クルミ(クリスマス)", "Kurumi(Xmas)", "圣诞胡桃", "圣诞铃铛b"],
    1086: ["绫音(圣诞节)", "アヤネ(クリスマス)", "Ayane(Xmas)", "圣诞熊锤", "蛋锤", "圣锤", "🎄🐻🔨", "🎄🐻","绫音(圣诞节)", "アヤネ(クリスマス)", "Ayane(Xmas)", "圣诞熊锤", "蛋锤", "圣锤", "🎄🐻🔨", "🎄🐻b"],
    1087: ["日和(新年)", "ヒヨリ(ニューイヤー)", "Hiyori(NewYear)", "新年日和", "春猫", "👘🐱","日和(新年)", "ヒヨリ(ニューイヤー)", "Hiyori(NewYear)", "新年日和", "春猫", "👘🐱b"],
    1088: ["优衣(新年)", "ユイ(ニューイヤー)", "Yui(NewYear)", "新年优衣", "春田", "新年由衣","优衣(新年)", "ユイ(ニューイヤー)", "Yui(NewYear)", "新年优衣", "春田", "新年由衣b"],
    1089: ["怜(新年)", "レイ(ニューイヤー)", "Rei(NewYear)", "春剑", "春怜", "春伶", "新春剑圣", "新年怜", "新年剑圣","怜(新年)", "レイ(ニューイヤー)", "Rei(NewYear)", "春剑", "春怜", "春伶", "新春剑圣", "新年怜", "新年剑圣b"],
    1090: ["惠理子(情人节)", "エリコ(バレンタイン)", "Eriko(Valentine)", "情人节病娇", "恋病", "情病", "恋病娇", "情病娇","惠理子(情人节)", "エリコ(バレンタイン)", "Eriko(Valentine)", "情人节病娇", "恋病", "情病", "恋病娇", "情病娇b"],
    1091: ["静流(情人节)", "シズル(バレンタイン)", "Shizuru(Valentine)", "情人节静流", "情姐", "情人节姐姐","静流(情人节)", "シズル(バレンタイン)", "Shizuru(Valentine)", "情人节静流", "情姐", "情人节姐姐b"],
    1092: ["安", "アン", "An", "胖安", "55kg","安", "アン", "An", "胖安", "55kgb"],
    1093: ["露", "ルゥ", "Ruu", "逃课女王","露", "ルゥ", "Ruu", "逃课女王b"],
    1094: ["古蕾娅", "グレア", "Gurea", "龙姬", "古雷娅", "古蕾亚", "古雷亚", "🐲🐔", "🐉🐔","古蕾娅", "グレア", "Gurea", "龙姬", "古雷娅", "古蕾亚", "古雷亚", "🐲🐔", "🐉🐔b"],
    1095: ["空花(大江户)", "クウカ(オーエド)", "Kuuka(Ooedo)", "江户空花", "江户抖m", "江m", "花m", "江花","空花(大江户)", "クウカ(オーエド)", "Kuuka(Ooedo)", "江户空花", "江户抖m", "江m", "花m", "江花b",'大江户空花'],
    1096: ["妮诺(大江户)", "ニノン(オーエド)", "Ninon(Ooedo)", "江户扇子", "忍扇","妮诺(大江户)", "ニノン(オーエド)", "Ninon(Ooedo)", "江户扇子", "忍扇b"],
    1097: ["雷姆", "レム", "Remu", "蕾姆","雷姆", "レム", "Remu", "蕾姆b"],
    1098: ["拉姆", "ラム", "Ramu","拉姆", "ラム", "Ramub"],
    1099: ["爱蜜莉雅", "エミリア", "Emiria", "艾米莉亚", "emt","爱蜜莉雅", "エミリア", "Emiria", "艾米莉亚", "emtb"],
    1100: ["铃奈(夏日)", "スズナ(サマー)", "Suzuna(Summer)", "瀑击弓", "水爆", "水爆弓", "水暴", "瀑", "水暴弓", "瀑弓", "泳装暴弓", "泳装爆弓","铃奈(夏日)", "スズナ(サマー)", "Suzuna(Summer)", "瀑击弓", "水爆", "水爆弓", "水暴", "瀑", "水暴弓", "瀑弓", "泳装暴弓", "泳装爆弓b"],
    1101: ["伊绪(夏日)", "イオ(サマー)", "Io(Summer)", "水魅魔", "水老师", "泳装魅魔", "泳装老师","伊绪(夏日)", "イオ(サマー)", "Io(Summer)", "水魅魔", "水老师", "泳装魅魔", "泳装老师b"],
    1103: ["咲恋(夏日)", "サレン(サマー)", "Saren(Summer)", "水电", "泳装充电宝", "泳装咲恋", "水着咲恋", "水电站", "水电宝", "水充", "👙🔋","咲恋(夏日)", "サレン(サマー)", "Saren(Summer)", "水电", "泳装充电宝", "泳装咲恋", "水着咲恋", "水电站", "水电宝", "水充", "👙🔋b"],
    1104: ["真琴(夏日)", "マコト(サマー)", "Makoto(Summer)", "水狼", "浪", "水🐺", "泳狼", "泳月", "泳月月", "泳朋", "水月", "水月月", "水朋", "👙🐺","真琴(夏日)", "マコト(サマー)", "Makoto(Summer)", "水狼", "浪", "水🐺", "泳狼", "泳月", "泳月月", "泳朋", "水月", "水月月", "水朋", "👙🐺b"],
    1105: ["香织(夏日)", "カオリ(サマー)", "Kaori(Summer)", "水狗", "泃", "水🐶", "水🐕", "泳狗","香织(夏日)", "カオリ(サマー)", "Kaori(Summer)", "水狗", "泃", "水🐶", "水🐕", "泳狗b"],
    1106: ["真步(夏日)", "マホ(サマー)", "Maho(Summer)", "水狐狸", "水狐", "水壶", "水真步", "水maho", "氵🦊", "水🦊", "💧🦊","真步(夏日)", "マホ(サマー)", "Maho(Summer)", "水狐狸", "水狐", "水壶", "水真步", "水maho", "氵🦊", "水🦊", "💧🦊b"],
    1107: ["碧(插班生)", "アオイ(編入生)", "Aoi(Hennyuusei)", "生菜", "插班碧","碧(插班生)", "アオイ(編入生)", "Aoi(Hennyuusei)", "生菜", "插班碧b"],
    1108: ["克萝依", "クロエ", "Kuroe", "华哥", "黑江", "黑江花子", "花子","克萝依", "クロエ", "Kuroe", "华哥", "黑江", "黑江花子", "花子b"],
    1109: ["琪爱儿", "チエル", "Chieru", "切露", "茄露", "茄噜", "切噜","琪爱儿", "チエル", "Chieru", "切露", "茄露", "茄噜", "切噜b"],
    1110: ["优妮", "ユニ", "Yuni", "真行寺由仁", "由仁", "u2", "优妮辈先", "辈先", "书记", "uni", "先辈", "仙贝", "油腻", "优妮先辈", "学姐", "18岁黑丝学姐","优妮", "ユニ", "Yuni", "真行寺由仁", "由仁", "u2", "优妮辈先", "辈先", "书记", "uni", "先辈", "仙贝", "油腻", "优妮先辈", "学姐", "18岁黑丝学姐b"],
    1111: ["镜华(万圣节)", "キョウカ(ハロウィン)", "Kyouka(Halloween)", "万圣镜华", "万圣小仓唯", "万圣xcw", "猫仓唯", "黑猫仓唯", "mcw", "猫唯", "猫仓", "喵唯","镜华(万圣节)", "キョウカ(ハロウィン)", "Kyouka(Halloween)", "万圣镜华", "万圣小仓唯", "万圣xcw", "猫仓唯", "黑猫仓唯", "mcw", "猫唯", "猫仓", "喵唯b"],
    1112: ["禊(万圣节)", "ミソギ(ハロウィン)", "Misogi(Halloween)", "万圣禊", "万圣炸弹人", "瓜炸弹人", "万圣炸弹", "万圣炸", "瓜炸", "南瓜炸", "🎃💣","禊(万圣节)", "ミソギ(ハロウィン)", "Misogi(Halloween)", "万圣禊", "万圣炸弹人", "瓜炸弹人", "万圣炸弹", "万圣炸", "瓜炸", "南瓜炸", "🎃💣b"],
    1113: ["美美(万圣节)", "ミミ(ハロウィン)", "Mimi(Halloween)", "万圣兔", "万圣兔子", "万圣兔兔", "绷带兔", "绷带兔子", "万圣美美", "绷带美美", "万圣🐰", "绷带🐰", "🎃🐰", "万圣🐇", "绷带🐇", "🎃🐇","美美(万圣节)", "ミミ(ハロウィン)", "Mimi(Halloween)", "万圣兔", "万圣兔子", "万圣兔兔", "绷带兔", "绷带兔子", "万圣美美", "绷带美美", "万圣🐰", "绷带🐰", "🎃🐰", "万圣🐇", "绷带🐇", "🎃🐇b"],
    1114: ["露娜", "ルナ", "Runa", "露仓唯", "露cw","露娜", "ルナ", "Runa", "露仓唯", "露cwb"],
    1115: ["克莉丝提娜(圣诞节)", "クリスティーナ(クリスマス)", "Kurisutiina(Xmas)", "Christina(Xmas)", "Cristina(Xmas)", "圣诞克", "圣诞克总", "圣诞女帝", "蛋克", "圣克", "必胜客","克莉丝提娜(圣诞节)", "クリスティーナ(クリスマス)", "Kurisutiina(Xmas)", "Christina(Xmas)", "Cristina(Xmas)", "圣诞克", "圣诞克总", "圣诞女帝", "蛋克", "圣克", "必胜客b"],
    1116: ["望(圣诞节)", "ノゾミ(クリスマス)", "Nozomi(Xmas)", "圣诞望", "圣诞偶像", "蛋偶像", "蛋望","望(圣诞节)", "ノゾミ(クリスマス)", "Nozomi(Xmas)", "圣诞望", "圣诞偶像", "蛋偶像", "蛋望b"],
    1117: ["伊莉亚(圣诞节)", "イリヤ(クリスマス)", "Iriya(Xmas)", "圣诞伊莉亚", "圣诞伊利亚", "圣诞伊莉雅", "圣诞伊利雅", "圣诞yly", "圣诞吸血鬼", "圣伊", "圣yly","伊莉亚(圣诞节)", "イリヤ(クリスマス)", "Iriya(Xmas)", "圣诞伊莉亚", "圣诞伊利亚", "圣诞伊莉雅", "圣诞伊利雅", "圣诞yly", "圣诞吸血鬼", "圣伊", "圣ylyb"],

    1119: ["可可萝(新年)", "コッコロ(ニューイヤー)", "Kokkoro(NewYear)", "春可可", "春白", "新年妈", "春妈","可可萝(新年)", "コッコロ(ニューイヤー)", "Kokkoro(NewYear)", "春可可", "春白", "新年妈", "春妈b"],
    1120: ["凯留(新年)", "キャル(ニューイヤー)", "Kyaru(NewYear)", "春凯留", "春黑猫", "春黑", "春臭鼬", "新年凯留", "新年黑猫", "新年臭鼬", "唯一神","凯留(新年)", "キャル(ニューイヤー)", "Kyaru(NewYear)", "春凯留", "春黑猫", "春黑", "春臭鼬", "新年凯留", "新年黑猫", "新年臭鼬", "唯一神b"],
    1121: ["铃莓(新年)", "スズメ(ニューイヤー)", "Suzume(NewYear)", "春铃莓", "春女仆", "春妹抖", "新年铃莓", "新年女仆", "新年妹抖","铃莓(新年)", "スズメ(ニューイヤー)", "Suzume(NewYear)", "春铃莓", "春女仆", "春妹抖", "新年铃莓", "新年女仆", "新年妹抖b"],
    1122: ["霞(魔法少女)", "カスミ(マジカル)", "Kasumi(MagiGirl)", "魔法少女霞", "魔法侦探", "魔法杜宾犬", "魔法驴", "魔法驴子", "魔驴", "魔法霞", "魔法少驴","霞(魔法少女)", "カスミ(マジカル)", "Kasumi(MagiGirl)", "魔法少女霞", "魔法侦探", "魔法杜宾犬", "魔法驴", "魔法驴子", "魔驴", "魔法霞", "魔法少驴b"],
    1123: ["栞(魔法少女)", "シオリ(マジカル)", "Shiori(MagiGirl)", "魔法少女栞", "魔法tp弓", "魔法小栞", "魔法白虎弓", "魔法白虎妹", "魔法白虎", "魔栞","栞(魔法少女)", "シオリ(マジカル)", "Shiori(MagiGirl)", "魔法少女栞", "魔法tp弓", "魔法小栞", "魔法白虎弓", "魔法白虎妹", "魔法白虎", "魔栞b"],
    1124: ["卯月(偶像大师)", "ウヅキ(デレマス)", "Udsuki(DEREM@S)", "卯月", "卵用", "Udsuki(DEREMAS)", "岛村卯月","卯月(偶像大师)", "ウヅキ(デレマス)", "Udsuki(DEREM@S)", "卯月", "卵用", "Udsuki(DEREMAS)", "岛村卯月b"],
    1125: ["凛(偶像大师)", "リン(デレマス)", "Rin(DEREM@S)", "凛", "Rin(DEREMAS)", "涩谷凛", "西部凛","凛(偶像大师)", "リン(デレマス)", "Rin(DEREM@S)", "凛", "Rin(DEREMAS)", "涩谷凛", "西部凛b"],
    1126: ["未央(偶像大师)", "ミオ(デレマス)", "Mio(DEREM@S)", "未央", "Mio(DEREMAS)", "本田未央","未央(偶像大师)", "ミオ(デレマス)", "Mio(DEREM@S)", "未央", "Mio(DEREMAS)", "本田未央b"],
    1127: ["铃(游侠)", "リン(レンジャー)", "Rin(Ranger)", "骑兵松鼠", "游侠松鼠", "游骑兵松鼠", "护林员松鼠", "护林松鼠", "游侠🐿️", "武松","铃(游侠)", "リン(レンジャー)", "Rin(Ranger)", "骑兵松鼠", "游侠松鼠", "游骑兵松鼠", "护林员松鼠", "护林松鼠", "游侠🐿️", "武松b"],
    1128: ["真阳(游侠)", "マヒル(レンジャー)", "Mahiru(Ranger)", "骑兵奶牛", "游侠奶牛", "游骑兵奶牛", "护林员奶牛", "护林奶牛", "游侠🐄", "游侠🐮","真阳(游侠)", "マヒル(レンジャー)", "Mahiru(Ranger)", "骑兵奶牛", "游侠奶牛", "游骑兵奶牛", "护林员奶牛", "护林奶牛", "游侠🐄", "游侠🐮b"],
    1129: ["璃乃(奇境)", "リノ(ワンダー)", "Rino(Wonder)", "璃乃(仙境)", "爽弓", "爱丽丝弓", "爱弓", "兔弓", "奇境妹弓", "仙境妹弓", "白丝妹弓","璃乃(奇境)", "リノ(ワンダー)", "Rino(Wonder)", "璃乃(仙境)", "爽弓", "爱丽丝弓", "爱弓", "兔弓", "奇境妹弓", "仙境妹弓", "白丝妹弓b"],
    1130: ["步未(奇境)", "アユミ(ワンダー)", "Ayumi(Wonder)", "步未(仙境)", "路人兔", "兔人妹", "爱丽丝路人", "奇境路人", "仙境路人","步未(奇境)", "アユミ(ワンダー)", "Ayumi(Wonder)", "步未(仙境)", "路人兔", "兔人妹", "爱丽丝路人", "奇境路人", "仙境路人b"],
    1131: ["流夏(夏日)", "ルカ(サマー)", "Ruka(Summer)", "泳装流夏", "水流夏", "泳装刘夏", "水刘夏", "泳装大姐", "泳装大姐头", "水大姐", "水大姐头", "水儿力", "泳装儿力", "水流","流夏(夏日)", "ルカ(サマー)", "Ruka(Summer)", "泳装流夏", "水流夏", "泳装刘夏", "水刘夏", "泳装大姐", "泳装大姐头", "水大姐", "水大姐头", "水儿力", "泳装儿力", "水流b"],
    1132: ["杏奈(夏日)", "アンナ(サマー)", "Anna(Summer)", "泳装中二", "泳装煤气罐", "水中二", "水煤气罐", "冲", "冲二","杏奈(夏日)", "アンナ(サマー)", "Anna(Summer)", "泳装中二", "泳装煤气罐", "水中二", "水煤气罐", "冲", "冲二b"],
    1133: ["七七香(夏日)", "ナナカ(サマー)", "Nanaka(Summer)", "泳装娜娜卡", "泳装77k", "泳装77香", "水娜娜卡", "水77k", "水77香", "水nnk","水七七香","七七香(夏日)", "ナナカ(サマー)", "Nanaka(Summer)", "泳装娜娜卡", "泳装77k", "泳装77香", "水娜娜卡", "水77k", "水77香", "水nnk","水七七香b"],
    1134: ["初音(夏日)", "ハツネ(サマー)", "Hatsune(Summer)", "水星", "海星", "水hego", "水星法", "泳装星法", "水⭐法", "水睡法", "湦","初音(夏日)", "ハツネ(サマー)", "Hatsune(Summer)", "水星", "海星", "水hego", "水星法", "泳装星法", "水⭐法", "水睡法", "湦b",'水初音','泳装初音'],
    1135: ["美里(夏日)", "ミサト(サマー)", "Misato(Summer)", "水母", "泳装圣母", "水圣母","美里(夏日)", "ミサト(サマー)", "Misato(Summer)", "水母", "泳装圣母", "水圣母b"],
    1136: ["纯(夏日)", "ジュン(サマー)", "Jun(Summer)", "泳装黑骑", "水黑骑", "泳装纯", "水纯", "小次郎","纯(夏日)", "ジュン(サマー)", "Jun(Summer)", "泳装黑骑", "水黑骑", "泳装纯", "水纯", "小次郎b"],
    1137: ["茜里(天使)", "アカリ(エンジェル)", "Akari(Angel)", "天使妹法", "天使茜里", "丘比特妹法","茜里(天使)", "アカリ(エンジェル)", "Akari(Angel)", "天使妹法", "天使茜里", "丘比特妹法b"],
    1138: ["依里(天使)", "ヨリ(エンジェル)", "Yori(Angel)", "天使姐法", "天使依里", "丘比特姐法","依里(天使)", "ヨリ(エンジェル)", "Yori(Angel)", "天使姐法", "天使依里", "丘比特姐法b"],
    1139: ["纺希(万圣节)", "ツムギ(ハロウィン)", "Tsumugi(Halloween)", "万圣裁缝", "万圣蜘蛛侠", "🎃🕷️", "🎃🕸️", "万裁", "瓜裁", "鬼裁", "鬼才","纺希(万圣节)", "ツムギ(ハロウィン)", "Tsumugi(Halloween)", "万圣裁缝", "万圣蜘蛛侠", "🎃🕷️", "🎃🕸️", "万裁", "瓜裁", "鬼裁", "鬼才b"],
    1140: ["怜(万圣节)", "レイ(ハロウィン)", "Rei(Halloween)", "万圣剑圣", "万剑", "瓜剑", "瓜怜", "万圣怜","怜(万圣节)", "レイ(ハロウィン)", "Rei(Halloween)", "万圣剑圣", "万剑", "瓜剑", "瓜怜", "万圣怜b"],
    1141: ["茉莉(万圣节)", "マツリ(ハロウィン)", "Matsuri(Halloween)", "万圣跳跳虎", "万圣老虎", "瓜虎", "🎃🐅","茉莉(万圣节)", "マツリ(ハロウィン)", "Matsuri(Halloween)", "万圣跳跳虎", "万圣老虎", "瓜虎", "🎃🐅b"],
    1142: ["莫妮卡(魔法少女)", "モニカ(マジカル)", "魔法少女莫妮卡", "魔二力","莫妮卡(魔法少女)", "モニカ(マジカル)", "魔法少女莫妮卡", "魔二力b",'魔法莫妮卡','魔法毛二力'],
    1143: ["智(魔法少女)", "トモ(マジカル)", "魔法少女智", "9智","智(魔法少女)", "トモ(マジカル)", "魔法少女智", "9智", "⑨b",'魔智','魔法智'],
    1144: ["秋乃(圣诞节)", "アキノ(クリスマス)", "Akino(Xmas)", "圣剑", "生煎", "圣诞哈哈剑", "哈哈剑(圣诞节)", "圣哈", "蛋哈", "蛋剑","秋乃(圣诞节)", "アキノ(クリスマス)", "Akino(Xmas)", "圣剑", "生煎", "圣诞哈哈剑", "哈哈剑(圣诞节)", "圣哈", "蛋哈", "蛋剑b"],
    1145: ["咲恋(圣诞节)", "サレン(クリスマス)", "Saren(Xmas)", "圣诞充电宝", "圣电", "圣诞咲恋","咲恋(圣诞节)", "サレン(クリスマス)", "Saren(Xmas)", "圣诞充电宝", "圣电", "圣诞咲恋b"],
    1146: ["优花梨(圣诞节)", "ユカリ(クリスマス)", "Yukari(Xmas)", "蛋黄", "由加莉(圣诞节)", "圣诞黄骑", "圣诞圣骑", "蛋骑", "黄骑(圣诞节)","优花梨(圣诞节)", "ユカリ(クリスマス)", "Yukari(Xmas)", "蛋黄", "由加莉(圣诞节)", "圣诞黄骑", "圣诞圣骑", "蛋骑", "黄骑(圣诞节)b"],
    1147: ["矛依未(新年)", "ムイミ（ニューイヤー）", "春511", "新春511", "新年511","矛依未(新年)", "ムイミ（ニューイヤー）", "春511", "新春511", "新年511b"],
    1150: ["似似花(新年)", "春nnk", "春似似花", "春妃", "新年nnk", "新春nnk","似似花(新年)", "春nnk", "春似似花", "春妃", "新年nnk", "新春nnkb",],
    # =================================== #
    1155: ["可可萝(仪装束)","コッコロ(儀装束)","礼妈","礼仪妈","礼服妈","姨妈","可可萝(仪装束)","コッコロ(儀装束)","礼妈","礼仪妈","礼服妈","姨妈b",'仪妈'],
    1156: ["优衣(仪装束)","ユイ(儀装束)","礼优衣","礼仪优衣","礼服优衣","礼田","礼装优衣","优衣(仪装束)","ユイ(儀装束)","礼优衣","礼仪优衣","礼服优衣","礼田","礼装优衣b",'礼ue','礼服ue'],
    1701: ["环奈","桥本环奈","毛大力","环奈","桥本环奈","毛大力b"],
    1702: ["环奈(振袖)","新春环奈","振袖环奈","春环","环奈(振袖)","新春环奈","振袖环奈","春环b"],
    1801: ["日和(公主)", "ヒヨリ（プリンセス）","公主猫拳","fes猫拳","日和(公主)", "ヒヨリ（プリンセス）","公主猫拳","fes猫拳b"],
    1802: ["优衣(公主)", "ユイ(プリンセス)", "Yui(Princess)", "公主优衣", "公主yui", "公主种田", "公主田", "公主ue", "掉毛优衣", "掉毛yui", "掉毛ue", "掉毛", "飞翼优衣", "飞翼ue", "飞翼", "飞翼高达","优衣(公主)", "ユイ(プリンセス)", "Yui(Princess)", "公主优衣", "公主yui", "公主种田", "公主田", "公主ue", "掉毛优衣", "掉毛yui", "掉毛ue", "掉毛", "飞翼优衣", "飞翼ue", "飞翼", "飞翼高达b"],

    1804: ["贪吃佩可(公主)", "ペコリーヌ(プリンセス)", "Pekoriinu(Princess)", "公主吃", "公主饭", "公主吃货", "公主佩可", "公主饭团", "公主🍙", "命运高达", "高达", "命运公主", "高达公主", "命吃", "春哥高达", "🤖🍙", "🤖","贪吃佩可(公主)", "ペコリーヌ(プリンセス)", "Pekoriinu(Princess)", "公主吃", "公主饭", "公主吃货", "公主佩可", "公主饭团", "公主🍙", "命运高达", "高达", "命运公主", "高达公主", "命吃", "春哥高达", "🤖🍙", "🤖b"],
    1805: ["可可萝(公主)", "コッコロ（プリンセス）", "Kokkoro(Princess)", "公主妈", "月光妈", "蝶妈", "蝴蝶妈", "月光蝶妈", "公主可", "公主可萝", "公主可可萝", "月光可", "月光可萝", "月光可可萝", "蝶可", "蝶可萝", "蝶可可萝","可可萝(公主)", "コッコロ（プリンセス）", "Kokkoro(Princess)", "公主妈", "月光妈", "蝶妈", "蝴蝶妈", "月光蝶妈", "公主可", "公主可萝", "公主可可萝", "月光可", "月光可萝", "月光可可萝", "蝶可", "蝶可萝", "蝶可可萝b"],
}
