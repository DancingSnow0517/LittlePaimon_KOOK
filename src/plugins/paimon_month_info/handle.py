import logging

from .draw import draw_monthinfo_card
from ...database.models.player_info import Player
from ...utils.genshin_api import get_mihoyo_private_data

log = logging.getLogger(__name__)


async def handle_myzj(player: Player, month: str):
    data = await get_mihoyo_private_data(player.uid, player.user_id, 'month_info', month=month)
    if isinstance(data, str):
        log.info(f'原神每月札记: ➤ 用户 {player.user_id}, UID {player.uid} 获取数据失败, {data}')
        return f'{player.uid}{data}'
    elif data['retcode'] != 0:
        log.info(
            f'原神每月札记: ➤ 用户 {player.user_id}, UID {player.uid}, 获取数据失败，code为 {data["retcode"]}， msg为 {data["message"]}')

        return f'{player.uid}获取数据失败，msg为{data["message"]}\n'
    else:
        log.info(f'原神每月札记: ➤ 用户 {player.user_id}, UID {player.uid} 获取数据成功')

        try:
            img = await draw_monthinfo_card(data['data'])
            log.info(f'原神每月札记: ➤➤ 用户 {player.user_id}, UID {player.uid} 绘制图片成功')

            return img
        except Exception as e:
            log.info(f'原神每月札记: ➤➤ 用户 {player.user_id}, UID {player.uid} 绘制图片失败，{e}')

            return f'{player.uid}绘制图片失败，{e}\n'
