import asyncio
import base64
import os
import random
import sqlite3
import math
from datetime import datetime, timedelta
from io import BytesIO
from PIL import Image
from hoshino import Service, priv
from hoshino.modules.priconne.pcr_duel import _pcr_duel_data as _pcr_data
from hoshino.modules.priconne.pcr_duel import duel_chara as chara
from hoshino.typing import CQEvent
from hoshino.util import DailyNumberLimiter
import copy
import json
from hoshino.config.__bot__ import BASE_DB_PATH

SCORE_DB_PATH = os.path.expanduser(BASE_DB_PATH + 'pcr_running_counter.db')


# 用于与赛跑金币互通
class ScoreCounter2:
    def __init__(self):
        os.makedirs(os.path.dirname(SCORE_DB_PATH), exist_ok=True)
        self._create_table()
        self._create_pres_table()

    def _connect(self):
        return sqlite3.connect(SCORE_DB_PATH)

    def _create_table(self):
        try:
            self._connect().execute('''CREATE TABLE IF NOT EXISTS SCORECOUNTER
                          (GID             INT    NOT NULL,
                           UID             INT    NOT NULL,
                           SCORE           INT    NOT NULL,
                           PRIMARY KEY(GID, UID));''')
        except:
            raise Exception('创建表发生错误')

    def _add_score(self, gid, uid, score):
        try:
            current_score = self._get_score(gid, uid)
            inscore = math.ceil(current_score + score)
            conn = self._connect()
            conn.execute("INSERT OR REPLACE INTO SCORECOUNTER (GID,UID,SCORE) \
                                VALUES (?,?,?)", (gid, uid, inscore))
            conn.commit()
        except:
            raise Exception('更新表发生错误')

    def _reduce_score(self, gid, uid, score):
        try:
            current_score = self._get_score(gid, uid)
            if current_score >= score:
                inscore = math.ceil(current_score - score)
                conn = self._connect()
                conn.execute("INSERT OR REPLACE INTO SCORECOUNTER (GID,UID,SCORE) \
                                VALUES (?,?,?)", (gid, uid, inscore))
                conn.commit()
            else:
                conn = self._connect()
                conn.execute("INSERT OR REPLACE INTO SCORECOUNTER (GID,UID,SCORE) \
                                VALUES (?,?,?)", (gid, uid, 0))
                conn.commit()
        except:
            raise Exception('更新表发生错误')

    def _get_score(self, gid, uid):
        try:
            r = self._connect().execute("SELECT SCORE FROM SCORECOUNTER WHERE GID=? AND UID=?", (gid, uid)).fetchone()
            return 0 if r is None else r[0]
        except:
            raise Exception('查找表发生错误')

    # 判断金币是否足够下注
    def _judge_score(self, gid, uid, score):
        try:
            current_score = self._get_score(gid, uid)
            if current_score >= score:
                return 1
            else:
                return 0
        except Exception as e:
            raise Exception(str(e))

    # 记录国王声望数据
    def _create_pres_table(self):
        try:
            self._connect().execute('''CREATE TABLE IF NOT EXISTS PRESTIGECOUNTER
                          (GID             INT    NOT NULL,
                           UID             INT    NOT NULL,
                           PRESTIGE           INT    NOT NULL,
                           PRIMARY KEY(GID, UID));''')
        except:
            raise Exception('创建表发生错误')

    def _set_prestige(self, gid, uid, prestige):
        with self._connect() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO PRESTIGECOUNTER (GID, UID, PRESTIGE) VALUES (?, ?, ?)",
                (gid, uid, prestige),
            )

    def _get_prestige(self, gid, uid):
        try:
            r = self._connect().execute("SELECT PRESTIGE FROM PRESTIGECOUNTER WHERE GID=? AND UID=?",
                                        (gid, uid)).fetchone()
            if r is None:
                score_counter = ScoreCounter2()
                score_counter._set_prestige(gid, uid, 0)
                return 0
            return r[0]
        except Exception as e:
            raise Exception('错误:\n' + str(e))
            return 0

    def _add_prestige(self, gid, uid, num):
        prestige = self._get_prestige(gid, uid)
        prestige += num
        with self._connect() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO PRESTIGECOUNTER (GID, UID, PRESTIGE) VALUES (?, ?, ?)",
                (gid, uid, prestige),
            )

    def _reduce_prestige(self, gid, uid, num):
        prestige = self._get_prestige(gid, uid)
        prestige -= num
        with self._connect() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO PRESTIGECOUNTER (GID, UID, PRESTIGE) VALUES (?, ?, ?)",
                (gid, uid, prestige),
            )
