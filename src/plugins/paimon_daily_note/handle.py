import logging

from .draw import draw_daily_note_card
from ...database.models.player_info import Player
from ...utils.genshin_api import get_mihoyo_private_data

log = logging.getLogger(__name__)


async def handle_ssbq(player: Player):
    data = await get_mihoyo_private_data(player.uid, player.user_id, 'daily_note')
    if isinstance(data, str):
        log.info(f'原神实时便签: ➤ 用户 {player.user_id} UID {player.uid} 获取数据失败, {data}')
        return f'{player.uid}{data}\n'
    elif data['retcode'] == 1034:
        log.info(f'原神实时便签: ➤ 用户 {player.user_id} UID {player.uid}, 获取数据失败，状态码为1034，疑似验证码')
        return f'{player.uid}获取数据失败，疑似遇米游社验证码阻拦，请稍后再试\n'
    elif data['retcode'] != 0:
        log.info(
            f'原神实时便签: ➤ 用户 {player.user_id} UID {player.uid}, 获取数据失败，code为 {data["retcode"]}， msg为 {data["message"]}')

        return f'{player.uid}获取数据失败，msg为{data["message"]}\n'
    else:
        log.info(f'原神实时便签: ➤ 用户 {player.user_id} UID {player.uid}, 获取数据成功')

        try:
            img = await draw_daily_note_card(data['data'], player.uid)
            log.info(f'原神实时便签: ➤➤ 用户 {player.user_id} UID {player.uid}, 绘制图片成功')

            return img
        except Exception as e:
            log.info(f'原神实时便签: ➤➤ 用户 {player.user_id} UID {player.uid}, 绘制图片失败，{e}')

            return f'{player.uid}绘制图片失败，{e}\n'
