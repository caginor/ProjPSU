"""Рейкастинг: лучи (DDA) и отрисовка колонок стен.

Заменил пошаговый перебор из game.py (шаг 0.03, цветные прямоугольники): луч идёт ровно
по линиям сетки, а стена рисуется текстурой.
  * карту читаем через game_map.get_tile(x, y) и Models.Tiles - рендер не знает про уровни;
  * туман - get_shade из UI.Backgrounds: один на стены, пол и потолок;
  * колонка считается по дробным координатам (верх и высота округляются один раз, в конце):
    целочисленная обрезка текстуры давала бы "лесенку" на стенах вблизи.
"""
import math

import pygame

from Models.Tiles import TILE_TEXTURES, Tile
from Settings.Settings import settings
from UI.Backgrounds import get_shade


class RayCaster:
    MIN_DEPTH = 0.1     # ближе стену не рисуем: иначе колонка раздувается до огромных размеров

    @staticmethod
    def cast_ray(player, game_map, angle: float) -> tuple[float, int, float, int]:
        """Один луч (алгоритм DDA).
        Возвращает: (расстояние, тип клетки, позиция на стене 0..1, сторона 0/1)."""
        sin_a = math.sin(angle)
        cos_a = math.cos(angle)
        if abs(sin_a) < 1e-6:        # защита от деления на ноль
            sin_a = 1e-6
        if abs(cos_a) < 1e-6:
            cos_a = 1e-6

        px, py = player.x, player.y
        map_x, map_y = int(px), int(py)

        delta_x = abs(1 / cos_a)     # длина луча между соседними линиями сетки
        delta_y = abs(1 / sin_a)

        if cos_a > 0:
            step_x, side_x = 1, (map_x + 1 - px) * delta_x
        else:
            step_x, side_x = -1, (px - map_x) * delta_x
        if sin_a > 0:
            step_y, side_y = 1, (map_y + 1 - py) * delta_y
        else:
            step_y, side_y = -1, (py - map_y) * delta_y

        while True:                  # идём по сетке, пока не упрёмся в твёрдую клетку
            if side_x < side_y:
                depth = side_x
                side_x += delta_x
                map_x += step_x
                side = 0
            else:
                depth = side_y
                side_y += delta_y
                map_y += step_y
                side = 1

            tile = game_map.get_tile(map_x, map_y)      # за краем карты - стена
            if tile != Tile.Floor:
                break

        # в какое место стены попали (0..1) - из этого берётся колонка текстуры
        if side == 0:
            wall_x = py + depth * sin_a
            flip = cos_a > 0
        else:
            wall_x = px + depth * cos_a
            flip = sin_a < 0
        wall_x -= math.floor(wall_x)
        if flip:
            wall_x = 1 - wall_x

        return depth, tile, wall_x, side

    @staticmethod
    def draw_wall_column(
        screen: pygame.Surface, texture: pygame.Surface, x: int, depth: float, wall_x: float, side: int
    ) -> None:
        rays = settings.raycasting
        wall_height = rays.Walls_height / depth                      # дробная высота стены
        top = settings.screen.Half_of_game_height - wall_height / 2  # дробный верх стены

        shade = get_shade(depth)                                     # туман; боковые стены темнее
        if side == 1:
            shade *= 0.7

        if shade < 0.01:                                             # слишком далеко: чёрная колонка
            pygame.draw.rect(screen, (0, 0, 0), (x, int(top), rays.Ray_width, int(wall_height) + 1))
            return

        tex_w, tex_h = texture.get_size()
        tex_x = min(int(wall_x * tex_w), tex_w - 1)
        scale = wall_height / tex_h                                  # пикселей экрана на пиксель текстуры

        # какие строки текстуры вообще попадают на экран
        src_top = max(0, int(-top / scale))
        src_bottom = min(tex_h, int((settings.screen.Game_height - top) / scale) + 1)
        src_bottom = max(src_bottom, src_top + 1)

        # положение и высота - по той же дробной формуле: границы пикселей текстуры
        # у соседних колонок ложатся на одну линию
        dest_top = round(top + src_top * scale)
        dest_bottom = round(top + src_bottom * scale)
        dest_height = max(1, dest_bottom - dest_top)

        column = texture.subsurface(pygame.Rect(tex_x, src_top, 1, src_bottom - src_top))
        column = pygame.transform.scale(column, (rays.Ray_width, dest_height))

        if shade < 0.99:
            channel = int(255 * shade)
            column.fill((channel, channel, channel), special_flags=pygame.BLEND_MULT)

        screen.blit(column, (x, dest_top))                           # лишнее обрежет set_clip

    @staticmethod
    def cast_rays(
        screen: pygame.Surface, player, game_map, textures: dict[str, pygame.Surface]
    ) -> list[float]:
        """Рисует все стены. Возвращает z_buffer: расстояние до стены для каждой колонки."""
        rays = settings.raycasting
        z_buffer: list[float] = []
        start_angle = player.angle - rays.Half_fov

        screen.set_clip((0, 0, settings.screen.Width, settings.screen.Game_height))  # не залезаем на HUD
        for ray in range(rays.Num_rays):
            angle = start_angle + ray * rays.Delta_angle
            depth, tile, wall_x, side = RayCaster.cast_ray(player, game_map, angle)

            depth *= math.cos(angle - player.angle)                  # убираем "рыбий глаз"
            depth = max(depth, RayCaster.MIN_DEPTH)

            texture = textures[TILE_TEXTURES[tile]]
            RayCaster.draw_wall_column(screen, texture, ray * rays.Ray_width, depth, wall_x, side)
            z_buffer.append(depth)
        screen.set_clip(None)

        return z_buffer
