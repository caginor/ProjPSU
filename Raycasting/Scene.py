"""Кадр 3D-вида одной командой: пол/потолок -> стены -> виньетка.

Прицел, HUD, FPS и мини-карту рисует Game (через GameElementDrawer человека 3), сюда они
не входят. Создавать после pygame.display.set_mode(): фон и виньетка конвертируются под экран.
"""
import pygame

from Raycasting.RayCaster import RayCaster
from Raycasting.SpriteDrawer import SpriteDrawer
from UI.Backgrounds import create_background, create_vignette


class Scene:
    def __init__(self) -> None:
        self.background = create_background()
        self.vignette = create_vignette()

    def draw(self, screen: pygame.Surface, player, game_map, textures) -> None:
        screen.blit(self.background, (0, 0))
        RayCaster.cast_rays(screen, player, game_map, textures)
        screen.blit(self.vignette, (0, 0))
