from typing import List

from .api import get_team_rate
from .models import TeamRate
from src.utils.path import RESOURCE_BASE_PATH
from ....database.models.character import Character
from ....database.models.cookie import LastQuery
from ....utils.alias import get_chara_icon
from ....utils.files import load_image
from ....utils.image_util import PMImage, font_manager as fm


async def draw_team_line(up: TeamRate, down: TeamRate, characters: List[str]) -> PMImage:
    img = PMImage(size=(1013, 127), mode='RGBA', color=(0, 0, 0, 0))
    up.formation.sort(key=lambda x: x.star, reverse=True)
    down.formation.sort(key=lambda x: x.star, reverse=True)
    for i, member in enumerate(up.formation):
        owned = (member.name in characters or member.name == '旅行者') if characters else True
        img.paste(await load_image(RESOURCE_BASE_PATH / 'icon' / f'{member.star}starbox.png'), (110 * i, 0))
        img.paste(
            await load_image(RESOURCE_BASE_PATH / 'avatar' / f'{get_chara_icon(name=member.name)}.png',
                             size=(100, 100)),
            (110 * i, 1))
        img.text(member.name if owned else '未拥有', (110 * i, 110 * i + 100), 103, fm.get('hywh', 18), '#33231a',
                       'center')
        if not owned:
            img.paste(await load_image(RESOURCE_BASE_PATH / 'icon' / 'grey_box.png'), (110 * i, 0))
    img.text(f'{round(up.rate * 100, 2)}%', 439, 30, fm.get('bahnschrift_bold', 30), '#33231a')
    for i, member in enumerate(down.formation):
        owned = (member.name in characters or member.name == '旅行者') if characters else True
        img.paste(await load_image(RESOURCE_BASE_PATH / 'icon' / f'{member.star}starbox.png'), (583 + 110 * i, 0))
        img.paste(
            await load_image(RESOURCE_BASE_PATH / 'avatar' / f'{get_chara_icon(name=member.name)}.png',
                             size=(100, 100)),
            (583 + 110 * i, 1))
        img.text(member.name if owned else '未拥有', (583 + 110 * i, 110 * i + 683), 103, fm.get('hywh', 18),
                       '#33231a',
                       'center')
        if not owned:
            img.paste(await load_image(RESOURCE_BASE_PATH / 'icon' / 'grey_box.png'), (583 + 110 * i, 0))
    img.text(f'{round(down.rate * 100, 2)}%', 574, 59, fm.get('bahnschrift_bold', 30), '#33231a', 'right')
    return img


async def draw_team(user_id: str):
    if last_query := await LastQuery.get_or_none(user_id=user_id):
        charas = await Character.filter(user_id=user_id, uid=last_query.uid)
    else:
        charas = await Character.filter(user_id=user_id)
    characters = [chara.name for chara in charas if chara is not None]
    team_data, version = await get_team_rate()
    if characters:
        team_data.sort_by_own(characters)
    img = PMImage(RESOURCE_BASE_PATH / 'abyss' / 'team_bg.png')
    img.text('深境螺旋十二层配队', 36, 29, fm.get('优设标题黑', 72), '#40342d')
    img.paste(await load_image(RESOURCE_BASE_PATH / 'general' / 'bubble.png'), (625, 35))
    img.text(f'{version}版本', (625, 625 + 147), 38, fm.get('SourceHanSansCN-Bold.otf', 30), 'white', 'center')
    img.text('CREATED BY LITTLEPAIMON | DATA FROM YOU-CHUANG',
                   1025, 158, fm.get('bahnschrift_regular.ttf', 30), '#8c4c2e', 'right')

    for i in range(15):
        img.paste(await draw_team_line(team_data.rateListUp[i], team_data.rateListDown[i], characters),
                  (33, 222 + 153 * i))
    return img
