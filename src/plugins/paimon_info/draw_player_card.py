from typing import Tuple, Optional, List

from src.utils.path import RESOURCE_BASE_PATH
from ...database.models.character import Character, Weapon
from ...database.models.player_info import PlayerWorldInfo, Player, PlayerInfo
from ...utils.alias import get_chara_icon
from ...utils.files import load_image
from ...utils.image_util import PMImage, font_manager as fm
from ...utils import requests

RESOURCES = RESOURCE_BASE_PATH / 'player_card'
ICON = RESOURCE_BASE_PATH / 'icon'
WEAPON = RESOURCE_BASE_PATH / 'weapon'


def get_percent_text(percent: int) -> str:
    if percent < 10:
        return f'0.{percent}%'
    elif percent == 1000:
        return '100%'
    else:
        p = list(str(percent))
        p.insert(-1, '.')
        return ''.join(p) + '%'


async def get_avatar(avatar_url: str, size: Tuple[int, int] = (146, 146)) -> Optional[PMImage]:
    try:
        avatar = await requests.get_img(avatar_url)
        if isinstance(avatar, str):
            return None
        avatar = PMImage(image=avatar)
        avatar.resize(size)
        avatar.to_circle('circle')
        avatar.add_border(6, '#ddcdba', 'circle')
        return avatar
    except Exception:
        return PMImage(size=size, color=(255, 255, 255, 255))


async def draw_weapon_icon(weapon: Weapon, size: Tuple[int, int] = (65, 65)) -> PMImage:
    """绘制武器图标"""
    weapon_bg = PMImage(await load_image(ICON / f'star{weapon.rarity}.png', size=size))
    weapon_icon = await load_image(WEAPON / f'{weapon.icon}.png', size=size)
    weapon_bg.paste(weapon_icon, (0, 0))
    return weapon_bg


async def draw_character_card(info: Character) -> Optional[PMImage]:
    if info is None:
        return None
    # 头像
    avatar = PMImage(await load_image(RESOURCE_BASE_PATH / 'avatar' / f'{get_chara_icon(name=info.name)}.png'))
    avatar.to_circle('circle')
    avatar.resize((122, 122))
    # 背景
    img = PMImage(await load_image(RESOURCES / f'chara_{info.rarity}star.png'))
    img.paste(avatar, (34, 27))
    # 等级
    img.text(f'LV.{info.level}', (0, img.width), 166, fm.get('hywh', 30),
             '#593d99' if info.rarity == 4 else '#964e2e', 'center')
    # 好感度
    img.paste(await load_image(ICON / f'好感度{info.fetter}.png', size=0.6), (147, 118))
    # 命座
    img.paste(await load_image(ICON / f'level_hywh_{len(info.constellation)}.png'), (157, 12))
    # 武器
    weapon = await draw_weapon_icon(info.weapon)
    img.paste(weapon, (15, 215))
    img.text(info.weapon.name[:4], 85, 214, fm.get('hywh', 24), (0, 0, 0, 153))
    img.text(f'Lv{info.weapon.level}', 87, 255, fm.get('hywh', 21),
             '#593d99' if info.weapon.rarity == 4 else '#964e2e')
    text_length = img.text_length(f'Lv{info.weapon.level}', fm.get('hywh', 21))
    img.paste(await load_image(ICON / f'level_hywh_{info.weapon.affix_level}.png'), (92 + int(text_length), 246))
    return img


async def draw_world_card(img: PMImage, info: PlayerWorldInfo):
    if info is None:
        pass
    elif info.name == '蒙德':
        if info.unlock:
            img.draw_ring((225, 225), (89, 1157), 0.08, info.percent / 1000, ['white', (0, 0, 0, 0)])
            img.text(get_percent_text(info.percent), (110, 301), 1387, fm.get('hywh', 24), 'white', 'center')
            img.text(str(info.level) if info.level != 8 else 'Max', 150, 1447, fm.get('hywh', 24), 'white')
        else:
            img.text('未解锁', (110, 301), 1387, fm.get('hywh', 24), 'white', 'center')
    elif info.name == '璃月':
        if info.unlock:
            img.draw_ring((225, 225), (313, 1157), 0.08, info.percent / 1000, ['white', (0, 0, 0, 0)])
            img.text(get_percent_text(info.percent), (334, 525), 1387, fm.get('hywh', 24), 'white', 'center')
            img.text(str(info.level) if info.level != 8 else 'Max', 374, 1447, fm.get('hywh', 24), 'white')
        else:
            img.text('未解锁', (334, 525), 1387, fm.get('hywh', 24), 'white', 'center')
    elif info.name == '稻妻':
        if info.unlock:
            img.draw_ring((225, 225), (537, 1157), 0.08, info.percent / 1000, ['white', (0, 0, 0, 0)])
            img.text(get_percent_text(info.percent), (558, 749), 1387, fm.get('hywh', 24), 'white', 'center')
            img.text(str(info.level) if info.level != 10 else 'Max', 598, 1447, fm.get('hywh', 24), 'white')
            img.text(str(info.tree_level) if info.tree_level != 50 else 'Max', 710, 1447, fm.get('hywh', 24),
                     'white',
                     'right')
        else:
            img.text('未解锁', (558, 749), 1387, fm.get('hywh', 24), 'white', 'center')
    elif info.name == '龙脊雪山':
        if info.unlock:
            img.draw_ring((225, 225), (89, 1494), 0.08, info.percent / 1000, ['white', (0, 0, 0, 0)])
            img.text(get_percent_text(info.percent), (110, 301), 1724, fm.get('hywh', 24), 'white', 'center')
            img.text(str(info.tree_level) if info.tree_level != 12 else 'Max', 150, 1784, fm.get('hywh', 24),
                     'white')
        else:
            img.text('未解锁', (110, 301), 1724, fm.get('hywh', 24), 'white', 'center')
    elif info.name == '层岩巨渊':
        if info.unlock:
            img.text(f'地表{get_percent_text(info.percent)}', (334, 525), 1724, fm.get('hywh', 24), 'white',
                     'center')
            img.text(str(info.stone_level) if info.stone_level != 10 else 'Max', 374, 1784, fm.get('hywh', 24),
                     'white')
        else:
            img.text('地表未解锁', (334, 525), 1724, fm.get('hywh', 24), 'white',
                     'center')
    elif info.name == '层岩巨渊·地下矿区':
        if info.unlock:
            img.draw_ring((225, 225), (313, 1494), 0.08, info.percent / 1000, ['white', (0, 0, 0, 0)])
            img.text(f'地下{get_percent_text(info.percent)}', (334, 525), 1751, fm.get('hywh', 24), 'white',
                     'center')
        else:
            img.text('地下未解锁', (334, 525), 1751, fm.get('hywh', 24), 'white',
                     'center')
    elif info.name == '渊下宫':
        if info.unlock:
            img.draw_ring((225, 225), (537, 1494), 0.08, info.percent / 1000, ['white', (0, 0, 0, 0)])
            img.text(get_percent_text(info.percent), (558, 749), 1724, fm.get('hywh', 24), 'white', 'center')
        else:
            img.text('未解锁', (558, 749), 1724, fm.get('hywh', 24), 'white', 'center')
    elif info.name == '须弥':
        if info.unlock:
            img.draw_ring((225, 225), (761, 1157), 0.08, info.percent / 1000, ['white', (0, 0, 0, 0)])
            img.text(get_percent_text(info.percent), (782, 973), 1387, fm.get('hywh', 24), 'white', 'center')
            img.text(str(info.level) if info.level != 10 else 'Max', 826, 1447, fm.get('hywh', 24), 'white')
            img.text(str(info.tree_level) if info.tree_level != 50 else 'Max', 938, 1447, fm.get('hywh', 24),
                     'white',
                     'right')
        else:
            img.text('未解锁', (782, 973), 1387, fm.get('hywh', 24), 'white', 'center')


async def draw_player_card(player: Player, info: PlayerInfo, characters: List[Character], avatar_url: str):
    img = PMImage(await load_image(RESOURCES / 'bg.png'))
    # 头像
    avatar = await get_avatar(avatar_url)
    if avatar:
        img.paste(avatar, (47, 52))
    # 昵称
    img.text(info.nickname, 221, 70, fm.get('hywh', 64), '#ddcdba')
    # 签名和uid
    if info.signature:
        img.text(info.signature, 223, 150, fm.get('hywh', 48), '#ddcdba')
        nickname_length = img.text_length(info.nickname, fm.get('hywh', 64))
        img.text(f'UID{player.uid}', 223 + nickname_length + 29, 90, fm.get('hywh', 48), '#ddcdba')
    else:
        img.text(f'UID{player.uid}', 223, 150, fm.get('hywh', 48), '#ddcdba')

    # 数据
    base_data = [info.level, info.base_info.activate_days, info.base_info.character_num, info.base_info.achievements,
                 info.base_info.abyss_floor, info.base_info.luxurious_chest,
                 info.base_info.precious_chest, info.base_info.exquisite_chest, info.base_info.common_chest,
                 info.base_info.magic_chest, info.base_info.anemoculus,
                 info.base_info.geoculus, info.base_info.electroculus, info.base_info.dendroculus]
    for i in range(len(base_data)):
        img.text(str(base_data[i]), (143 + 174 * (i % 5), 239 + 174 * (i % 5)), 312 + 119 * (i // 5),
                 fm.get('hywh', 48), 'black', 'center')

    # 尘歌壶
    home_data = [info.home.level, info.home.comfort_value, info.home.item_num, info.home.visit_num]
    for i in range(len(home_data)):
        img.text(str(home_data[i]), (155 + 225 * (i % 4), 252 + 225 * (i % 4)), 961, fm.get('hywh', 48), 'black',
                 'center')
    home_name = {'罗浮洞': 168, '翠黛峰': 336, '清琼岛': 505, '绘绮庭': 673, '妙香林': 841}
    for name in home_name:
        img.text(name if name in info.home.unlock else '未解锁', home_name[name], 923, fm.get('hywh', 24),
                 (0, 0, 0, 153), 'center')

    # 世界探索
    for w in info.world_explore.list():
        await draw_world_card(img, w)
    # 角色
    for i in range(len(characters)):
        img.paste(await draw_character_card(characters[i]), (112 + 222 * (i % 4), 1959 + 341 * (i // 4)))

    return img
