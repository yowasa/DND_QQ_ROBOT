from peewee import *

dnd_db = SqliteDatabase("data/dnd.db")


class BaseModel(Model):
    class Meta:
        database = dnd_db
        only_save_dirty = True


class User(BaseModel):
    id = AutoField()
    qq_number = BigIntegerField(index=True, unique=True)
    cur_character_id = IntegerField(null=True)
    jrrp = IntegerField(null=True)
    jrrp_date = CharField(null=True)
    level = IntegerField(null=True)


class Character(BaseModel):
    id = AutoField()
    user_id = IntegerField(index=True)
    name = CharField(index=True)
    sex = CharField(null=True)
    camp = CharField(null=True)
    status = IntegerField(null=True)
    race = IntegerField(null=True)
    sub_race = IntegerField(null=True)
    job = IntegerField(null=True)
    sub_job = IntegerField(null=True)
    backend = CharField(null=True)
    desc = CharField(null=True)
    level = IntegerField(null=True)
    exp = IntegerField(null=True)
    hp = IntegerField(null=True)
    cur_hp = IntegerField(null=True)
    armor_hp = IntegerField(null=True)
    speed = IntegerField(null=True)


class CharacterLog(BaseModel):
    id = AutoField()
    character_id = IntegerField(index=True)
    log_content = CharField()


class CharacterLanguage(BaseModel):
    id = AutoField()
    character_id = IntegerField(index=True)
    language_id = IntegerField()


class CharacterSkilled(BaseModel):
    id = AutoField()
    character_id = IntegerField(index=True)
    skilled_id = IntegerField()


class CharacterSkill(BaseModel):
    id = AutoField()
    character_id = IntegerField(index=True)
    skill_id = IntegerField()


class CharacterExpertise(BaseModel):
    id = AutoField()
    character_id = IntegerField(index=True)
    expertise_id = IntegerField(index=True)


class Equipment(BaseModel):
    id = AutoField()
    character_id = IntegerField(index=True)
    right_hand = IntegerField()
    right_hand_name = CharField()
    right_hand_type = IntegerField()
    left_hand = IntegerField()
    left_hand_name = CharField()
    left_hand_type = IntegerField()


class Notice(BaseModel):
    id = AutoField()
    character_id = IntegerField(index=True)
    notice_code = CharField()
    notice_content = CharField()


class CharacterItem(BaseModel):
    id = AutoField()
    character_id = IntegerField(index=True)
    item_id = IntegerField()
    item_name = CharField()
    item_type = IntegerField()
    item_num = IntegerField()


class Attribute(BaseModel):
    id = AutoField()
    character_id = IntegerField(index=True)
    attr_type = IntegerField()
    str = IntegerField()
    dex = IntegerField()
    con = IntegerField()
    int = IntegerField()
    wis = IntegerField()
    cha = IntegerField()


class Weapon(BaseModel):
    id = AutoField()
    item_id = IntegerField(index=True)
    name = CharField(index=True, unique=True)
    damage = CharField()


class Armor(BaseModel):
    id = AutoField()
    item_id = IntegerField(index=True)
    name = CharField(index=True, unique=True)
    ac = CharField()
    addition = CharField()


class Item(BaseModel):
    id = AutoField()
    name = CharField()
    type = IntegerField()
    desc = CharField()


class CharacterAbnormalState(BaseModel):
    id = AutoField()
    character_id = IntegerField(index=True)
    abnormal_id = IntegerField()


class Job(BaseModel):
    id = AutoField()
    name = CharField(index=True, unique=True)
    ename = CharField(index=True, unique=True)
    life_dice = CharField()
    desc = CharField()
    limit = IntegerField()

class SubJob(BaseModel):
    id = AutoField()
    name = CharField(index=True, unique=True)
    ename = CharField(index=True, unique=True)
    type = IntegerField()
    parent_id = IntegerField()
    desc = CharField()



class Race(BaseModel):
    id = AutoField()
    name = CharField(index=True, unique=True)
    ename = CharField(index=True, unique=True)
    type = IntegerField()
    parent_race_id = IntegerField()
    size = IntegerField()
    speed = IntegerField()
    str = IntegerField()
    dex = IntegerField()
    con = IntegerField()
    int = IntegerField()
    wis = IntegerField()
    cha = IntegerField()


class RaceLanguage(BaseModel):
    id = AutoField()
    race_id = IntegerField(index=True)
    language_id = IntegerField()


class RaceSkill(BaseModel):
    id = AutoField()
    race_id = IntegerField(index=True)
    skill_id = IntegerField()


class RaceSkilled(BaseModel):
    id = AutoField()
    race_id = IntegerField(index=True)
    skilled_id = IntegerField()


class JobSkill(BaseModel):
    id = AutoField()
    subjob_id = IntegerField(index=True)
    limit_lv = IntegerField(index=True)
    skill_id = IntegerField()


class JobSkilled(BaseModel):
    id = AutoField()
    job_id = IntegerField(index=True)
    skilled_id = IntegerField()


class JobSkilledSelectAble(BaseModel):
    id = AutoField()
    job_id = IntegerField(index=True)
    skilled_id = IntegerField()


class Skill(BaseModel):
    id = AutoField()
    name = CharField(index=True, unique=True)
    ename = CharField(index=True, unique=True)
    desc = CharField()


class Language(BaseModel):
    id = AutoField()
    name = CharField(index=True, unique=True)
    ename = CharField(index=True, unique=True)
    type = IntegerField()
    usage = CharField()
    words = CharField()


class Expertise(BaseModel):
    id = AutoField()
    name = CharField(index=True, unique=True)


class Skilled(BaseModel):
    id = AutoField()
    type = IntegerField(index=True)
    name = CharField(index=True, unique=True)


class AbnormalState(BaseModel):
    id = AutoField()
    name = CharField(index=True, unique=True)
    desc = CharField()


class LevelInfo(BaseModel):
    id = AutoField()
    exp = IntegerField()
    lv = IntegerField()
    buffer = IntegerField()


class CheckInfo(BaseModel):
    id = AutoField()
    name = CharField(index=True, unique=True)
    ename = CharField()
    ref_attr = CharField()


class Alignment(BaseModel):
    id = AutoField()
    name = CharField(index=True, unique=True)
    ename = CharField()
    tag = CharField()
    desc = CharField()

# User.create_table()