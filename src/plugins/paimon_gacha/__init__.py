from typing import TYPE_CHECKING

from khl import Message
from khl.command import Exceptions
from khl_card import CardMessage, Card
from khl_card.accessory import Image, Kmarkdown
from khl_card.modules import Container, Header, Section, Divider, Context

from .data_handle import load_user_data
from .draw import draw_gacha_img
from ...utils.message_util import on_exception

if TYPE_CHECKING:
    from ...bot import LittlePaimon


async def on_startup(bot: 'LittlePaimon'):
    @bot.command_info('原神模拟抽卡，卡池有 `常驻` `角色1` `角色2` `武器`', '抽[数量]十连[卡池]')
    @bot.command('sim_gacha', regex=r'^抽(?P<num>\d*)十连(?P<pool>\S*)$')
    async def sim_gacha(msg: Message, num: str, pool):
        num = int(num) if num != '' and num.isdigit() else 1
        if num <= 0 or num > 9:
            await msg.reply('一次性最多抽 9 次十连')
            return
        pool = pool or '角色1'
        try:
            result = await draw_gacha_img(msg.author.id, pool, num, msg.author.nickname)
        except IndexError:
            result = '当前没有可以抽的卡池哦~请等待卡池开放'
        except Exception as e:
            result = f'抽卡发生错误:{e}'
        if isinstance(result, str):
            await msg.reply(result)
            return
        else:
            result_url = []
            for img in result:
                img.save('Temp/gacha.png')
                result_url.append(await bot.client.create_asset('Temp/gacha.png'))

        cm = CardMessage(
            Card(
                Container(*[Image(url) for url in result_url])
            )
        )

        await msg.reply(cm.build())

    sim_gacha.on_exception(Exceptions.Handler.ArgLenNotMatched)(on_exception('模拟抽卡使用方法：抽[次数]十连[池子]'))

    # noinspection PyShadowingBuiltins
    @bot.command_info('查看模拟抽卡记录', '!!模拟抽卡记录 [角色|武器]')
    @bot.my_command('show_log', aliases=['模拟抽卡记录'])
    async def show_log(msg: Message, type: str = None):
        user_info = load_user_data(msg.author.id)
        if user_info['抽卡数据']['抽卡总数'] == 0:
            await msg.reply('你此前并没有抽过卡哦')
            return
        if type is None:
            card = Card(color='#87CEEB')
            data = user_info['抽卡数据']
            card.append(Header('你的模拟抽卡记录如下:'))
            card.append(Section(Kmarkdown(f'**你在本频道总共抽卡 {data["抽卡总数"]} 次**')))
            card.append(Section(Kmarkdown(f'其中五星共 **{data["5星出货数"]}** 个, 四星共{data["4星出货数"]}个')))

            try:
                t5 = '{:.2f}%'.format(((data['5星出货数'] / (
                            data['抽卡总数'] - data['角色池未出5星数'] - data['武器池未出5星数'] - data[
                        '常驻池未出5星数'])) * 100))
            except ZeroDivisionError:
                t5 = '0.00%'
            try:
                u5 = '{:.2f}%'.format(data['5星up出货数'] / data['5星出货数'] * 100)
            except ZeroDivisionError:
                u5 = '0.00%'
            try:
                t4 = '{:.2f}%'.format(((data['4星出货数'] / (
                            data['抽卡总数'] - data['角色池未出4星数'] - data['武器池未出4星数'] - data['常驻池未出4星数'])) * 100))
            except ZeroDivisionError:
                t4 = '0.00%'
            try:
                u4 = '{:.2f}%'.format(data['4星up出货数'] / data['4星出货数'] * 100)
            except ZeroDivisionError:
                u4 = '0.00%'
            dg_name = data['定轨武器名称'] if data['定轨武器名称'] != '' else '未定轨'

            card.append(Section(Kmarkdown(f'五星出货率为 **{t5}** up率为 **{u5}**')))
            card.append(Section(Kmarkdown(f'四星出货率为 **{t4}** up率为 **{u4}**')))

            card.append(Divider())
            card.append(Header('角色池:'))
            card.append(Section(
                Kmarkdown(f'目前 **{data["角色池未出5星数"]}** 抽未出五星 **{data["角色池未出4星数"]}** 抽未出四星')))
            card.append(Section(Kmarkdown(f'下次五星是否up: {data["角色池5星下次是否为up"]}')))
            card.append(Header('武器池:'))
            card.append(Section(
                Kmarkdown(f'目前 **{data["武器池未出5星数"]}** 抽未出五星 **{data["武器池未出4星数"]}** 抽未出四星')))
            card.append(Section(Kmarkdown(f'下次五星是否up: {data["武器池5星下次是否为up"]}')))
            card.append(Section(Kmarkdown(f'定轨武器为 **{dg_name}**, 能量值为 **{data["定轨能量"]}**')))
            card.append(Header('常驻池:'))
            card.append(Section(
                Kmarkdown(f'目前 **{data["常驻池未出5星数"]}** 抽未出五星 **{data["常驻池未出4星数"]}** 抽未出四星')))
        else:
            card = get_rw_record(type, user_info)
        card.append(Divider()).append(Context(Kmarkdown('Created By LittlePaimon')))
        await msg.reply([card.build()])

    show_log.on_exception(Exceptions.Handler.ArgLenNotMatched)(on_exception())

    # noinspection PyShadowingBuiltins
    def get_rw_record(type, user_info) -> Card:
        card = Card(color='#87CEEB')
        if type == '角色':
            if len(user_info['角色列表']):
                card.append(Header('你所拥有的角色如下:'))
                for role in user_info['角色列表'].items():
                    if len(role[1]['星级']) == 5:
                        card.append(Section(Kmarkdown(f'> {role[1]["星级"]}{role[0]}\n'
                                                      f'数量: {role[1]["数量"]} 出货: {" ".join([str(i) for i in role[1]["出货"]])}')))
                    else:
                        card.append(Section(Kmarkdown(f'> {role[1]["星级"]}{role[0]}\n'
                                                      f'数量: {role[1]["数量"]}')))
            else:
                card.append(Section(Kmarkdown('你还没有角色')))
        elif not len(user_info['武器列表']):
            card.append(Section(Kmarkdown('你还没有武器')))
        else:
            card.append(Header('你所拥有的武器如下:'))
            for wp in user_info['武器列表'].items():
                if len(wp[1]['星级']) == 5:
                    card.append(Section(Kmarkdown(f'> {wp[1]["星级"]}{wp[0]}\n'
                                                  f'数量: {wp[1]["数量"]} 出货: {" ".join([str(i) for i in wp[1]["出货"]])}')))
                else:
                    card.append(Section(Kmarkdown(f'> {wp[1]["星级"]}{wp[0]}\n'
                                                  f'数量: {wp[1]["数量"]}')))
        return card
