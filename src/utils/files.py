import json
from pathlib import Path
from typing import Union


def load_json(path: Union[Path, str], encoding: str = 'utf-8'):
    """
    读取本地json文件，返回文件数据。
    :param path: 文件路径
    :param encoding: 编码，默认为utf-8
    :return: 数据
    """
    if isinstance(path, str):
        path = Path(path)
    return json.load(path.open('r', encoding=encoding)) if path.exists() else {}


def save_json(data: dict, path: Union[Path, str] = None, encoding: str = 'utf-8'):
    """
    保存json文件
    :param data: json数据
    :param path: 保存路径
    :param encoding: 编码
    """
    if isinstance(path, str):
        path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    json.dump(data, path.open('w', encoding=encoding), ensure_ascii=False, indent=4)
