from peewee import *

spell_db = SqliteDatabase("data/rich_man.db")


class BaseModel(Model):
    class Meta:
        database = spell_db
        only_save_dirty = True


# 账号
class Account(BaseModel):
    id = AutoField()
    qq_number = BigIntegerField(index=True)


# 用户
class User(BaseModel):
    id = AutoField()
    qq_number = BigIntegerField(index=True)
    group_number = BigIntegerField(index=True)


# 状态
class UserStatus(BaseModel):
    id = AutoField()
    money = BigIntegerField(index=True)  # 金钱
    index = BigIntegerField(index=True)  # 在哪个位置
    ext = CharField(null=True)  # 额外信息 例如连锁店数量 用于计算收益
    item = CharField(null=True)  # 道具
    buff = CharField(null=True)  # 增益减益
    action_count = BigIntegerField(index=True)  # 剩余行动次数
    action_date = CharField(null=True)  # 刷新日期（发现日期不对刷新到指定次数）


# 游戏实例
class Game(BaseModel):
    id = AutoField()
    group_number = BigIntegerField(index=True)  # 每个群都有自己的地图
    game_status = BigIntegerField(index=True)  # 游戏状态
    inflation_ratio = BigIntegerField(index=True)  # 游戏货币膨胀系数


# 地图道路格
class Road(BaseModel):
    id = AutoField()
    game_id = BigIntegerField(index=True)  # 属于哪个游戏实例
    index = BigIntegerField(index=True)  # 道路下标
    land_id = BigIntegerField(index=True)  # 属于哪一块土地


# 土地格
class Land(BaseModel):
    id = AutoField()
    game_id = BigIntegerField(index=True)  # 属于哪个游戏实例
    type = BigIntegerField(index=True)  # 土地类型（大土地小土地公用土地）
    owner = BigIntegerField(index=True)  # 土地归属人
    build_id = BigIntegerField(index=True)  # 建筑


# 建筑
class Build(BaseModel):
    id = AutoField()
    game_id = BigIntegerField(index=True)  # 属于哪个游戏实例
    type = BigIntegerField(index=True)  # 建筑类型 1-住宅
    owner = BigIntegerField(index=True)  # 土地归属人
    build = BigIntegerField(index=True)  # 建筑


Account.create_table()
