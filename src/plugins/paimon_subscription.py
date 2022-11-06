import datetime
import logging
import re
from typing import TYPE_CHECKING

from khl import Message, EventTypes, Event, GuildUser, User, MessageTypes
from khl_card import CardMessage, Card, ThemeTypes
from khl_card.accessory import PlainText, Button, Kmarkdown
from khl_card.modules import Section, Header, ActionGroup

from .paimon_auto_bbs import mhy_bbs_sign
from .paimon_cloud_genshin import sign
from .paimon_daily_note.draw import draw_daily_note_card
from ..database.models.cookie import PrivateCookie
from ..database.models.subscription import DailyNoteSub, MihoyoBBSSub, CloudGenshinSub
from ..utils.genshin_api import get_mihoyo_private_data
from ..utils.message_util import update_message, update_private_message

if TYPE_CHECKING:
    from ..bot import LittlePaimon

log = logging.getLogger(__name__)


async def on_startup(bot: 'LittlePaimon'):
    @bot.command_info('显示你的所有订阅信息', '!!订阅信息')
    @bot.my_command('sub', aliases=['订阅信息', '订阅'])
    async def sub(msg: Message):
        await msg.reply((await gen_sub_card(msg.author.id)).build())

    @bot.on_event(EventTypes.MESSAGE_BTN_CLICK)
    async def on_btn_click(_: 'LittlePaimon', event: Event):
        value = event.body['value']  # type: str
        msg_id = event.body['msg_id']
        user_id = event.body['user_id']
        if 'guild_id' in event.body:
            guild_id = event.body['guild_id']
            user = GuildUser(guild_id=guild_id, _gate_=bot.client.gate, _lazy_loaded_=True, **event.body['user_info'])
            target_id = event.body['target_id']
        else:
            guild_id = None
            user = User(_gate_=bot.client.gate, _lazy_loaded_=True, **event.body['user_info'])
            target_id = None

        match = re.match(r'^sub_(?P<type>\w+)_(?P<uid>\d+)$', value)
        if match:
            type = match.group('type')
            uid = match.group('uid')
            if type == 'daily_note':
                if (await DailyNoteSub.get_or_none(uid=uid)) is None:
                    await DailyNoteSub.create(user_id=user_id, uid=uid, last_remind_time=datetime.datetime.now())
            elif type == 'mihoyo_bbs':
                if (await MihoyoBBSSub.get_or_none(uid=uid)) is None:
                    await MihoyoBBSSub.create(user_id=user_id, uid=uid)
            elif type == 'cloud_genshin':
                if cloud_genshin := await CloudGenshinSub.get_or_none(uid=uid):
                    if not cloud_genshin.auto_sign:
                        cloud_genshin.auto_sign = True
                        await cloud_genshin.save()
                else:
                    if isinstance(user, GuildUser) and target_id:
                        await (await bot.client.fetch_public_channel(target_id)).send('请先绑定云原神token')
                    else:
                        await user.send('请先绑定云原神token')
            if guild_id is not None:
                await update_message((await gen_sub_card(user_id)).build(), msg_id, user_id, bot.client.gate)
            else:
                await update_private_message((await gen_sub_card(user_id)).build(), msg_id, bot.client.gate)
        match = re.match(r'^unsub_(?P<type>\w+)_(?P<uid>\d+)$', value)
        if match:
            type = match.group('type')
            uid = match.group('uid')
            if type == 'daily_note':
                if (daily_note := await DailyNoteSub.get_or_none(uid=uid)) is not None:
                    await daily_note.delete()
            elif type == 'mihoyo_bbs':
                if (mihoyo_bbs := await MihoyoBBSSub.get_or_none(uid=uid)) is not None:
                    await mihoyo_bbs.delete()
            elif type == 'cloud_genshin':
                if cloud_genshin := await CloudGenshinSub.get_or_none(uid=uid):
                    if cloud_genshin.auto_sign:
                        cloud_genshin.auto_sign = False
                        await cloud_genshin.save()
                else:
                    if isinstance(user, GuildUser) and target_id:
                        await (await bot.client.fetch_public_channel(target_id)).send('请先绑定云原神token')
                    else:
                        await user.send('请先绑定云原神token')
            if guild_id is not None:
                await update_message((await gen_sub_card(user_id)).build(), msg_id, user_id, bot.client.gate)
            else:
                await update_private_message((await gen_sub_card(user_id)).build(), msg_id, bot.client.gate)

    @bot.task.add_cron(hour=6, timezone='Asia/Shanghai')
    async def sign_bbs():
        for user in await MihoyoBBSSub.all():
            ck = await PrivateCookie.get_or_none(uid=user.uid)
            if ck:
                _, result = await mhy_bbs_sign(ck.user_id, ck.uid)
                try:
                    await (await bot.client.fetch_user(ck.user_id)).send(result)
                except Exception as e:
                    log.info(f'给用户 {ck.user_id} 发送信息失败: {e}')

    @bot.task.add_cron(hour=6, timezone='Asia/Shanghai')
    async def sign_cloud_genshin():
        uid_list = await CloudGenshinSub.all()
        for uid in uid_list:
            msg = await sign(uid)
            try:
                await (await bot.client.fetch_user(uid.user_id)).send(msg)
            except Exception as e:
                log.info(f'云原神自动签到: UID{uid.uid} 发生错误 {e}')

    @bot.task.add_interval(minutes=30, timezone='Asia/Shanghai')
    async def check():
        for user in await DailyNoteSub.all():
            last_remind_time = user.last_remind_time
            difference = datetime.datetime.now() - last_remind_time.replace(tzinfo=None)
            if difference.total_seconds() <= 28800:
                continue
            data = await get_mihoyo_private_data(user.uid, user.user_id, 'daily_note')
            if isinstance(data, str):
                log.info(f'原神实时便签: ➤ 用户 {user.user_id} UID {user.uid} 获取数据失败, {data}')
                continue
            elif data['retcode'] != 0:
                log.info(
                    f'原神实时便签: ➤ 用户 {user.user_id} UID {user.uid}, 获取数据失败，code为 {data["retcode"]}， msg为 {data["message"]}')
                continue
            else:
                log.info(f'原神实时便签: ➤ 用户 {user.user_id} UID {user.uid}, 获取数据成功')
                if data['data']['current_resin'] >= 140:
                    try:
                        img = await draw_daily_note_card(data, user.uid)
                        log.info(f'原神实时便签: ➤➤ 用户 {user.user_id} UID {user.uid}, 绘制图片成功')
                        img.save('Temp/ssbq.png')

                        url = await bot.client.create_asset('Temp/ssbq.png')
                    except Exception as e:
                        log.info(f'原神实时便签: ➤➤ 用户 {user.user_id} UID {user.uid}, 绘制图片失败，{e}')
                        continue
                    u = await bot.client.fetch_user(user.user_id)
                    if data['data']['current_resin'] >= data['data']['max_resin']:
                        await u.send('树脂溢出了~')
                    else:
                        await u.send('树脂快要溢出了~')
                    await u.send(url, type=MessageTypes.IMG)
                    user.last_remind_time = datetime.datetime.now()
                    await user.save()


async def gen_sub_card(user_id: str):
    cookies = await PrivateCookie.filter(user_id=user_id)
    modules = []
    for ck in cookies:
        modules.append(Section(Kmarkdown(f'UID: **{ck.uid}**')))
        modules.append(await get_buttons(ck.uid))

    modules.append(Header('你的云原神：'))
    cloud_genshin = await CloudGenshinSub.filter(user_id=user_id)
    counter = 0
    buttons = []
    for cloud in cloud_genshin:
        counter += 1
        buttons.append(Button(PlainText(cloud.uid),
                              value=f'sub_cloud_genshin_{cloud.uid}' if not cloud.auto_sign else f'unsub_cloud_genshin_{cloud.uid}',
                              theme=ThemeTypes.DANGER if not cloud.auto_sign else ThemeTypes.SUCCESS,
                              click='return-val'))
        if counter == 4:
            counter = 0
            modules.append(ActionGroup(*buttons))
            buttons.clear()
    if counter != 0:
        modules.append(ActionGroup(*buttons))
    cm = CardMessage(Card(
        Header('你的订阅：'),
        *modules,
        theme=ThemeTypes.WARNING
    ))
    return cm


async def get_buttons(uid: str):
    daily_note = await DailyNoteSub.get_or_none(uid=uid)
    mihoyo_bbs = await MihoyoBBSSub.get_or_none(uid=uid)
    return ActionGroup(
        Button(PlainText('实时便笺'),
               value=f'sub_daily_note_{uid}' if daily_note is None else f'unsub_daily_note_{uid}',
               theme=ThemeTypes.DANGER if daily_note is None else ThemeTypes.SUCCESS,
               click='return-val'),
        Button(PlainText('米游社签到'),
               value=f'sub_mihoyo_bbs_{uid}' if mihoyo_bbs is None else f'unsub_mihoyo_bbs_{uid}',
               theme=ThemeTypes.DANGER if mihoyo_bbs is None else ThemeTypes.SUCCESS,
               click='return-val')
    )
