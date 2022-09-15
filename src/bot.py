import asyncio
import hashlib
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
from khl_card import Card

from . import panels
from .api.command import CommandInfoManager
from .api.panel import registered_panel, ClickablePanel
from .database import connect
from .panels import MainPanel
from .utils import requests
from .utils.browser import install_browser
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
            log.info('正在关闭web服务...')
            self.server.stop()


class LittlePaimon(Bot):
    command_info: CommandInfoManager

    def __init__(self):
        super().__init__(config.token)
        self.command_info = CommandInfoManager()

    def my_command(self, name: str = '', *, aliases: List[str] = (), rules=()):
        return self.command(name, prefixes=['!!', '！！'], aliases=list(aliases), rules=list(rules))

    def admin_command(self, name: str = '', *, aliases: List[str] = (), rules=()):
        return self.my_command(name, aliases=aliases, rules=rules + (self.is_admin,))

    @staticmethod
    def is_admin(msg: Message) -> bool:
        """a rule check is admin"""
        return msg.author.id in config.admin


def main():
    bot = LittlePaimon()
    webapp_thread = WebappThread()

    @bot.on_startup
    async def on_startup(_: LittlePaimon):
        await connect()
        await check_resource()
        await install_browser()
        if config.enable_web_app:
            webapp_thread.start()
        for i in inspect.getmembers(
                panels,
                lambda x: issubclass(x, ClickablePanel) if inspect.isclass(x) and x != ClickablePanel else False
        ):
            i[1]().registry()

        if os.path.exists('Temp'):
            if not os.path.isdir('Temp'):
                log.error('Temp 不是个文件夹')
        else:
            os.mkdir('Temp')

    @bot.on_startup
    async def load_plugins(_: LittlePaimon):
        log.info('正在加载插插件。。。')
        modules = get_plugins('src/plugins')

        for module in modules:
            module = importlib.import_module(module, 'src.plugins')
            func = getattr(module, 'on_startup')
            await func(bot)

        log.info('插件加载完成。共 %d 个', len(modules))

    @bot.command_info('小派蒙的帮助信息', '直接 !!help 即可。或 !!help [命令名字] 来查看具体命令用法')
    @bot.my_command('help', aliases=['帮助'])
    async def help_panel(msg: Message, cmd: str = None):
        if cmd is None:
            await msg.ctx.channel.send(MainPanel.get_panel().build())
        elif cmd == 'all':
            cards = [info.make_help_card() for info in bot.command_info.info_map.values()]
            card = Card(color='#FF74E3')
            for c in cards:
                card.modules += c.modules
            print(card.build_to_json())
            await msg.reply([card.build()])
        else:
            info = bot.command_info.get(name=cmd)
            if info:
                await msg.reply([info.make_help_card().build()])
            else:
                await msg.reply(f'未找到命令： {cmd}')

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


async def check_resource():
    res_path = Path() / 'resources' / 'LittlePaimon'
    log.info('正在检查资源完整性...')
    resource_list = (await requests.get('http://img.genshin.cherishmoon.fun/resources/resources_list')).json()
    for resource in resource_list:
        file_path = res_path.parent / resource['path']
        if file_path.exists():
            if not resource['lock'] or hashlib.md5(file_path.read_bytes()).hexdigest() == resource['hash']:
                continue
            else:
                file_path.unlink()
        try:
            await requests.download(f'http://img.genshin.cherishmoon.fun/resources/{resource["path"]}', file_path)
            await asyncio.sleep(0.5)
        except Exception:
            log.warning(f'下载 {resource["path"].split("/")[-1]} 失败')
    log.info('资源检查完成')
