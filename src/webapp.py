import logging
from pathlib import Path

from pywebio.input import textarea, input_group, checkbox
from pywebio.output import put_markdown, popup
from pywebio.platform import config as cfg
from pywebio.platform.flask import wsgi_app

log = logging.getLogger(__name__)
css_path = Path() / 'resources' / 'style.css'

with open('resources/style.css', 'r') as f:
    css = f.read()


@cfg(title='小派蒙绑定原神Cookie', description='绑定Cookie', css_style=css)
def bind_cookie_page():
    put_markdown('**重要提醒**：Cookie的作用相当于账号密码，非常重要，如是非可信任的机器人，请勿绑定！！')
    put_markdown('**方法**：详见 [Cookie获取教程](https://docs.qq.com/doc/DQ3JLWk1vQVllZ2Z1)')
    data = input_group('绑定Cookie', [
        textarea('米游社Cookie', name='cookie', required=True),
        checkbox(name='confirm', options=['我已知晓Cookie的重要性，确认绑定'], validate=is_confirm)
    ])
    result = bind_cookie(data)
    popup('绑定结果', put_markdown(result))


def is_cookie(cookie: str):
    if 'cookie_token' not in cookie or all(i not in cookie for i in ['account_id', 'login_uid', 'ltuid', 'stuid']):
        return 'Cookie必须包含cookie_token以及account_id、login_uid、ltuid、stuid其中之一'


def is_confirm(confirm: list):
    if not confirm:
        return '请先勾选确认'


def bind_cookie(data: dict):
    print(data)
    return '测试'


app = wsgi_app(bind_cookie_page)
