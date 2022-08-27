import os.path
from pathlib import Path
from shutil import copyfile

from pydantic import BaseModel


class Config(BaseModel):
    token: str
    log_level: str = 'INFO'

    @classmethod
    def parse_file(cls, *args, **kwargs):
        if not os.path.exists('config.json'):
            copyfile('resources/default_config.json', 'config.json')
        return super().parse_file(*args, **kwargs)


config = Config.parse_file(Path() / 'config.json')
