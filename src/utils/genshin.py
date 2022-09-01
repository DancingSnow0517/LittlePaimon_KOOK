import json
import logging

from .alias import get_name_by_id
from .genshin_api import get_enka_data

log = logging.getLogger(__name__)


async def update_from_enka(user_id: str, uid: str) -> str:
    """
    从enka.network更新原神数据
    :return: 更新结果
    """
    data = await get_enka_data(uid)
    print(json.dumps(data, indent=4, ensure_ascii=False))
    if not data:
        log.info(f'无法获取到 {uid} 的数据，可能是 Enka.Network 接口服务出现问题')
        return '无法从Enka.Network获取该uid的信息，可能是接口服务出现问题，请稍候再试'
    if 'avatarInfoList' not in data:
        return '未在游戏中打开角色展柜，请打开后3分钟后再试'
    for character in data['avatarInfoList']:
        ...
    log.info(f'➤UID {uid} 更新Enka成功')
    return '更新成功，本次更新的角色有：\n' + ' '.join(
        [get_name_by_id(str(c['avatarId'])) for c in data['playerInfo']['showAvatarInfoList']])
