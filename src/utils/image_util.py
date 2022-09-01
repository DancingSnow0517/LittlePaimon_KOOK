from PIL import ImageFont

from ..config.path import FONTS_PATH


class FontManager:
    def __init__(self) -> None:
        self.font_path = FONTS_PATH
        self.fonts = [font_name.stem + font_name.suffix for font_name in FONTS_PATH.iterdir() if font_name.is_file()]
        self.fonts_cache = {}

    def get(self, font_name: str = 'hywh.ttf', size: int = 25, variation: str = None) -> ImageFont.ImageFont:
        """
        获取字体，如果已在缓存中，则直接返回
        :param font_name: 字体名称
        :param size: 字体大小
        :param variation: 字体变体
        """
        if 'ttf' not in font_name and 'ttc' not in font_name and 'otf' not in font_name:
            font_name += '.ttf'
        if font_name not in self.fonts:
            font_name = font_name.replace('.ttf', '.ttc')
        if font_name not in self.fonts:
            raise FileNotFoundError(f'不存在字体文件 {font_name} ，请补充至字体资源中')
        if f'{font_name}-{size}' in self.fonts_cache:
            font = self.fonts_cache[f'{font_name}-{size}']
        else:
            font = ImageFont.truetype(str(self.font_path / font_name), size)
        self.fonts_cache[f'{font_name}-{size}'] = font
        if variation:
            font.set_variation_by_name(variation)
        return font


font_manager = FontManager()
