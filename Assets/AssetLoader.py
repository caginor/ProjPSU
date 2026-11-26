"""Загрузка картинок. Вызывать ПОСЛЕ pygame.display.set_mode(): без окна convert() падает.

Результат - один словарь {имя: Surface}, его читают все:
  * рендер: стены по Models.Tiles.TILE_TEXTURES (wall, door_red, door_blue, exit, stairs);

Нет файла - вместо картинки цветная заглушка (цвета те же, что были у стен и предметов
до текстур), а в лог пишется строка. Игра запускается и без единой текстуры.
"""
import pygame

from Logging.Logger import Logger
from Settings.Settings import settings

WALL_COLORS = {
    "wall": (130, 135, 145),
    "door_red": (200, 60, 60),
    "door_blue": (60, 110, 220),
    "exit": (70, 200, 90),
    "stairs": (225, 185, 55),
}


class AssetLoader:
    @staticmethod
    def make_fallback(name: str, size: tuple[int, int] | None) -> pygame.Surface:
        """Заглушка для отсутствующей картинки."""
        if name in WALL_COLORS:                                   # стена: цвет + тёмная сетка
            color = WALL_COLORS[name]
            surface = pygame.Surface((64, 64))
            surface.fill(color)
            dark = tuple(channel // 2 for channel in color)
            for line in range(0, 64, 16):
                pygame.draw.line(surface, dark, (line, 0), (line, 63))
                pygame.draw.line(surface, dark, (0, line), (63, line))
            return surface

        if name == "door_anim":                                   # дверь анимации: коричневая с рамкой
            surface = pygame.Surface(size or settings.door.Animation_size)
            surface.fill((90, 50, 25))
            pygame.draw.rect(surface, (40, 20, 10), surface.get_rect(), 6)
            return surface

    @staticmethod
    def load_image(
        path: str, name: str, size: tuple[int, int] | None = None, alpha: bool = False
    ) -> pygame.Surface:
        try:
            image = pygame.image.load(path)
        except (FileNotFoundError, pygame.error) as exc:
            Logger.error(f"AssetLoader: can't load {path}: {exc}")
            image = AssetLoader.make_fallback(name, size)

        # convert() ускоряет отрисовку; convert_alpha() сохраняет прозрачность
        image = image.convert_alpha() if alpha else image.convert()
        if size:
            image = pygame.transform.scale(image, size)           # без сглаживания: чёткие пиксели
        return image

    @classmethod
    def load_assets(cls) -> dict[str, pygame.Surface]:
        textures = settings.textures
        assets: dict[str, pygame.Surface] = {}

        for name, path in textures.Paths.items():
            if name == "door_anim":
                assets[name] = cls.load_image(path, name, settings.door.Animation_size)
            else:
                assets[name] = cls.load_image(path, name)

        return assets