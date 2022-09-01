import logging

from tortoise import Tortoise

from ..config.path import GENSHIN_DB_PATH, GENSHIN_VOICE_DB_PATH

log = logging.getLogger(__name__)

DATA_BASE = {
    "connections": {
        "genshin": {
            "engine": "tortoise.backends.sqlite",
            "credentials": {"file_path": GENSHIN_DB_PATH}
        },
        "genshin_voice": {
            "engine": "tortoise.backends.sqlite",
            "credentials": {"file_path": GENSHIN_VOICE_DB_PATH}
        }
    },
    "apps": {
        "genshin": {
            "models": ["src.database.models.player_info", "src.database.models.abyss_info",
                       "src.database.models.character", "src.database.models.cookie"],
            "default_connection": "genshin"
        },
        "genshin_voice": {
            "models": ["src.database.models.genshin_voice"],
            "default_connection": "genshin_voice"
        }
    }
}


async def connect():
    """"建立数据库连接"""
    try:
        await Tortoise.init(DATA_BASE)
        await Tortoise.generate_schemas()
        log.info('数据库连接成功')
    except Exception as e:
        log.error('数据库连接失败: ', e)
        raise e


async def disconnect():
    """断开数据库连接"""
    await Tortoise.close_connections()
    log.info('数据库连接已断开')
