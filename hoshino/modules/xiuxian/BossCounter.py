import os
import sqlite3

from hoshino.config.__bot__ import BASE_DB_PATH

CACHE_DB_PATH = os.path.expanduser(BASE_DB_PATH + 'xiuxian_boss_status.db')


class BossCounter():

    def __init__(self):
        os.makedirs(os.path.dirname(CACHE_DB_PATH), exist_ok=True)
        self._create_boss_status_table()

    def _connect(self):
        return sqlite3.connect(CACHE_DB_PATH)

    def _create_boss_status_table(self):
        try:
            self._connect().execute('''CREATE TABLE IF NOT EXISTS BOSS_STATUS_INFO
                          (GID             INT    NOT NULL,
                           BOSS_NAME TEXT NOT NULL DEFAULT '无',
                            HP INT NOT NULL DEFAULT 0,
                           PRIMARY KEY(GID, BOSS_NAME));''')
        except:
            raise Exception('创建Boss状态表发生错误')

    def _get_hp_by_name(self, gid, name):
        try:
            r = self._connect().execute(
                f'SELECT HP FROM BOSS_STATUS_INFO WHERE GID={gid} AND BOSS_NAME="{name}"', ).fetchall()
            if r:
                return r[0][0]
            else:
                return None
        except:
            raise Exception('查找Boss状态时发生错误')

    def _save_boss_hp_info(self, gid, name, hp):

        with self._connect() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO BOSS_STATUS_INFO (GID, BOSS_NAME, HP) VALUES (?, ?, ?)",
                (gid, name, hp)
            )


class UserDamageCounter():

    def __init__(self):
        os.makedirs(os.path.dirname(CACHE_DB_PATH), exist_ok=True)
        self._create_boss_status_table()

    def _connect(self):
        return sqlite3.connect(CACHE_DB_PATH)

    def _create_boss_status_table(self):
        try:
            self._connect().execute('''CREATE TABLE IF NOT EXISTS USER_DAMAGE_INFO
                          (GID             INT    NOT NULL,
                           UID           INT    NOT NULL,
                           BOSS_NAME TEXT NOT NULL DEFAULT '',
                            DAMAGE INT NOT NULL DEFAULT 0,
                           PRIMARY KEY(GID, UID,BOSS_NAME));''')
        except:
            raise Exception('创建用户伤害状态表发生错误')

    def _get_damage_by_name(self, gid, uid, name):
        try:
            r = self._connect().execute(
                f'SELECT DAMAGE FROM USER_DAMAGE_INFO WHERE GID={gid} AND BOSS_NAME="{name}" AND UID="{uid}"', ).fetchall()
            if r:
                return r[0][0]
            else:
                return None
        except:
            raise Exception('查找用户伤害状态时发生错误')

    def _save_user_damage_info(self, gid, uid, name, hp):

        with self._connect() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO USER_DAMAGE_INFO (GID, UID,BOSS_NAME, DAMAGE) VALUES (?, ?, ?, ?)",
                (gid, uid, name, hp)
            )
    def _get_damage_by_boss(self, gid, name):
        try:
            r = self._connect().execute(
                f'SELECT UID,DAMAGE FROM USER_DAMAGE_INFO WHERE GID={gid} AND BOSS_NAME="{name}" ORDER BY DAMAGE DESC', ).fetchall()
            if r:
                return r
            else:
                return None
        except:
            raise Exception('查找用户伤害状态时发生错误')