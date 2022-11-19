import logging
import random
import traceback
from typing import TYPE_CHECKING, Tuple, List

from khl import Message, MessageTypes
from khl_card import Card, ThemeTypes
from khl_card.accessory import Image
from khl_card.modules import Container

from .draw_character_bag import draw_chara_bag
from .draw_character_card import draw_chara_card
from .draw_character_detail import draw_chara_detail
from .draw_player_card import draw_player_card
from ...api.interface import CommandGroups
from ...database.models.cookie import PrivateCookie
from ...database.models.player_info import Player
from ...utils import requests
from ...utils.alias import get_match_alias
from ...utils.genshin import GenshinInfoManager
from ...utils.types import MALE_CHARACTERS, BOY_CHARACTERS, GIRL_CHARACTERS, LOLI_CHARACTERS, FEMALE_CHARACTERS

if TYPE_CHECKING:
    from ...bot import LittlePaimon

log = logging.getLogger(__name__)

running_ysa = []


async def on_startup(bot: 'LittlePaimon'):
    @bot.command_info('查看原神个人信息卡片', '!!原神卡片 [UID]', [CommandGroups.INFO])
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

    @bot.command_info('查看角色背包及练度排行', '!!角色背包 [UID]', [CommandGroups.INFO])
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

    @bot.command_info('随机角色同人图+角色信息卡片', '!!角色图 <角色名>', [CommandGroups.INFO])
    @bot.my_command('ysc', aliases=['角色图', '角色卡片'])
    async def ysc(msg: Message, *characters: str):
        log.info('原神角色卡片: 开始执行')
        chars = get_characters(characters)
        if not chars:
            await msg.reply(f'没有找到叫 {characters} 的角色')
            return
        cookies = await PrivateCookie.filter(user_id=msg.author.id)
        if len(cookies) == 0:
            await msg.reply('你还没有绑定 cookie')
            return
        urls = []
        if len(cookies) == 1:
            # 当查询对象只有一个时，查询所有角色
            gim = GenshinInfoManager(cookies[0].user_id, cookies[0].uid)
            await gim.set_last_query()
            log.info(f'原神角色卡片: ➤用户: {cookies[0].user_id}, UID: {cookies[0].uid}')
            for char in chars:
                char_info = await gim.get_character(name=char)
                if char_info is None:
                    log.info(f'原神角色卡片: ➤➤ 角色: {char} 没有该角色信息，发送随机图')
                    (await requests.get_img(f'http://img.genshin.cherishmoon.fun/{char}')).save('Temp/ysc.png')
                    urls.append(await bot.client.create_asset('Temp/ysc.png'))
                else:
                    img = await draw_chara_card(char_info)
                    img.save('Temp/ysc.png')
                    urls.append(await bot.client.create_asset('Temp/ysc.png'))
                    log.info(f'原神角色卡片: ➤➤ 角色: {char} 制图完成')
        else:
            # 当查询对象有多个时，只查询第一个角色
            for ck in cookies:
                gim = GenshinInfoManager(ck.user_id, ck.uid)
                await gim.set_last_query()
                log.info(f'原神角色卡片: ➤用户: {ck.user_id}, UID: {ck.uid}')
                char_info = await gim.get_character(name=chars[0])
                if char_info is None:
                    log.info(f'原神角色卡片: ➤➤ 角色: {chars[0]} 没有该角色信息，发送随机图')
                    (await requests.get_img(f'http://img.genshin.cherishmoon.fun/{chars[0]}')).save('Temp/ysc.png')
                    urls.append(await bot.client.create_asset('Temp/ysc.png'))
                else:
                    img = await draw_chara_card(char_info)
                    img.save('Temp/ysc.png')
                    urls.append(await bot.client.create_asset('Temp/ysc.png'))
                    log.info(f'原神角色卡片: ➤➤ 角色: {chars[0]} 制图完成')

        if urls:
            card = Card(
                Container(
                    *[Image(url) for url in urls]
                ),
                theme=ThemeTypes.NONE
            )
            await msg.reply([card.build()])

    @bot.command_info('查看指定角色的详细面板数据及伤害计算', '!!角色详情 <角色名>', [CommandGroups.INFO])
    @bot.my_command('ysd', aliases=['角色详情', '角色信息', '角色面板'])
    async def ysd(msg: Message, *characters: str):
        log.info('原神角色面板: 开始执行')
        chars = get_characters(characters)
        if not chars:
            await msg.reply(f'没有找到叫 {characters} 的角色')
            return
        cookies = await PrivateCookie.filter(user_id=msg.author.id)
        if len(cookies) == 0:
            await msg.reply('你还没有绑定 cookie')
            return
        urls = []
        if len(cookies) == 1:
            # 当查询对象只有一个时，查询所有角色
            gim = GenshinInfoManager(cookies[0].user_id, cookies[0].uid)
            await gim.set_last_query()
            log.info(f'原神角色面板: ➤用户: {cookies[0].user_id}, UID: {cookies[0].uid}')
            for char in chars:
                char_info = await gim.get_character(name=char, data_source='enka')
                if not char_info:
                    log.error(f'原神角色面板: ➤➤ 角色: {char} 没有该角色信息')
                    await msg.ctx.channel.send(f'暂无你 {char} 信息，请在游戏内展柜放置该角色')
                else:
                    img = await draw_chara_detail(cookies[0].uid, char_info)
                    img.save('Temp/ysc.png')
                    urls.append(await bot.client.create_asset('Temp/ysc.png'))
                    log.info(f'原神角色面板: ➤➤➤ 制图完成')
        else:
            # 当查询对象有多个时，只查询第一个角色
            for ck in cookies:
                gim = GenshinInfoManager(ck.user_id, ck.uid)
                await gim.set_last_query()
                log.info(f'原神角色面板: ➤用户: {ck.user_id}, UID: {ck.uid}')
                char_info = await gim.get_character(name=chars[0])
                if not char_info:
                    await msg.ctx.channel.send(f'暂无你 {chars[0]} 信息，请在游戏内展柜放置该角色')
                    return
                else:
                    img = await draw_chara_detail(ck.uid, char_info)
                    img.save('Temp/ysc.png')
                    urls.append(await bot.client.create_asset('Temp/ysc.png'))
                    log.info(f'原神角色面板: ➤➤➤ 制图完成')
        if urls:
            card = Card(
                Container(
                    *[Image(url) for url in urls]
                ),
                theme=ThemeTypes.NONE
            )
            await msg.reply([card.build()])


def get_characters(characters: Tuple[str], limit: int = 3) -> List[str]:
    ret = []
    for char in characters:
        if char in ['老婆', '老公', '女儿', '儿子', '爸爸', '妈妈']:
            if char == '老公':
                ret.append(random.choice(MALE_CHARACTERS + BOY_CHARACTERS))
            elif char == '老婆':
                ret.append(random.choice(FEMALE_CHARACTERS + GIRL_CHARACTERS))
            elif char == '女儿':
                ret.append(random.choice(GIRL_CHARACTERS + LOLI_CHARACTERS))
            elif char == '儿子':
                ret.append(random.choice(BOY_CHARACTERS))
            elif char == '爸爸':
                ret.append(random.choice(MALE_CHARACTERS))
            elif char == '妈妈':
                ret.append(random.choice(FEMALE_CHARACTERS))
        elif character_match := get_match_alias(char, '角色', True):
            ret.append(list(character_match.keys())[0])
        if len(ret) > limit:
            return ret[:limit]
        else:
            return ret
