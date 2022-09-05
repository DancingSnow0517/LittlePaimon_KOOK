import logging
import traceback
from typing import TYPE_CHECKING

from khl import Message, MessageTypes

from .draw_abyss_card import draw_abyss_card
from .draw_character_bag import draw_chara_bag
from .draw_player_card import draw_player_card
from ...database.models.cookie import PrivateCookie
from ...database.models.player_info import Player
from ...utils.genshin import GenshinInfoManager

if TYPE_CHECKING:
    from ...bot import LittlePaimon

log = logging.getLogger(__name__)

running_ysa = []


async def on_startup(bot: 'LittlePaimon'):
    @bot.my_command('ys', aliases=['原神卡片', '个人卡片'])
    async def ys(msg: Message, uid: str = None):
        log.info('原神信息查询: 开始执行')
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
            log.info(f'原神信息查询: ➤用户: {ck.user_id}, UID: {ck.uid}')
            gim = GenshinInfoManager(ck.user_id, ck.uid)
            player_info, characters_list = await gim.get_player_info()
            if isinstance(player_info, str):
                log.info(f'原神信息查询: ➤➤ {player_info}')
                await msg.reply(player_info)
            else:
                log.info(f'原神信息查询: ➤➤ 数据获取成功')
                try:
                    img = await draw_player_card(Player(user_id=ck.user_id, uid=ck.uid), player_info, characters_list,
                                                 msg.author.avatar)
                    log.info('原神信息查询: ➤➤➤ 制图完成')
                    img.save('Temp/ys.png')
                    url = await bot.client.create_asset('Temp/ys.png')
                    await msg.reply(url, type=MessageTypes.IMG)
                except Exception as e:
                    traceback.print_exc()
                    log.error(f'原神信息查询: ➤➤➤ 制图出错: {e}')

    @bot.my_command('ysa', aliases=['角色背包', '练度统计'])
    async def ysa(msg: Message, uid: str = None):
        log.info('原神角色背包: 开始执行')
        await msg.ctx.channel.send('开始绘制角色背包卡片，请稍等...')
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
            if f'{ck.user_id}-{ck.uid}' in running_ysa:
                await msg.reply(f'UID{ck.uid} 正在绘制角色背包，请勿重复发送指令')
                return
            running_ysa.append(f'{ck.user_id}-{ck.uid}')
            log.info(f'原神角色背包: ➤用户: {ck.user_id}, UID: {ck.uid}')
            gim = GenshinInfoManager(ck.user_id, ck.uid)
            player_info, characters_list = await gim.get_chara_bag()
            if isinstance(player_info, str):
                log.info(f'原神角色背包: ➤➤ {player_info}')
                await msg.reply(player_info)
            else:
                log.info('原神角色背包: ➤➤ 数据获取成功')
                try:
                    img = await draw_chara_bag(Player(user_id=ck.user_id, uid=ck.uid), player_info, characters_list,
                                               msg.author.avatar)
                    log.info('原神角色背包: ➤➤➤ 制图完成')
                    img.save('Temp/ysa.png')
                    url = await bot.client.create_asset('Temp/ysa.png')
                    await msg.reply(url, type=MessageTypes.IMG)
                except Exception as e:
                    traceback.print_exc()
                    log.error(f'原神角色背包: ➤➤➤ 制图出错: {e}')

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
