import json
from pathlib import Path
from typing import Union, Optional, Tuple, Dict

from PIL import Image

from . import requests

cache_image: Dict[str, any] = {}
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                         'Chrome/104.0.0.0 Safari/537.36'}


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


async def load_image(
        path: Union[Path, str],
        *,
        size: Optional[Union[Tuple[int, int], float]] = None,
        crop: Optional[Tuple[int, int, int, int]] = None,
        mode: Optional[str] = None,
) -> Image.Image:
    """
    说明：
        读取图像，并预处理
    参数：
        :param path: 图片路径
        :param size: 预处理尺寸
        :param crop: 预处理裁剪大小
        :param mode: 预处理图像模式
        :return: 图像对象
    """
    if str(path) in cache_image:
        img = cache_image[str(path)]
    else:
        if path.exists():
            img = Image.open(path)
        elif path.name.startswith(('UI_', 'Skill_')):
            img = await requests.download_icon(path.name, headers=headers, save_path=path, follow_redirects=True)
        else:
            raise FileNotFoundError(f'{path} not found')
        cache_image[str(path)] = img
    if mode:
        img = img.convert(mode)
    if size:
        if isinstance(size, float):
            img = img.resize((int(img.size[0] * size), int(img.size[1] * size)), Image.ANTIALIAS)
        elif isinstance(size, tuple):
            img = img.resize(size, Image.ANTIALIAS)
    if crop:
        img = img.crop(crop)
    return img
