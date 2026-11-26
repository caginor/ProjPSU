"""Единственный источник конфигурации проекта.

Заменил корневой settings.py с плоскими константами. Важное правило: конфиг читают
через экземпляр `settings`, а не через класс `Settings` - у dataclass-поля без default'а
нет атрибутов класса, и `Settings.items`/`Settings.skip_keys` из прошлой версии падали
с AttributeError в половине модулей.

Поля объявлены с аннотациями (: вместо =), иначе @dataclass их не видит, класс получает
только class-атрибуты, а asdict() возвращает {'screen': {}, 'items': {}, ...} - то есть
пустой settings.json.

На импорте больше нет побочных эффектов: JSON пишется только по прямому запуску модуля
(python -m Settings.Settings) и только для отладки, читателя у него нет.
"""
import json
from dataclasses import asdict, dataclass, field
import math

import pygame


@dataclass
class ScreenSettings:
    Width: int = 1920
    Height: int = 1080
    FPS: int = 60
    Hud_height: int = 120
    Game_height: int = field(init=False)
    Half_of_game_height: int = field(init=False)

    def __post_init__(self) -> None:
        self.Game_height = self.Height - self.Hud_height
        self.Half_of_game_height = self.Game_height // 2


@dataclass
class SkipKeys:
    Skip_keys: tuple = (pygame.K_ESCAPE, pygame.K_SPACE, pygame.K_RETURN)


@dataclass
class ViewDistance:
    Distance: float = 6.0


@dataclass
class Raycasting:
    Walls_height: int = 1000
    Fov: float = math.pi / 3                 # угол обзора
    Ray_width: int = 3                       # ширина колонки в пикселях (1920 / 3 = 640 лучей)
    Sprite_scale: float = 0.3                # размер предметов относительно стены
    Half_fov: float = field(init=False)
    Num_rays: int = field(init=False, default=0)         # считает Settings.__post_init__ (нужна ширина экрана)
    Delta_angle: float = field(init=False, default=0.0)  # считает Settings.__post_init__

    def __post_init__(self) -> None:
        self.Half_fov = self.Fov / 2


# --- [Человек 1] игрок и текстуры ---
@dataclass
class PlayerSettings:
    Speed: float = 3.0                       # клеток в секунду
    Rot_speed: float = 2.2                   # радиан в секунду
    Radius: float = 0.2                      # радиус хитбокса


@dataclass
class Textures:
    """Имена - контракт между рендером и остальными: стены берутся по Models.Tiles.TILE_TEXTURES,
    предметы - по id из карты. 'key' - одна картинка, из неё красятся ключи из Keys.Names.
    Нет файла - рисуется цветная заглушка (см. Assets/AssetLoader.py)."""

    Paths: dict = field(
        default_factory=lambda: {
            "wall": "textures/wall.png",                # стена
            "door_red": "textures/door_red.png",        # красная дверь
            "door_blue": "textures/door_blue.png",      # синяя дверь
            "exit": "textures/exit.png",                # выход на улицу
            "stairs": "textures/stairs.png",            # лестница (вниз и вверх)
        }
    )


@dataclass
class Items:
    Names: dict = field(
        default_factory=lambda: {
            "coal": "Уголь",
            "gauze": "Марля",
            "bottle": "Бутылка",
        }
    )


@dataclass
class Keys:
    Names: dict = field(
        default_factory=lambda: {
            "key_red": ("Красный ключ", (255, 90, 90)),
            "key_blue": ("Синий ключ", (90, 140, 255)),
        }
    )


@dataclass
class Title:
    Fade_time: float = 1.2
    Pre_intro_messages: list = field(
        default_factory=lambda: [
            ["Идея игры вдохновлена", "предхеллоуинским видео от студентов ПГНИУ"],
        ]
    )
    Message_hold_time: float = 4.0
    Text: str = "СБЕГИ ИЗ ПГНИУ"
    Lines: list = field(
        default_factory=lambda: [
            "Тебе понадобится самодельный противогаз,",
            "чтобы выйти наружу.",
        ]
    )
    Hold_time: float = 5.0


@dataclass
class Door:
    Animation_size: tuple = (420, 520)
    Opening_time: float = 0.8
    Fade_time: float = 0.4


@dataclass
class Clip:
    """Видеопролог. Файла нет или moviepy не стоит - интро пропускается, игра стартует."""

    Path: str = "intro/video.mp4"


@dataclass
class Settings:
    screen: ScreenSettings = field(default_factory=ScreenSettings)
    skip_keys: SkipKeys = field(default_factory=SkipKeys)
    view: ViewDistance = field(default_factory=ViewDistance)
    raycasting: Raycasting = field(default_factory=Raycasting)
    items: Items = field(default_factory=Items)
    keys: Keys = field(default_factory=Keys)
    title: Title = field(default_factory=Title)
    door: Door = field(default_factory=Door)
    clip: Clip = field(default_factory=Clip)
    player: PlayerSettings = field(default_factory=PlayerSettings)   # [Человек 1]
    textures: Textures = field(default_factory=Textures)             # [Человек 1]
    world: WorldSettings = field(default_factory=WorldSettings)      # [Человек 2]

    def __post_init__(self) -> None:
        """Производные величины, которым нужны сразу две секции конфига."""
        rays = self.raycasting
        rays.Num_rays = self.screen.Width // rays.Ray_width
        rays.Delta_angle = rays.Fov / rays.Num_rays

settings = Settings()


def dump(path: str = "settings.json") -> str:
    """Отладочный дамп конфига. Вызывается вручную, приложению не нужен."""
    with open(path, "w", encoding="utf-8") as file:
        json.dump(asdict(settings), file, indent=2, ensure_ascii=False)
    return path


if __name__ == "__main__":
    print(f"конфиг выписан в {dump()}")