import time
from typing import TYPE_CHECKING

from khl import Message
from khl_card import Card, ThemeTypes
from khl_card.accessory import Image, Kmarkdown
from khl_card.modules import Container, Section

from ...utils.alias import get_match_alias

if TYPE_CHECKING:
    from ...bot import LittlePaimon


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
        elif r_day in ['周一', '周四']:
            day = '1'
        elif r_day in ['周二', '周五']:
            day = '2'
        elif r_day in ['周三', '周六']:
            day = '3'
        else:
            day = '0'

        if day == '0':
            await msg.reply('周日所有材料都可以刷哦!')
        elif day in ['1', '4']:
            await msg.reply([Card(
                Container(Image('https://static.cherishmoon.fun/LittlePaimon/DailyMaterials/周一周四.jpg')),
                theme=ThemeTypes.NONE
            ).build()])
        elif day in ['2', '5']:
            await msg.reply([Card(
                Container(Image('https://static.cherishmoon.fun/LittlePaimon/DailyMaterials/周二周五.jpg')),
                theme=ThemeTypes.NONE
            ).build()])
        else:
            await msg.reply([Card(
                Container(Image('https://static.cherishmoon.fun/LittlePaimon/DailyMaterials/周三周六.jpg')),
                theme=ThemeTypes.NONE
            ).build()])

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
                        Container(Image(img_url.format(true_name)))
                    ).build()])
                except:
                    await msg.reply(f'没有找到{name}的图鉴')
            elif match_alias:
                print(match_alias)
                if isinstance(match_alias, dict):
                    match_alias = list(match_alias.keys())
                await msg.reply([Card(
                    Section(Kmarkdown('请 **准确的** 告诉小派蒙要查询的 **名字** 哦~\n你可能想要查询的:')),
                    *[Section(Kmarkdown(f'{match_alias.index(n) + 1}、`{n}`')) for n in match_alias]
                ).build()])
            else:
                await msg.reply(f'没有找到{name}的图鉴')

    create_wiki_matcher(r'(?P<name1>\w*)(?P<type>(原魔|怪物)(图鉴|攻略))(?P<name2>\w*)', '原魔图鉴', '原魔')
    create_wiki_matcher(r'(?P<name1>\w*)(?P<type>武器(图鉴|攻略))(?P<name2>\w*)', '武器图鉴', '武器')
    create_wiki_matcher(r'(?P<name1>\w*)(?P<type>圣遗物(图鉴|攻略))(?P<name2>\w*)', '圣遗物图鉴', '圣遗物')
    create_wiki_matcher(r'(?P<name1>\w*)(?P<type>角色攻略)(?P<name2>\w*)', '角色攻略', '角色')
    create_wiki_matcher(r'(?P<name1>\w*)(?P<type>角色材料)(?P<name2>\w*)', '角色材料', '角色')
    create_wiki_matcher(r'(?P<name1>\w*)(?P<type>收益曲线)(?P<name2>\w*)', '收益曲线', '角色')
    create_wiki_matcher(r'(?P<name1>\w*)(?P<type>参考面板)(?P<name2>\w*)', '参考面板', '角色')
