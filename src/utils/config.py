import json
import os.path
from pathlib import Path
from shutil import copyfile
from typing import List

from pydantic import BaseModel


class Config(BaseModel):
    token: str
    log_level: str = 'INFO'
    enable_web_app: bool
    web_app_port: int
    web_app_address: str
    admin: List[str]
    public_ip: str
    botmarket_uuid: str
    github_proxy: str = 'https://ghproxy.com/'

    # noinspection PyTypeChecker
    @classmethod
    def parse_file(cls, *args, **kwargs) -> 'Config':
        if not os.path.exists('config.json'):
            copyfile('resources/default_config.json', 'config.json')
        return super().parse_file(*args, **kwargs)

    def save(self):
        with open('config.json', 'w', encoding='utf-8') as f:
            json.dump(self.dict(), f, indent=4, ensure_ascii=False)


config = Config.parse_file(Path() / 'config.json')
