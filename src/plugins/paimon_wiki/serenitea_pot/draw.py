import math
from typing import Optional, Union, Dict

from .api import get_blueprint_data, get_blueprint_material_data
from .models import Item
from ....utils import requests
from ....utils.files import load_image, load_json
from ....utils.image_util import PMImage, font_manager as fm
from ....utils.path import RESOURCE_BASE_PATH

FURNITURE_PATH = RESOURCE_BASE_PATH / 'furniture'
FURNITURE_PATH.mkdir(parents=True, exist_ok=True)

FURNITURE_DATA_PATH = FURNITURE_PATH / 'exist_id.json'

url_data = load_json(FURNITURE_DATA_PATH)  # type: Dict[str, str]

num_color = [('#f6b9c9', '#a90d35'), ('#f2cab9', '#ff6f30'), ('#b9d8f2', '#157eaa'), ('#dedede', '#707070')]


async def draw_item(item: Item, total_num: int):
    # 背景图
    bg = PMImage(RESOURCE_BASE_PATH / 'icon' / f'star{item.level if item.level != 0 else 2}.png')
    bg.resize((180, 180))
    # 摆设图标
    if (path := FURNITURE_PATH / item.icon_url.split('/')[-1]).exists():
        icon = await load_image(path, size=(180, 180))
    else:
        icon = await requests.get_img(item.icon_url, size=(180, 180), save_path=path)
    bg.paste(icon, (0, 0))
    # 摆设名称
    if bg.text_length(item.name, fm.get('hywh', 24)) >= 180:
        c = len(item.name) // 2
        bg.text(item.name[:c], (1, 181), 126, fm.get('hywh', 24), 'black', 'center')
        bg.text(item.name[:c], (0, 180), 125, fm.get('hywh', 24), 'white', 'center')
        bg.text(item.name[c:], (1, 181), 151, fm.get('hywh', 24), 'black', 'center')
        bg.text(item.name[c:], (0, 180), 150, fm.get('hywh', 24), 'white', 'center')
    else:
        bg.text(item.name, (1, 181), 151, fm.get('hywh', 24), 'black', 'center')
        bg.text(item.name, (0, 180), 150, fm.get('hywh', 24), 'white', 'center')
    # 摆设数量
    if item.level == 0:
        color = num_color[3]
    else:
        # 根据占总数量的百分比来决定颜色
        percent = item.num / total_num
        if percent >= 0.2:
            color = num_color[0]
        elif 0.1 <= percent < 0.2:
            color = num_color[1]
        elif 0.05 <= percent <= 0.1:
            color = num_color[2]
        else:
            color = num_color[3]
    num_card_length = 60 if item.num < 100 else 120
    bg.draw_rounded_rectangle2((179 - num_card_length, 1), (num_card_length - 1, 33), 12, color[0], ['ur', 'll'])
    bg.text(str(item.num), (179 - num_card_length, 179), 1, fm.get('bahnschrift_regular', 40, 'Bold'), color[1],
            'center')
    return bg


async def draw_pot_materials(share_code: int, user_id: Optional[str] = None) -> Union[str, PMImage]:
    save_path = FURNITURE_PATH / f'摹本{share_code}.png'
    if str(share_code) in url_data:
        return url_data[str(share_code)]
    items, cookie = await get_blueprint_data(share_code, user_id)
    material_items = await get_blueprint_material_data(items, cookie)
    if items is None:
        return '没有能够查询尘歌壶摹本的Cookie，请联系超管添加~'
    elif isinstance(items, str):
        return items
    img = PMImage(RESOURCE_BASE_PATH / 'general' / 'bg.png')
    row = math.ceil(len(items) / 5)
    if isinstance(material_items, list):
        row += math.ceil(len(material_items) / 5)
    img.stretch((210, 1890), 205 * row + (120 if isinstance(material_items, list) else 0) - 30, 'height')
    # 标题
    img.text('尘歌壶摹本材料', 36, 29, fm.get('优设标题黑', 72), '#40342d')
    bubble = PMImage(await load_image(RESOURCE_BASE_PATH / 'general' / 'bubble.png'))
    code_length = img.text_length(f'摹数{share_code}', fm.get('SourceHanSansCN-Bold.otf', 30))
    bubble.stretch((15, int(bubble.width) - 15), code_length, 'width')
    img.paste(bubble, (500, 38))
    img.text(f'摹数{share_code}', 513, 41, fm.get('SourceHanSansCN-Bold.otf', 30), 'white')
    # 摆设提示线
    item_line = await load_image(RESOURCE_BASE_PATH / 'general' / 'line.png')
    img.paste(item_line, (40, 144))
    img.text('摆设一览', 63, 156, fm.get('SourceHanSansCN-Bold.otf', 30), 'white')
    # logo和生成时间
    img.text(f'CREATED BY LITTLEPAIMON', 1025, 158, fm.get('bahnschrift_regular.ttf', 30), '#8c4c2e', 'right')
    total_num = sum(item.num for item in items)
    # 摆设一览
    for i, item in enumerate(items):
        img.paste(await draw_item(item, total_num), (40 + 205 * (i % 5), 230 + 205 * (i // 5)))

    if isinstance(material_items, list):
        now_height = 240 + 205 * math.ceil(len(items) / 5)
        # 材料提示线
        img.paste(item_line, (40, now_height))
        img.text('材料一览', 63, now_height + 12, fm.get('SourceHanSansCN-Bold.otf', 30), 'white')
        # 材料一览
        for i, item in enumerate(material_items):
            img.paste(await draw_item(item, total_num), (40 + 205 * (i % 5), now_height + 80 + 205 * (i // 5)))
    img.save(save_path, mode='RGB', quality=85)
    return img
