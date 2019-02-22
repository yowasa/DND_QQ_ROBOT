from peewee import *

spell_db = SqliteDatabase("data/spell.db")


class BaseModel(Model):
    class Meta:
        database = spell_db
        only_save_dirty = True


class Job(BaseModel):
    id = AutoField()
    name = CharField(index=True, unique=True)
    ename = CharField(index=True, unique=True)


class Spell(BaseModel):
    id = AutoField()
    name = CharField(index=True, unique=True)
    ename = CharField(index=True, unique=True)
    level = IntegerField()
    type = CharField(null=True)
    cast_time = CharField(null=True)
    cast_range = CharField(null=True)
    component = CharField(null=True)
    duration = CharField(null=True)
    describe = TextField(null=True)


class JobSpell(BaseModel):
    job = ForeignKeyField(Job, backref='spells')
    spell = ForeignKeyField(Spell, backref='jobs')
