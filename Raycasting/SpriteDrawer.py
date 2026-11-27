"""Предметы и ключи в 3D-виде (вместо кружков из game.py).

Предмет - словарь из карты: {"x", "y", "id", "type", "collected"}; картинка берётся из
textures[item["id"]]. Здесь только проекция на экран: угол к предмету -> колонка,
расстояние -> размер и яркость (туман), z_buffer -> закрыт ли предмет стеной.
"""
import math

import pygame

from Settings.Settings import settings
from UI.Backgrounds import get_shade


class SpriteDrawer:
    @staticmethod
    def draw_sprites(
        screen: pygame.Surface,
        player,
        items: list[dict],
        z_buffer: list[float],
        textures: dict[str, pygame.Surface],
    ) -> None:
        rays = settings.raycasting
        width = settings.screen.Width
        game_height = settings.screen.Game_height

        visible = [item for item in items if not item["collected"]]
        visible.sort(key=lambda i: -((i["x"] - player.x) ** 2 + (i["y"] - player.y) ** 2))   # дальние первыми

        for item in visible:
            image = textures.get(item["id"])
            if image is None:
                continue

            dx = item["x"] - player.x
            dy = item["y"] - player.y

            # угол между взглядом игрока и предметом, в диапазоне -pi..pi
            delta = math.atan2(dy, dx) - player.angle
            delta = (delta + math.pi) % (2 * math.pi) - math.pi
            if abs(delta) > rays.Half_fov + 0.1:
                continue

            depth = math.hypot(dx, dy) * math.cos(delta)
            if depth < 0.1:
                continue

            # закрыт стеной - не рисуем
            screen_x = int((delta / rays.Fov + 0.5) * width)
            ray = max(0, min(rays.Num_rays - 1, screen_x // rays.Ray_width))
            if depth > z_buffer[ray]:
                continue

            shade = get_shade(depth)
            if shade < 0.01:                     # в темноте предмета не видно
                continue

            wall_height = rays.Walls_height / depth
            size = max(1, min(int(wall_height * rays.Sprite_scale), game_height))
            floor_y = settings.screen.Half_of_game_height + int(wall_height / 2)   # предмет стоит на полу

            scaled = pygame.transform.scale(image, (size, size))
            channel = int(255 * shade)
            scaled.fill((channel, channel, channel, 255), special_flags=pygame.BLEND_RGBA_MULT)
            screen.blit(scaled, (screen_x - size // 2, floor_y - size))
