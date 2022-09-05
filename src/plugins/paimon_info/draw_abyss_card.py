import datetime

from ...config.path import RESOURCE_BASE_PATH
from ...database.models.abyss_info import AbyssInfo
from ...utils.files import load_image
from ...utils.image_util import PMImage, font_manager as fm


def datetime_to_cn(time: datetime.datetime) -> str:
    """
    将datetime转换为n月上半|下半
    :param time: 时间
    :return: 中文时间
    """
    time_str = ['零', '一', '二', '三', '四', '五', '六', '七', '八', '九', '十', '十一', '十二']
    if time.day < 16:
        return f'{time_str[time.month]}月上半'
    else:
        return f'{time_str[time.month]}月下半'


async def draw_abyss_card(info: AbyssInfo):
    if not info.total_battle or not info.max_battle:
        return '暂无深渊挑战数据，请稍候再试'
    # 加载图片素材
    img = PMImage(await load_image(RESOURCE_BASE_PATH / 'abyss' / 'bg.png', mode='RGBA'))
    orange_line = await load_image(RESOURCE_BASE_PATH / 'general' / 'line.png')
    # 标题文字
    img.text('深渊战报', 36, 29, fm.get('优设标题黑', 108), '#40342d')
    # 标题时间文字
    bubble = PMImage(await load_image(RESOURCE_BASE_PATH / 'general' / 'bubble.png'))
    time_str = datetime_to_cn(info.start_time)
    time_length = img.text_length(time_str, fm.get('SourceHanSansCN-Bold.otf', 30))
    bubble.stretch((15, int(bubble.width) - 15), time_length, 'width')
    img.paste(bubble, (425, 38))
    img.text(time_str, 438, 41, fm.get('SourceHanSansCN-Bold.otf', 30), 'white')
    # UID和昵称
    if info.nickname:
        img.text(f'UID{info.uid}', 1040, 72, fm.get('bahnschrift_regular.ttf', 36), '#40342d', 'right')
        img.text(info.nickname, 1040, 114, fm.get('SourceHanSansCN-Bold.otf', 30), '#40342d', 'right')
    else:
        img.text(f'UID{info.uid}', 1040, 114, fm.get('bahnschrift_regular.ttf', 36), '#40342d', 'right')
    # 战绩速览标题
    img.paste(orange_line, (40, 164))
    img.text('战绩速览', 63, 176, fm.get('SourceHanSansCN-Bold.otf', 30), 'white')
    # logo和生成时间
    img.text(f'CREATED BY LITTLEPAIMON AT {datetime.datetime.now().strftime("%m-%d %H:%M")}',
             1025, 178, fm.get('bahnschrift_regular.ttf', 30), '#8c4c2e', 'right')

    # 数据栏
    img.paste(await load_image(RESOURCE_BASE_PATH / 'abyss' / 'data_line.png'), (40, 246))
    # 获得总星数
    img.text(f'{info.total_star}/36', (47, 150), 357, fm.get('bahnschrift_regular.ttf', 56), '#40342d', 'center')
    # 战斗次数
    img.text(str(info.total_battle), (209, 312), 357, fm.get('bahnschrift_regular.ttf', 56), '#40342d', 'center')
    # 最多击破
    img.text(str(info.max_defeat.value), (370, 473), 357, fm.get('bahnschrift_regular.ttf', 56), '#40342d',
             'center')
    chara_img = PMImage(await load_image(RESOURCE_BASE_PATH / 'thumb' / f'{info.max_defeat.name}.png', size=(96, 96)))
    chara_img.to_circle('circle')
    img.paste(chara_img, (373, 248))
    # 战技次数
    img.text(str(info.max_normal_skill.value), (532, 635), 357, fm.get('bahnschrift_regular.ttf', 56), '#40342d',
             'center')
    chara_img = PMImage(
        await load_image(RESOURCE_BASE_PATH / 'thumb' / f'{info.max_normal_skill.name}.png', size=(96, 96)))
    chara_img.to_circle('circle')
    img.paste(chara_img, (536, 248))
    # 爆发次数
    img.text(str(info.max_energy_skill.value), (693, 796), 357, fm.get('bahnschrift_regular.ttf', 56), '#40342d',
             'center')
    chara_img = PMImage(
        await load_image(RESOURCE_BASE_PATH / 'thumb' / f'{info.max_energy_skill.name}.png', size=(96, 96)))
    chara_img.to_circle('circle')
    img.paste(chara_img, (696, 248))
    # 最深抵达
    img.text(str(info.max_floor), (838, 1038), 298, fm.get('bahnschrift_regular.ttf', 60), '#40342d', 'center')
    # 最强一击
    circle = await load_image(RESOURCE_BASE_PATH / 'general' / 'orange_circle.png')
    chara_img = PMImage(await load_image(RESOURCE_BASE_PATH / 'thumb' / f'{info.max_damage.name}.png', size=(205, 205)))
    chara_img.to_circle('circle')
    img.text('最强一击', 270, 520, fm.get('SourceHanSansCN-Bold.otf', 48), '#40342d')
    img.text(str(info.max_damage.value), 270, 590, fm.get('bahnschrift_bold.ttf', 72, 'Bold'), '#40342d')
    img.paste(circle, (46, 485))
    img.paste(chara_img, (49, 488))
    # 最多承伤
    chara_img = PMImage(
        await load_image(RESOURCE_BASE_PATH / 'thumb' / f'{info.max_take_damage.name}.png', size=(205, 205)))
    chara_img.to_circle('circle')
    img.text('最多承伤', 791, 520, fm.get('SourceHanSansCN-Bold.otf', 48), '#40342d')
    img.text(str(info.max_take_damage.value), 791, 590, fm.get('bahnschrift_bold.ttf', 72, 'Bold'), '#40342d')
    img.paste(circle, (560, 485))
    img.paste(chara_img, (563, 488))
    # 没有9-12层信息时不会只详细战绩
    if all(info.floors.get(i) is None for i in range(9, 13)):
        return img
    # 详细战绩标题
    img.paste(orange_line, (40, 747))
    img.text('详细战绩', 63, 759, fm.get('SourceHanSansCN-Bold.otf', 30), 'white')
    for i in range(9, 13):
        img.paste(await load_image(RESOURCE_BASE_PATH / 'abyss' / f'floor{i}.png'), (41, 834 + (i - 9) * 194))
        if info.floors.get(i):
            if info.floors[i].stars:
                img.text('-'.join(map(str, info.floors[i].stars)), 91, 960 + (i - 9) * 194,
                         fm.get('bahnschrift_bold.ttf', 30, 'Bold'), 'white')
            if info.floors[i].battles_up:
                up = info.floors[i].battles_up
                down = info.floors[i].battles_down
                j = 0
                for character in up[0]:
                    img.paste(
                        await load_image(RESOURCE_BASE_PATH / 'icon' / f'star{character.rarity}.png', size=(95, 95)),
                        (192 + (j % 4) * 103, 832 + (i - 9) * 194))
                    img.paste(
                        await load_image(RESOURCE_BASE_PATH / 'thumb' / f'{character.name}.png', size=(95, 95)),
                        (192 + (j % 4) * 103, 832 + (i - 9) * 194))
                    img.draw_rounded_rectangle2((192 + (j % 4) * 103, 903 + (i - 9) * 194), (30, 23), 10,
                                                '#333333',
                                                ['ll', 'ur'])
                    img.text(str(character.level), (192 + (j % 4) * 103, 192 + (j % 4) * 103 + 30),
                             906 + (i - 9) * 194,
                             fm.get('bahnschrift_bold.ttf', 20, 'Bold'), 'white', 'center')
                    j += 1
                j = 0
                for character in down[0]:
                    img.paste(
                        await load_image(RESOURCE_BASE_PATH / 'icon' / f'star{character.rarity}.png', size=(95, 95)),
                        (637 + (j % 4) * 103, 832 + (i - 9) * 194))
                    img.paste(
                        await load_image(RESOURCE_BASE_PATH / 'thumb' / f'{character.name}.png', size=(95, 95)),
                        (637 + (j % 4) * 103, 832 + (i - 9) * 194))
                    img.draw_rounded_rectangle2((637 + (j % 4) * 103, 903 + (i - 9) * 194), (30, 23), 10,
                                                '#333333',
                                                ['ll', 'ur'])
                    img.text(str(character.level), (637 + (j % 4) * 103, 637 + (j % 4) * 103 + 30),
                             906 + (i - 9) * 194,
                             fm.get('bahnschrift_bold.ttf', 20, 'Bold'), 'white', 'center')
                    j += 1

                j = 0
                for group in up:
                    img.paste(await load_image(RESOURCE_BASE_PATH / 'general' / 'orange_bord_small.png'),
                              (192 + (j % 3) * 287, 936 + (i - 9) * 194))
                    for k in range(len(group)):
                        img.paste(await load_image(
                            RESOURCE_BASE_PATH / 'avatar_side' / f'{group[k].icon.replace("Icon_", "Icon_Side_")}.png',
                            size=(40, 40)), (190 + (j % 3) * 287 + (k % 4) * 32, 928 + (i - 9) * 194))
                    img.text(f'{i}-{j + 1} {info.floors[i].end_times_down[j].strftime("%H:%M:%S")}',
                             (192 + (j % 3) * 287, 463 + (j % 3) * 287), (978 + (i - 9) * 194),
                             fm.get('bahnschrift_regular.ttf', 24), '#40342d', 'center')
                    j += 1

                j = 0
                for group in down:
                    img.paste(await load_image(RESOURCE_BASE_PATH / 'general' / 'orange_bord_small.png'),
                              (330 + (j % 3) * 287, 936 + (i - 9) * 194))
                    for k in range(len(group)):
                        img.paste(await load_image(
                            RESOURCE_BASE_PATH / 'avatar_side' / f'{group[k].icon.replace("Icon_", "Icon_Side_")}.png',
                            size=(40, 40)), (328 + (j % 3) * 287 + (k % 4) * 32, 928 + (i - 9) * 194))
                    j += 1
            else:
                img.paste(await load_image(RESOURCE_BASE_PATH / 'abyss' / 'nock.png'), (192, 834 + (i - 9) * 194))

        else:
            img.paste(await load_image(RESOURCE_BASE_PATH / 'abyss' / 'nodata.png'), (192, 834 + (i - 9) * 194))

    return img
