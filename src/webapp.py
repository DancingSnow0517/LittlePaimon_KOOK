import asyncio
import datetime
import logging
from pathlib import Path

from pywebio.input import textarea, input_group, checkbox, input
from pywebio.output import put_markdown, popup
from pywebio.platform import config as cfg
from pywebio.platform.flask import wsgi_app

from .database.models.cookie import LastQuery, PrivateCookie
from .utils.genshin_api import get_bind_game_info, get_stoken_by_cookie

log = logging.getLogger(__name__)
css_path = Path() / 'resources' / 'style.css'

with open('resources/style.css', 'r') as f:
    css = f.read()

loop = asyncio.new_event_loop()


@cfg(title='小派蒙绑定原神Cookie', description='绑定Cookie', css_style=css)
def bind_cookie_page():
    put_markdown('**重要提醒**：Cookie的作用相当于账号密码，非常重要，如是非可信任的机器人，请勿绑定！！')
    put_markdown('**获取`Cookie`方法**：详见 [Cookie获取教程](https://docs.qq.com/doc/DQ3JLWk1vQVllZ2Z1)')
    put_markdown(
        '**获取`KOOK用户id`方法**：打开开发者模式 (`KOOK设置`->`高级设置`->`开发者模式`)，右键你的头像然后`复制ID`')
    put_markdown('也可以使用 `!!原神绑定` 命令来查看你的`用户id`')
    data = input_group('绑定Cookie', [
        input('KOOK 用户id', name='user_id', required=True, validate=is_user_id, placeholder='KOOK 用户id'),
        textarea('米游社Cookie', name='cookie', required=True, validate=is_cookie, placeholder='Cookie'),
        checkbox(name='confirm', options=['我已知晓Cookie的重要性，确认绑定'], validate=is_confirm)
    ])
    result = loop.run_until_complete(bind_cookie(data))
    popup('绑定结果', put_markdown(result))


def is_cookie(cookie: str):
    if 'cookie_token' not in cookie or all(i not in cookie for i in ['account_id', 'login_uid', 'ltuid', 'stuid']):
        return 'Cookie必须包含cookie_token以及account_id、login_uid、ltuid、stuid其中之一'


def is_confirm(confirm: list):
    if not confirm:
        return '请先勾选确认'


def is_user_id(user_id: str):
    if not user_id.isdigit():
        return '必须是合法的 KOOK 用户id'


async def bind_cookie(data: dict):
    user_id = str(data['user_id'])
    cookie = data['cookie']
    if result := await get_bind_game_info(cookie):
        game_name = result['nickname']
        game_uid = result['game_role_id']
        mys_id = result['mys_id']
        await LastQuery.update_or_create(user_id=user_id,
                                         defaults={'uid': game_uid, 'last_time': datetime.datetime.now()})
        log.info(f'用户 {user_id} 成功绑定cookie')
        if 'login_ticket' in cookie and (stoken := await get_stoken_by_cookie(cookie)):
            await PrivateCookie.update_or_create(user_id=user_id, uid=game_uid, mys_id=mys_id,
                                                 defaults={'cookie': data['cookie'],
                                                           'stoken': f'stuid={mys_id};stoken={stoken};'})
            return f'`{user_id}` 成功绑定原神 **{game_name}** - **{game_uid}**'
        else:
            await PrivateCookie.update_or_create(user_id=user_id, uid=game_uid, mys_id=mys_id,
                                                 defaults={'cookie': data['cookie']})
            return f'`{user_id}` 成功绑定原神 **{game_name}** - **{game_uid}**\n' \
                   f'但cookie中没有`login_ticket`或`login_ticket`无效，`米游币相关功能`无法使用'
    else:
        return '这个`cookie` **无效** ，请确认是否正确\n请重新获取`cookie`后 **刷新** 本页面再次绑定'


app = wsgi_app(bind_cookie_page)
