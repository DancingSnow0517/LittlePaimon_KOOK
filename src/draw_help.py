import math

from .api.command import CommandInfoManager
from .api.interface import CommandGroups
from .utils.files import load_image
from .utils.image_util import PMImage, font_manager as fm
from .utils.path import RESOURCE_BASE_PATH
from .utils.constant import VERSION


def draw_group_card(group: CommandGroups):
    ...


async def draw_help(command_info: CommandInfoManager, group: CommandGroups = None):
    bg = PMImage(await load_image(RESOURCE_BASE_PATH / 'general' / 'bg.png'))
    img = PMImage(size=(1080, 10000), color=(255, 255, 255, 0), mode='RGBA')
    orange_line = await load_image(RESOURCE_BASE_PATH / 'general' / 'orange.png')
    orange_name_bg = await load_image(RESOURCE_BASE_PATH / 'general' / 'orange_card.png')
    black_line = await load_image(RESOURCE_BASE_PATH / 'general' / 'black2.png')
    black_name_bg = await load_image(RESOURCE_BASE_PATH / 'general' / 'black_card2.png')
    orange_bord = await load_image(RESOURCE_BASE_PATH / 'general' / 'orange_bord.png')
    black_bord = await load_image(RESOURCE_BASE_PATH / 'general' / 'black_bord.png')

    img.text('小派蒙帮助', 38, 40, fm.get('SourceHanSerifCN-Bold.otf', 72), 'black')
    img.text(f'V{VERSION}', 1040, 75, fm.get('bahnschrift_regular', 36), 'black', 'right')
    img.text('<>内为必须，[]内为可选', 1040, 105, fm.get('SourceHanSerifCN-Bold.otf', 22), 'black', 'right')

    height_now = 172
    if group is None:
        for g in CommandGroups:
            plugin_line = PMImage(orange_line)
            plugin_name_bg = PMImage(orange_name_bg)
            matcher_card = PMImage(orange_bord)
            name_length = img.text_length(str(g.value), fm.get('SourceHanSerifCN-Bold.otf', 30))
            img.paste(plugin_line, (40, height_now))
            plugin_name_bg.stretch((23, plugin_name_bg.width - 36), int(name_length), 'width')
            img.paste(plugin_name_bg, (40, height_now))
            img.text(str(g.value), 63, height_now + 5, fm.get('SourceHanSerifCN-Bold.otf', 30), 'white')
            height_now += plugin_line.height + 11
            info_list = command_info.get_by_group(g)
            if info_list:
                info_groups = [info_list[i:i + 3] for i in range(0, len(info_list), 3)]
                for info_group in info_groups:
                    max_length = max(len(cmd.desc) for cmd in info_group)
                    max_height = math.ceil(max_length / 16) * 22 + 40
                    matcher_card.stretch((5, matcher_card.height - 5), max_height, 'height')
                    for index, cmd in enumerate(info_group):
                        img.paste(matcher_card, (40 + 336 * index, height_now))
                        img.text(cmd.usage, 40 + 336 * index + 15, height_now + 10, fm.get('SourceHanSansCN-Bold.otf', 24),
                                 'black')
                        img.text_box(cmd.desc.replace('\n', '^'),
                                     (40 + 336 * index + 10, 40 + 336 * index + matcher_card.width - 22),
                                     (height_now + 44, height_now + max_height - 10),
                                     fm.get('SourceHanSansCN-Bold.otf', 18), '#40342d')
                    height_now += max_height + 10 + 6
            height_now += 19
    else:
        plugin_line = PMImage(orange_line)
        plugin_name_bg = PMImage(orange_name_bg)
        matcher_card = PMImage(orange_bord)
        name_length = img.text_length(str(group.value), fm.get('SourceHanSerifCN-Bold.otf', 30))
        img.paste(plugin_line, (40, height_now))
        plugin_name_bg.stretch((23, plugin_name_bg.width - 36), int(name_length), 'width')
        img.paste(plugin_name_bg, (40, height_now))
        img.text(str(group.value), 63, height_now + 5, fm.get('SourceHanSerifCN-Bold.otf', 30), 'white')
        height_now += plugin_line.height + 11
        info_list = command_info.get_by_group(group)
        if info_list:
            info_groups = [info_list[i:i+3] for i in range(0, len(info_list), 3)]
            for info_group in info_groups:
                max_length = max(len(cmd.desc) for cmd in info_group)
                max_height = math.ceil(max_length / 16) * 22 + 40
                matcher_card.stretch((5, matcher_card.height - 5), max_height, 'height')
                for index, cmd in enumerate(info_group):
                    img.paste(matcher_card, (40 + 336 * index, height_now))
                    img.text(cmd.usage, 40 + 336 * index + 15, height_now + 10, fm.get('SourceHanSansCN-Bold.otf', 24),
                             'black')
                    img.text_box(cmd.desc.replace('\n', '^'),
                                 (40 + 336 * index + 10, 40 + 336 * index + matcher_card.width - 22),
                                 (height_now + 44, height_now + max_height - 10),
                                 fm.get('SourceHanSansCN-Bold.otf', 18), '#40342d')
                height_now += max_height + 10 + 6
        height_now += 19
    img.text('CREATED BY LITTLEPAIMON', (0, 1080), height_now + 8, fm.get('SourceHanSerifCN-Bold.otf', 24), 'black',
             'center')
    height_now += 70
    bg.stretch((50, bg.height - 50), height_now - 100, 'height')
    bg.paste(img, (0, 0))

    return bg
