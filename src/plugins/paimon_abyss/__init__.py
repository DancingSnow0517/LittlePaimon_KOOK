import logging
import traceback
from typing import TYPE_CHECKING

from khl import Message, MessageTypes

from .draw_abyss_card import draw_abyss_card
from .abyss_statistics import get_statistics
from .youchuang import draw_team
from ...api.interface import CommandGroups
from ...database.models.cookie import PrivateCookie
from ...utils.genshin import GenshinInfoManager

if TYPE_CHECKING:
    from ...bot import LittlePaimon

log = logging.getLogger(__name__)


async def on_startup(bot: 'LittlePaimon'):
    @bot.command_info('查看 本期|上期 的深渊战报\n1: 这期深渊 2: 上期深渊', '!!深渊信息 [1|2] [UID]', [CommandGroups.ABYSS])
    @bot.my_command('sy', aliases=['深渊战报', '深渊信息'])
    async def sy(msg: Message, abyss_index: int = 1, uid: str = None):
        log.info('原神深渊战报: 开始执行')
        abyss_index = abyss_index if abyss_index == 1 or abyss_index == 2 else 1
        if uid is None:
            cookies = await PrivateCookie.filter(user_id=msg.author.id)
            if len(cookies) == 0:
                await msg.reply('你还没有绑定 cookie')
                return
        else:
            cookies = await PrivateCookie.filter(uid=uid)
            if len(cookies) == 0:
                await msg.reply(f'数据库没有查询到 uid 的信息')
                return
            for ck in cookies:
                if ck.user_id != msg.author.id:
                    await msg.reply(f'UID: {ck.uid} 不属于你')
                    cookies.remove(ck)
        for ck in cookies:
            log.info(f'原神深渊战报: ➤用户: {ck.user_id}, UID: {ck.uid}')
            gim = GenshinInfoManager(ck.user_id, ck.uid)
            abyss_info = await gim.get_abyss_info(abyss_index)
            if isinstance(abyss_info, str):
                log.info(f'原神深渊战报: ➤➤ {abyss_info}')
                await msg.reply(abyss_info)
            else:
                log.info('原神深渊战报: ➤➤ 数据获取成功')
                try:
                    img = await draw_abyss_card(abyss_info)
                    log.info('原神深渊战报: ➤➤➤ 制图完成')
                    img.save('Temp/sy.png')
                    url = await bot.client.create_asset('Temp/sy.png')
                    await msg.reply(url, type=MessageTypes.IMG)
                except Exception as e:
                    traceback.print_exc()
                    log.error(f'原神深渊战报: ➤➤➤ 制图出错: {e}')

    @bot.command_info('查看本群深渊统计，仅群可用', '!!深渊统计', [CommandGroups.ABYSS])
    @bot.my_command('abyss_stat', aliases=['深渊统计', '深渊群数据', '深渊群排行'])
    async def abyss_stat(msg: Message):
        try:
            result = await get_statistics(msg.ctx.guild.id, bot)
            if isinstance(result, str):
                await msg.reply(result)
                return
            result.save('Temp/abyss_stat.png')
            url = await bot.client.create_asset('Temp/abyss_stat.png')
            await msg.reply(url, type=MessageTypes.IMG)
        except Exception as e:
            traceback.print_exc()
            await msg.reply(f'制作深渊统计时出错：{e}')

    @bot.command_info('查看深渊配队推荐，数据来源于游创工坊', '!!深渊配队', [CommandGroups.ABYSS])
    @bot.my_command('abyss_team', aliases=['深渊配队', '配队推荐', '深渊阵容'])
    async def abyss_team(msg: Message):
        try:
            result = await draw_team(msg.author.id)
            result.save('Temp/abyss_team.png')
            url = await bot.client.create_asset('Temp/abyss_team.png')
            await msg.reply(url, type=MessageTypes.IMG)
        except Exception as e:
            traceback.print_exc()
            await msg.reply(f'制作深渊配队时出错：{e}')
