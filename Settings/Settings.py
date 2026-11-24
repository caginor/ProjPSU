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

@dataclass
class PlayerSettings:
    Speed: float = 3.0                       # клеток в секунду
    Rot_speed: float = 2.2                   # радиан в секунду
    Radius: float = 0.2                      # радиус хитбокса

@dataclass
class Textures:
    """Имена - контракт между рендером и остальными: стены берутся по Models.Tiles.TILE_TEXTURES,
    предметы - по id из карты. 'key' - одна картинка, из неё красятся ключи из Keys.Names.
    Нет файла - рисуется цветная заглушка (см. Assets/Assets.py)."""

    Paths: dict = field(
        default_factory=lambda: {
            "wall": "textures/wall.png",                # стена
            "door_red": "textures/door_red.png",        # красная дверь
            "door_blue": "textures/door_blue.png",      # синяя дверь
            "exit": "textures/exit.png",                # выход на улицу
            "stairs": "textures/stairs.png",            # лестница (вниз и вверх)
            "door_anim": "textures/door_anim.png",      # дверь для анимации перехода
            "key": "textures/key.png",                  # ключ (светлый/серый, красится в цвет)
            "coal": "textures/coal.png",
            "gauze": "textures/gauze.png",
            "bottle": "textures/bottle.png",
        }
    )
    Item_size: tuple = (64, 64)              # предметы и ключи приводятся к этому размеру

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
    textures: Textures = field(default_factory=Textures)

settings = Settings()


def dump(path: str = "settings.json") -> str:
    """Отладочный дамп конфига. Вызывается вручную, приложению не нужен."""
    with open(path, "w", encoding="utf-8") as file:
        json.dump(asdict(settings), file, indent=2, ensure_ascii=False)
    return path


if __name__ == "__main__":
    print(f"конфиг выписан в {dump()}")