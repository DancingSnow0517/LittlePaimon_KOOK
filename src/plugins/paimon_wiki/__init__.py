import time
from typing import TYPE_CHECKING, Dict, List

from khl import Message, MessageTypes
from khl_card import Card, ThemeTypes, CardMessage
from khl_card.accessory import Image, Kmarkdown
from khl_card.modules import Container, Section

from .draw_daily_material import get_daily_material, draw_material
from .draw_map import init_map, draw_map, get_full_map
from src.utils.path import RESOURCE_BASE_PATH
from ...utils.alias import get_match_alias

if TYPE_CHECKING:
    from ...bot import LittlePaimon

days_cn = {
    '1': '周一',
    '2': '周二',
    '3': '周三',
    '4': '周四',
    '5': '周五',
    '6': '周六',
}


class WaitInfo:
    match_alias: List[str]
    type: str
    img_url: str

    def __init__(self, **kwargs) -> None:
        self.match_alias = kwargs.get('match_alias', [])
        self.type = kwargs.get('type', '')
        self.img_url = kwargs.get('img_url', '')


wait_to_match: Dict[str, WaitInfo] = {}


async def on_startup(bot: 'LittlePaimon'):
    # noinspection PyShadowingBuiltins
    @bot.command_info('查看某日开放材料刷取的角色和武器', '<今天|周几>材料')
    @bot.command('daily_material',
                 regex=r'^(?P<day>周[一二三四五六日]|[今明后]天|[今明后]日|现在)(?P<type>天赋|武器|角色|)材料$')
    async def daily_material(msg: Message, r_day: str, r_type: str):
        if r_day in ['今日', '今天', '现在']:
            day = time.strftime("%w")
        elif r_day in ['明日', '明天']:
            day = str(int(time.strftime("%w")) + 1)
        elif r_day in ['后日', '后天']:
            day = str(int(time.strftime("%w")) + 2)
        elif r_day == '周日':
            await msg.reply('周日所有材料都可以刷哦!')
            return
        else:
            day = '0'
        if day == '0':
            await msg.reply('周日所有材料都可以刷哦!')
        else:
            img = await draw_material(days_cn[day])
            img.save('Temp/daily_material.png')
            await msg.reply(await bot.client.create_asset('Temp/daily_material.png'), type=MessageTypes.IMG)

    @bot.command_info('查看某个材料的介绍和采集点。', '!!材料图鉴 <材料名> [地图]')
    @bot.my_command('material_map', aliases=['材料图鉴'])
    async def material_map(msg: Message, material: str = None, genshin_map: str = None):
        if genshin_map is None:
            genshin_map = '提瓦特'
        elif genshin_map not in {'提瓦特', '层岩巨渊', '渊下宫'}:
            await msg.reply('地图名称有误，请在【提瓦特、层岩巨渊、渊下宫】中选择')
            return
        if (file_path := RESOURCE_BASE_PATH / 'genshin_map' / 'results' / f'{genshin_map}_{material}.png').exists():
            url = await bot.client.create_asset(file_path)
            await msg.reply(url, type=MessageTypes.IMG)
        else:
            await msg.ctx.channel.send(f'开始查找 **{material}** 的资源点，请稍候...')
            result = await draw_map(material, genshin_map)
            if isinstance(result, CardMessage):
                await msg.reply(result.build())
            else:
                url = await bot.client.create_asset(result)
                await msg.reply(url, type=MessageTypes.IMG)

    @bot.command_info('查看多个材料大地图采集点。', '!!材料地图 <材料名列表>\n示例：!!材料地图 鸣草 鬼兜虫')
    @bot.my_command('material_map_full', aliases=['材料地图'])
    async def material_map_full(msg: Message, *material: str):
        if len(material) == 0:
            await msg.reply('请给要查询的材料给小派蒙哦~')
        if len(material) > 3:
            material = material[:3]
        else:
            await msg.reply(f'开始查找{"、".join(material)}的资源点，请稍候...')
            result = await get_full_map(list(material), '提瓦特')
            if isinstance(result, CardMessage):
                await msg.reply(result.build())
            else:
                result.save('Temp/material_map_full.png')
                url = await bot.client.create_asset('Temp/material_map_full.png')
                await msg.reply(url, type=MessageTypes.IMG)

    @bot.command('match', regex=r'^(?P<index>\d+)$')
    async def match(msg: Message, index: int):
        if msg.author.id in wait_to_match:
            if index > len(wait_to_match[msg.author.id].match_alias) or index <= 0:
                await msg.reply('这不是个正确的选项')
            else:
                name = wait_to_match[msg.author.id].match_alias[index - 1]
                try:
                    await msg.reply([Card(
                        Container(Image(wait_to_match[msg.author.id].img_url.format(name))),
                        theme=ThemeTypes.NONE
                    ).build()])
                except Exception as e:
                    print(e)
                    await msg.reply(f'没有找到{name}的图鉴')
                finally:
                    del wait_to_match[msg.author.id]

    def create_wiki_matcher(pattern: str, help_fun: str, help_name: str):
        # noinspection PyShadowingBuiltins
        @bot.command_info(f'查看该{help_name}的{help_fun}', usage=f'<{help_name}名> {help_fun}')
        @bot.command(help_fun, regex=pattern)
        async def _(msg: Message, r_name1: str = None, r_type: str = '角色', r_name2: str = None):
            name = r_name1 or r_name2
            if '武器' in r_type:
                type = '武器'
                img_url = 'https://static.cherishmoon.fun/LittlePaimon/WeaponMaps/{}.jpg'
            elif '圣遗物' in r_type:
                type = '圣遗物'
                img_url = 'https://static.cherishmoon.fun/LittlePaimon/ArtifactMaps/{}.jpg'
            elif '怪物' in r_type or '原魔' in r_type:
                type = '原魔'
                img_url = 'https://static.cherishmoon.fun/LittlePaimon/MonsterMaps/{}.jpg'
            elif r_type == '角色攻略':
                type = '角色'
                img_url = 'https://static.cherishmoon.fun/LittlePaimon/XFGuide/{}.jpg'
            elif r_type == '角色材料':
                type = '角色'
                img_url = 'https://static.cherishmoon.fun/LittlePaimon/RoleMaterials/{}.jpg'
            elif r_type == '收益曲线':
                type = '角色'
                img_url = 'https://static.cherishmoon.fun/LittlePaimon/blue/{}.jpg'
            elif r_type == '参考面板':
                type = '角色'
                img_url = 'https://static.cherishmoon.fun/LittlePaimon/blueRefer/{}.jpg'
            else:
                return
            match_alias = get_match_alias(name, type)
            true_name = match_alias[0] if (
                    isinstance(match_alias, list) and len(match_alias) == 1) else match_alias if isinstance(
                match_alias, str) else None
            if true_name:
                try:
                    await msg.reply([Card(
                        Container(Image(img_url.format(true_name))),
                        theme=ThemeTypes.NONE
                    ).build()])
                except:
                    await msg.reply(f'没有找到{name}的图鉴')
            elif match_alias:
                print(match_alias)
                if isinstance(match_alias, dict):
                    match_alias = list(match_alias.keys())
                await msg.reply([Card(
                    Section(Kmarkdown('请 **准确的** 告诉小派蒙要查询的 **名字** 哦~\n你可能想要查询的:')),
                    *[Section(Kmarkdown(f'{match_alias.index(n) + 1}、`{n}`')) for n in match_alias],
                    Section(Kmarkdown('请回答小派蒙对应的数字'))
                ).build()])
                wait_to_match[msg.author.id] = WaitInfo(match_alias=match_alias, type=type, img_url=img_url)
            else:
                await msg.reply(f'没有找到{name}的图鉴')

    create_wiki_matcher(r'(?P<name1>\w*)(?P<type>(?:原魔|怪物)(?:图鉴|攻略))(?P<name2>\w*)', '原魔图鉴', '原魔')
    create_wiki_matcher(r'(?P<name1>\w*)(?P<type>武器(?:图鉴|攻略))(?P<name2>\w*)', '武器图鉴', '武器')
    create_wiki_matcher(r'(?P<name1>\w*)(?P<type>圣遗物(?:图鉴|攻略))(?P<name2>\w*)', '圣遗物图鉴', '圣遗物')
    create_wiki_matcher(r'(?P<name1>\w*)(?P<type>角色攻略)(?P<name2>\w*)', '角色攻略', '角色')
    create_wiki_matcher(r'(?P<name1>\w*)(?P<type>角色材料)(?P<name2>\w*)', '角色材料', '角色')
    create_wiki_matcher(r'(?P<name1>\w*)(?P<type>收益曲线)(?P<name2>\w*)', '收益曲线', '角色')
    create_wiki_matcher(r'(?P<name1>\w*)(?P<type>参考面板)(?P<name2>\w*)', '参考面板', '角色')

    bot.task.add_cron(hour=7, timezone='Asia/Shanghai')(get_daily_material)
