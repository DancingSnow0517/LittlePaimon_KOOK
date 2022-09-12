import logging
from typing import Dict, Optional

from khl.command import Command, DefaultLexer

log = logging.getLogger(__name__)


class CommandInfo:
    name: str
    desc: str
    usage: str
    cmd: Command

    def __init__(self, name: str, desc: str, usage: str, cmd: Command) -> None:
        self.name = name
        self.desc = desc
        self.usage = usage
        self.cmd = cmd

    def __repr__(self) -> str:
        return f"CommandInfo(name={self.name}, desc={self.desc}, usage={self.usage})"


class CommandInfoManager:
    _info_map: Dict[str, CommandInfo]

    def __init__(self) -> None:
        self._info_map = {}

    def __call__(self, desc: str = '暂无命令介绍', usage: str = '暂无命令用法'):
        def _dec(cmd: Command):
            self.add(CommandInfo(cmd.name, desc, usage, cmd))
            return cmd

        return _dec

    def add(self, info: CommandInfo):
        self._info_map[info.name] = info

    def get(self, name: str) -> Optional[CommandInfo]:
        if name in self._info_map:
            return self._info_map.get(name)
        else:
            for cmd_info in self._info_map.values():
                if isinstance(cmd_info.cmd.lexer, DefaultLexer):
                    if name in cmd_info.cmd.lexer.triggers:
                        return cmd_info
            return None

    def pop(self, name: str) -> Optional[CommandInfo]:
        if name in self._info_map:
            info = self._info_map[name]
            del self._info_map[name]
        else:
            return None
        return info

    def __setitem__(self, name: str, info: CommandInfo):
        if name in self._info_map:
            raise ValueError(f'command_info: {name} already exists')
        self._info_map[name] = info
        log.debug(f'command_info: {name} added')

    def __getitem__(self, item) -> Optional[CommandInfo]:
        return self.get(item)

    def __iter__(self):
        return iter(self._info_map.items())

    @property
    def info_map(self):
        return self._info_map
