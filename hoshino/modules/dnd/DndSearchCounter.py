import os
import sqlite3

from hoshino.config.__bot__ import BASE_DB_PATH

DB_PATH = 'data/rulateday.db'


# 记录贵族相关数据

class DndSearchCounter:
    def __init__(self):
        pass

    def _connect(self):
        return sqlite3.connect(DB_PATH)

    def _search_skill(self, name):
        try:
            r = self._connect().execute(f'select * from dnd5e_skill_phb where name like "%{name}%"').fetchall()
            return [] if r is None else r
        except:
            raise Exception('搜索技能发生错误')

    def _search_armor(self, name):
        try:
            r = self._connect().execute(f'select * from dnd5e_armor_weapon_phb where name like "%{name}%"').fetchall()
            return [] if r is None else r
        except:
            raise Exception('搜索武器发生错误')

    def _search_classes(self, name):
        try:
            r = self._connect().execute(f'select * from dnd5e_classes_phb where name like "%{name}%"').fetchall()
            return [] if r is None else r
        except Exception as e:
            raise Exception('搜索职业发生错误')

    def _search_feat(self, name):
        try:
            r = self._connect().execute(f'select * from dnd5e_feat_phb where name like "%{name}%"').fetchall()
            return [] if r is None else r
        except Exception as e:
            raise Exception('搜索专长发生错误')

    def _search_races(self, name):
        try:
            r = self._connect().execute(f'select * from dnd5e_races_phb where name like "%{name}%"').fetchall()
            return [] if r is None else r
        except Exception as e:
            raise Exception('搜索种族发生错误')

    def _search_rule(self, name):
        try:
            r = self._connect().execute(f'select * from dnd5e_rule_phb where name like "%{name}%"').fetchall()
            return [] if r is None else r
        except Exception as e:
            raise Exception('搜索规则发生错误')

    def _search_tools(self, name):
        try:
            r = self._connect().execute(f'select * from dnd5e_tools_phb where name like "%{name}%"').fetchall()
            return [] if r is None else r
        except Exception as e:
            raise Exception('搜索工具发生错误')

    def _search_spell_list(self, name):
        try:
            r = self._connect().execute(f'select * from dnd5e_spell_list_phb where name like "%{name}%"').fetchall()
            return [] if r is None else r
        except Exception as e:
            raise Exception('搜索技能发生错误')

    def _search_magic_items(self, name):
        try:
            r = self._connect().execute(f'select * from dnd5e_magic_items_dmg where name like "%{name}%"').fetchall()
            return [] if r is None else r
        except Exception as e:
            raise Exception('搜索魔术物品发生错误')

    def _search_rule_dmg(self, name):
        try:
            r = self._connect().execute(f'select * from dnd5e_rule_dmg where name like "%{name}%"').fetchall()
            return [] if r is None else r
        except Exception as e:
            raise Exception('搜索城主规则发生错误')

    def _search_background(self, name):
        try:
            r = self._connect().execute(f'select * from dnd5e_background_phb where name like "%{name}%"').fetchall()
            return [] if r is None else r
        except Exception as e:
            raise Exception('搜索背景发生错误')

    def _search_mm(self, name):
        try:
            r = self._connect().execute(f'select * from dnd5e_mm where name like "%{name}%"').fetchall()
            return [] if r is None else r
        except Exception as e:
            raise Exception('搜索怪物发生错误')

    def _radom_cn_name(self, limit):
        try:
            r = self._connect().execute(f'select name from cn_ancient_names_corpus ORDER BY RANDOM() LIMIT {limit}').fetchall()
            return [] if r is None else r
        except Exception as e:
            raise Exception('随机中文名称发生错误')

    def _radom_en_name(self, limit):
        try:
            r = self._connect().execute(f'select name from english_cn_name_corpus ORDER BY RANDOM() LIMIT {limit}').fetchall()
            return [] if r is None else r
        except Exception as e:
            raise Exception('随机英文名称发生错误')
    def _radom_jp_name(self, limit):
        try:
            r = self._connect().execute(f'select name from japanese_names_corpus ORDER BY RANDOM() LIMIT {limit}').fetchall()
            return [] if r is None else r
        except Exception as e:
            raise Exception('随机日文名称发生错误')
