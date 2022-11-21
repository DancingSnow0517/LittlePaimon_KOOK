import logging
from typing import TYPE_CHECKING

from khl import Message, MessageTypes

from .data_source import get_gacha_log_data, get_gacha_log_img, gacha_log_to_UIGF
from ...database.models.cookie import PrivateCookie

if TYPE_CHECKING:
    from ...bot import LittlePaimon

log = logging.getLogger(__name__)

running_update = []
running_show = []


async def on_startup(bot: 'LittlePaimon'):
    @bot.my_command('update_log', aliases=['更新抽卡记录', '抽卡记录更新', '获取抽卡记录'])
    async def update_log(msg: Message, uid: str = None):
        if uid is None:
            ck = await PrivateCookie.get_or_none(user_id=msg.author.id)
        else:
            ck = await PrivateCookie.get_or_none(user_id=msg.author.id, uid=uid)
        if ck is None:
            await msg.reply('没有找到你的cookie')
            return

        if f'{ck.user_id}-{ck.uid}' in running_update:
            await msg.reply(f'UID{ck.uid}已经在获取抽卡记录中，请勿重复发送')
            return
        await msg.ctx.channel.send(f'开始为UID{ck.uid}更新抽卡记录，请稍候...')
        running_update.append(f'{ck.user_id}-{ck.uid}')
        try:
            result = await get_gacha_log_data(ck.user_id, ck.uid)
            await msg.reply(result)
        except Exception as e:
            log.info(f'原神抽卡记录 ➤➤更新抽卡记录时出现错误: {e}')
            await msg.reply(f'更新抽卡记录时出现错误：{e}')
        running_update.remove(f'{ck.user_id}-{ck.uid}')

    @bot.my_command('show_log', aliases=['查看抽卡记录', '抽卡记录', '查询抽卡记录'])
    async def show_log(msg: Message, uid: str = None):
        if uid is None:
            ck = await PrivateCookie.get_or_none(user_id=msg.author.id)
        else:
            ck = await PrivateCookie.get_or_none(user_id=msg.author.id, uid=uid)
        if ck is None:
            await msg.reply('没有找到你的cookie')
            return
        if f'{ck.user_id}-{ck.uid}' in running_show:
            await msg.reply(f'UID{ck.uid}已经在绘制抽卡记录分析中，请勿重复发送')
            return
        log.info(f'原神抽卡记录: ➤ 用户: {ck.user_id}, UID: {ck.uid}, 开始绘制抽卡记录图片')
        running_show.append(f'{ck.user_id}-{ck.uid}')
        await msg.ctx.channel.send(f'开始为UID{ck.uid}绘制抽卡记录分析，请稍候...')
        try:
            result = await get_gacha_log_img(msg.author, ck.uid)
            if isinstance(result, str):
                await msg.reply(result)
            else:
                result.save('Temp/gacha_log.png')
                await msg.reply(await bot.client.create_asset('Temp/gacha_log.png'), type=MessageTypes.IMG)
        except Exception as e:
            log.info(f'原神抽卡记录: ➤➤绘制抽卡记录图片时出现错误：{e}')
            await msg.reply(f'绘制抽卡记录分析时出现错误：{e}')
        running_show.remove(f'{ck.user_id}-{ck.uid}')

    @bot.my_command('export_log', aliases=['导出抽卡记录', '抽卡记录导出'])
    async def export_log(msg: Message, uid: str = None):
        if uid is None:
            ck = await PrivateCookie.get_or_none(user_id=msg.author.id)
        else:
            ck = await PrivateCookie.get_or_none(user_id=msg.author.id, uid=uid)
        if ck is None:
            await msg.reply('没有找到你的cookie')
            return
        state, message, path = gacha_log_to_UIGF(ck.user_id, ck.uid)
        if not state:
            await msg.reply(message)
        else:
            try:
                url = await bot.client.create_asset(path)
                await msg.reply(url, type=MessageTypes.FILE)
            except Exception as e:
                await msg.reply(f'上传文件失败，错误信息：{e}')
