"""HEADless-проверка структуры: все модули импортируются, все экраны рисуются.

    python tools/smoke_test.py

Экран не открывается: pygame работает на dummy-видеодрайвере, события не приходят.
Тайминги заставок обнуляются через settings - это и проверка, что конфиг единственный.
Смысл ровно один: заменить "один раз запустить глазами", чего у проекта не было.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame  # noqa: E402

MODULES = [
    "Colors.Color",
    "Errors",
    "Logging.Logger",
    "Models.DoorStates",
    "Models.Display",
    "Models.ParametrizedLine",
    "Models.Text",
    "Models.Tiles",
    "Settings.Settings",
    "Player.Player",
    "InventoryHandler.InventoryHandler",
    "UI.TextWriter",
    "UI.Fade",
    "UI.Backgrounds",
    "UI.Door",
    "UI.GameElementDrawer",
    "UI.ScreenWriter",
    "Intro.IntroPlayer",
    "GameManager.GameManager",
    "Assets.AssetLoader",
    "Raycasting.RayCaster",
    "Raycasting.SpriteDrawer",
    "Raycasting.Scene",
    "GameManager.game",
    "map",
    "main",
]


def check_imports() -> None:
    import importlib

    for name in MODULES:
        importlib.import_module(name)
        print(f"  import {name}")


def check_screens() -> None:
    from InventoryHandler.InventoryHandler import InventoryHandler
    from Models.DoorStates import DoorStates
    from Player.Player import Player
    from Settings.Settings import settings
    from UI.Backgrounds import create_background, create_vignette
    from UI.Door import Door, Side
    from UI.GameElementDrawer import GameElementDrawer
    from UI.ScreenWriter import ScreenWriter

    pygame.init()
    screen = pygame.display.set_mode((settings.screen.Width, settings.screen.Height))
    clock = pygame.time.Clock()

    background = create_background()
    assert background.get_size() == (settings.screen.Width, settings.screen.Game_height)
    assert background.get_at((0, 0)) != background.get_at((0, settings.screen.Half_of_game_height - 1)), \
        "фон у горизонта не должен быть таким же, как у края"

    vignette = create_vignette()
    center = vignette.get_at((settings.screen.Width // 2, settings.screen.Game_height // 2)).a
    corner = vignette.get_at((2, settings.screen.Game_height - 3)).a
    assert corner > center, f"виньетка должна темнить края (центр {center}, угол {corner})"

    screen.blit(background, (0, 0))
    screen.blit(vignette, (0, 0))

    door = Door(pygame.Surface(settings.door.Animation_size).convert())
    door.start(lambda: None, Side.Dir_right)
    assert door.rect.bottom <= settings.screen.Game_height, \
        f"дверь ниже 3D-вида: bottom={door.rect.bottom}, Game_height={settings.screen.Game_height}"
    for _ in range(200):
        door.update(1 / 60)
        door.draw(screen)
    assert door.state == DoorStates.Idle and door.action is None, "автомат не вернулся в Idle"

    pygame.draw.rect(screen, (40, 40, 40), (0, 0, settings.screen.Width, settings.screen.Game_height))
    drawer = GameElementDrawer(screen, clock)
    drawer.draw_fps()
    drawer.draw_crosshair()
    player = Player()
    InventoryHandler.initialize({"coal": pygame.Surface((16, 16)).convert()})
    player.inventory.add("coal")
    InventoryHandler.update(player.inventory, player.keys)
    drawer.draw_hud(player, "Подобран уголь", "Ищи марлю в аудитории справа")

    writer = ScreenWriter(screen)
    settings.title.Fade_time = 0.001
    settings.title.Hold_time = 0.0
    settings.title.Message_hold_time = 0.0
    assert writer.show_title_screen(), "титул должен отработать до конца"
    assert writer.show_messages(), "сообщения должны отработать до конца"
    writer.draw_win_screen()
    pygame.display.flip()


def check_intro_fallback() -> None:
    """Без файла и без moviepy пролог обязан вернуть True, а не упасть."""
    from Intro.IntroPlayer import ClipHandler
    from Models.Display import Display
    from Settings.Settings import settings

    screen = pygame.display.set_mode((settings.screen.Width, settings.screen.Height))
    ClipHandler.initialize(os.path.join("intro", "нет-такого-файла.mp4"))
    assert ClipHandler.play_intro_clip(screen, Display(settings.screen.Width, settings.screen.Height)) is True
    ClipHandler.initialize()


def main() -> int:
    steps = [
        ("импорты всех модулей", check_imports),
        ("фон, виньетка, дверь, HUD", check_screens),
        ("пролог без видео", check_intro_fallback),
    ]
    for title, step in steps:
        print(f"[..] {title}")
        try:
            step()
        except Exception as exc:
            print(f"[XX] {title}: {type(exc).__name__}: {exc}")
            return 1
        print(f"[OK] {title}")
    print("\nструктура жива: импорты, экраны и тайминги работают")
    pygame.quit()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())