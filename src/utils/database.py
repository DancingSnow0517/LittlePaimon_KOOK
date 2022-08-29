import logging
import sqlite3

from typing import Optional, List

connection: Optional[sqlite3.Connection] = None

log = logging.getLogger(__name__)


class CookieInfo:
    guild_id: str
    user_id: str
    uid: str
    cookie: str

    def __init__(self, guild_id: str, user_id: str, uid: str, cookie: str) -> None:
        self.guild_id = guild_id
        self.user_id = user_id
        self.uid = uid
        self.cookie = cookie

    def __repr__(self) -> str:
        return f'CookieInfo(guild_id={self.guild_id}, user_id={self.user_id}, uid={self.uid}, cookie={self.cookie})'


def init():
    """
    初始化数据库数据
    """
    _check_connection()
    log.info('正在初始化数据库...')

    init_cookie = '''CREATE TABLE if not exists cookie(
    guild_id TEXT,
    user_id TEXT,
    uid TEXT,
    cookie TEXT
    )'''

    cur = connection.cursor()
    cur.execute(init_cookie).close()
    cur.close()

    log.info('数据库初始化完成。')


def get_cookies() -> List[CookieInfo]:
    """
    获取数据库的所有 cookie 信息
    :return: 一个 CookieInfo 的列表
    """
    _check_connection()
    cur = connection.cursor()
    data = cur.execute('SELECT * FROM cookie').fetchall()
    cur.close()
    return [CookieInfo(*info) for info in data]


def add_cookie(guild_id, user_id, uid, cookie) -> bool:
    """

    :param guild_id: 服务器id
    :param user_id: 用户id
    :param uid: 原神id
    :param cookie: 米游社cookie
    :return: bool，表示操作是否成功
    """
    _check_connection()
    cur = connection.cursor()
    count = cur.execute(f"SELECT count(*) FROM cookie WHERE uid={uid}").fetchone()[0]
    if count == 0:
        cur.execute(f"INSERT INTO cookie (guild_id, user_id, uid, cookie)"
                    f"VALUES ({guild_id}, {user_id}, {uid}, {cookie})")
        connection.commit()
        log.info(f'{user_id} 的 cookie 添加成功')
        return True
    else:
        log.info(f'uid: {uid} 已存在')
        return False


def _connect() -> sqlite3.Connection:
    log.info('正在连接数据库...')
    return sqlite3.connect('little_paimon.db')


def _disconnect():
    if connection is None:
        log.error('数据库没有连接')
    else:
        connection.close()


def _check_connection():
    global connection
    if connection is None:
        connection = _connect()
