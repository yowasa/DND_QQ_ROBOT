import os
import sqlite3

from hoshino.config.__bot__ import BASE_DB_PATH

CACHE_DB_PATH = os.path.expanduser(BASE_DB_PATH + 'ghs.db')


def trance_subobj(e):
    return SubObj(e)


class SubObj():
    def __init__(self, r):
        self.id = r[0]
        self.user_type = r[1]
        self.user_id = r[2]
        self.clazz = r[3]
        self.type = r[4]
        self.type_user = r[5]


def trance_sendlogobj(e):
    return SendLog(e)


class SendLog():
    def __init__(self, r):
        self.id = r[0]
        self.user_type = r[1]
        self.user_id = r[2]
        self.clazz = r[3]
        self.message_id = r[4]
        self.message_info = r[5]
        self.send_flag = r[6]


class PixivCounter():

    def __init__(self):
        os.makedirs(os.path.dirname(CACHE_DB_PATH), exist_ok=True)
        self._create_subscribe()
        self._create_subscribesendlog()
        self._create_user()
        self._create_group()

    def _connect(self):
        return sqlite3.connect(CACHE_DB_PATH)

    def _create_subscribe(self):
        try:
            self._connect().execute('''
                            create table IF NOT EXISTS subscribe
                            (
                                id INTEGER not null
                                    primary key,
                                user_type VARCHAR(255) not null,
                                user_id INTEGER not null,
                                clazz VARCHAR(255) not null,
                                type VARCHAR(255) not null,
                                type_user INTEGER not null
                            );
        ''')
        except:
            raise Exception('创建p站订阅时发生错误')

    def _create_subscribesendlog(self):
        try:
            self._connect().execute('''
                            create table IF NOT EXISTS subscribesendlog
                            (
                                id INTEGER not null
                                    primary key,
                                user_type VARCHAR(255) not null,
                                user_id INTEGER not null,
                                clazz VARCHAR(255) not null,
                                message_id INTEGER not null,
                                message_info VARCHAR(255) not null,
                                send_flag INTEGER not null default 0
                            );
        ''')
        except:
            raise Exception('创建订阅缓存时发生错误')

    def _create_user(self):
        try:
            self._connect().execute('''
                            create table IF NOT EXISTS "user"
                            (
                                qq_number INTEGER not null,
                                pixiv_detail INTEGER not null 
                            );
        ''')
        except:
            raise Exception('创建用户配置时发生错误')

    def _create_group(self):
        try:
            self._connect().execute('''
                            create table IF NOT EXISTS "group"
                            (
                                group_number INTEGER not null,
	                            auto_delete INTEGER not null 
                            );
        ''')
        except:
            raise Exception('创建群组配置时发生错误')

    def _get_subscribe_id(self, user_id, user_type, clazz, type, type_user):
        try:
            r = self._connect().execute(
                'SELECT id FROM subscribe WHERE user_id=? AND "user_type"=? AND "clazz"=? AND "type"=? AND "type_user"=?',
                (user_id, user_type, clazz, type, type_user)).fetchone()
            return 0 if r is None else r[0]
        except:
            raise Exception('获取订阅id失败')

    def _save_subscribe(self, user_id, user_type, clazz, type, type_user):
        with self._connect() as conn:
            conn.execute(
                'INSERT INTO subscribe (user_id, user_type, clazz, "type", type_user) VALUES (?, ?, ?, ?, ?)',
                (user_id, user_type, clazz, type, type_user),
            )

    def _del_by_subscribe_id(self, id):
        try:
            self._connect().execute(
                "DELETE FROM subscribe WHERE id=? ", id)

        except:
            raise Exception('删除订阅失败')

    def _select_no_user_type(self, user_id, user_type, clazz):
        try:
            r = self._connect().execute(
                'SELECT "type" FROM subscribe WHERE user_id=? AND "user_type"=? AND "clazz"=? AND "type"!="user"',
                (user_id, user_type, clazz)).fetchall()
            return [] if r is None else r
        except:
            raise Exception('查找p站缓存时生错误')

    def _select_user_type(self, user_id, user_type, clazz):
        try:
            r = self._connect().execute(
                'SELECT "type" FROM subscribe WHERE user_id=? AND "user_type"=? AND "clazz"=? AND "type"="user"',
                (user_id, user_type, clazz)).fetchall()
            return [] if r is None else r
        except:
            raise Exception('查找p站缓存时生错误')

    def _select_all_subinfo_by_class(self, clazz):
        try:
            r = self._connect().execute(
                'SELECT * FROM subscribe WHERE "clazz"=?',
                (clazz)).fetchall()
            return [] if r is None else [trance_subobj(e) for e in r]
        except:
            raise Exception('查找p站缓存时生错误')

    def select_sendlog_limit(self, user_id, user_type, send_flag, limit):
        try:
            r = self._connect().execute(
                'SELECT * FROM subscribesendlog WHERE "user_id"=? AND user_type=? AND send_flag=? limit ?',
                (user_id, user_type, send_flag, limit)).fetchall()
            return [] if r is None else [trance_sendlogobj(e) for e in r]
        except:
            raise Exception('查找p站缓存时生错误')

    def select_sendlog(self, user_id, user_type, message_id_li):
        try:
            r = self._connect().execute(
                'SELECT * FROM subscribesendlog WHERE "user_id"=? AND user_type=? AND message_id in (?)',
                (user_id, user_type, ','.join(message_id_li))).fetchall()
            return [] if r is None else [trance_sendlogobj(e) for e in r]
        except:
            raise Exception('查找p站缓存时生错误')

    def set_sendlog_flag(self, id):
        with self._connect() as conn:
            conn.execute(
                "UPDATE subscribe SET send_flag=1 WHERE id=? ", id)

    def _save_sendlog(self, user_id, user_type, clazz, message_id, message_info, send_flag=0):
        with self._connect() as conn:
            conn.execute(
                'INSERT INTO subscribe (user_id, user_type, clazz, message_id, message_info,send_flag) VALUES (?, ?, ?, ?, ?,?)',
                (user_id, user_type, clazz, message_id, message_info, send_flag),
            )

    def select_no_send_group(self):
        try:
            r = self._connect().execute(
                'SELECT * FROM subscribesendlog WHERE send_flag=0 group by user_id').fetchall()
            return [] if r is None else [trance_sendlogobj(e) for e in r]
        except:
            raise Exception('查找p站缓存时生错误')

    def _get_group_auto_delete(self, group_id):
        try:
            r = self._connect().execute(
                'SELECT auto_delete FROM "group" WHERE user_id=?', group_id).fetchone()
            return 1 if r is None else r[0]
        except:
            raise Exception('查找p站缓存时生错误')

    def _save_group_auto_delete(self, group_id, auto):
        with self._connect() as conn:
            conn.execute(
                'INSERT OR REPLACE INTO "group" (group_number, auto_delete) VALUES (?, ?)',
                (group_id, auto),
            )

    def _get_user_need_detail(self, qq_number):
        try:
            r = self._connect().execute(
                'SELECT pixiv_detail FROM "user" WHERE qq_number=?', qq_number).fetchone()
            return 0 if r is None else r[0]
        except:
            raise Exception('查找p站缓存时生错误')

    def _save_user_need_detail(self, group_id, need):
        with self._connect() as conn:
            conn.execute(
                'INSERT OR REPLACE INTO "user" (qq_number, pixiv_detail) VALUES (?, ?)',
                (group_id, need),
            )