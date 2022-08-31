import importlib
import inspect
import logging
import os
import re
from pathlib import Path
from threading import Thread
from typing import List

from gevent import pywsgi
from khl import Bot, Event, EventTypes, Message, GuildUser, User

from . import panels
from .api.panel import registered_panel, ClickablePanel
from .utils import database
from .utils.config import config
from .utils.message_util import update_message, update_private_message
from .webapp import app

log = logging.getLogger(__name__)


class WebappThread(Thread):
    server: pywsgi.WSGIServer = None

    def run(self) -> None:
        super().run()
        log.info('正在启动web服务...')
        self.server = pywsgi.WSGIServer((config.web_app_address, config.web_app_port), app, log=None)
        self.server.serve_forever()

    def stop(self):
        if self.server:
            self.server.stop()


class LittlePaimon(Bot):

    def __init__(self):
        super().__init__(config.token)

    def my_command(self, name: str = '', *, aliases: List[str] = (), rules=()):
        return self.command(name, prefixes=['!!', '！！'], aliases=list(aliases), rules=list(rules))


def main():
    bot = LittlePaimon()

    webapp_thread = WebappThread()

    @bot.on_startup
    async def on_startup(_: LittlePaimon):
        if config.enable_web_app:
            webapp_thread.start()
        await database.init()
        print(await database.get_cookies())
        await database.add_cookie('123123', '123123', '123123')
        await database.remove_cookies(uid='123123')
        for i in inspect.getmembers(
                panels,
                lambda x: issubclass(x, ClickablePanel) if inspect.isclass(x) and x != ClickablePanel else False
        ):
            i[1]().registry()

    @bot.on_startup
    async def load_plugins(_: LittlePaimon):
        log.info('正在加载插插件。。。')
        modules = get_plugins('src/plugins')

        for module in modules:
            module = importlib.import_module(module, 'src.plugins')
            func = getattr(module, 'on_startup')
            await func(bot)

        log.info('插件加载完成。共 %d 个', len(modules))

    @bot.command(name='test')
    async def test(msg: Message):
        await msg.reply(panels.TestPanel.get_panel().build())

    @bot.on_event(EventTypes.MESSAGE_BTN_CLICK)
    async def on_button_click(_: LittlePaimon, event: Event):
        value = event.body['value']
        msg_id = event.body['msg_id']
        user_id = event.body['user_id']
        if 'guild_id' in event.body:
            guild_id = event.body['guild_id']
            user = GuildUser(guild_id=guild_id, _gate_=bot.client.gate, _lazy_loaded_=True, **event.body['user_info'])
        else:
            guild_id = None
            user = User(_gate_=bot.client.gate, _lazy_loaded_=True, **event.body['user_info'])

        match = re.match(r'^open_panel_([a-zA-Z_0-9]+)$', value)
        if match:
            panel_id = match.group(1)
            if panel_id in registered_panel:
                if guild_id is not None:
                    await update_message(registered_panel[panel_id].get_panel().build(), msg_id, user_id,
                                         bot.client.gate)
                else:
                    await update_private_message(registered_panel[panel_id].get_panel().build(), msg_id,
                                                 bot.client.gate)

    bot.run()
    webapp_thread.stop()


def get_plugins(package='.') -> List[str]:
    modules = []
    for file in os.listdir(package):
        if not file.startswith('__'):
            name, ext = os.path.splitext(file)
            modules.append("." + name)
    return modules
