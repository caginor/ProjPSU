"""Состояние игрока, которое читает интерфейс.

Движение/поворот/коллизии - часть человека 1, и он же решит, в каком модуле жить
Player'у. Здесь только те поля, без которых не запустится HUD: инвентарь, ключи,
наличие противогаза. Как только человек 1 перенесёт своего Player'а сюда, эти три поля
остаться должны как есть - на них завязан InventoryHandler.
"""
import math

import pygame

from Settings.Settings import settings

class Player:
    def __init__(self, x: float = 0.0, y: float = 0.0, angle: float = 0.0) -> None:
        self.x = x
        self.y = y
        self.angle = angle
        self.inventory: set[str] = set()   # 'coal', 'gauze', 'bottle'
        self.keys: set[str] = set()        # 'key_red', 'key_blue'
        self.has_mask: bool = False

    # TODO(человек 1): update/rotate/move и коллизии - поверх этих полей.

    def reset(self) -> None:
        """Состояние на новый заход, иначе инвентарь течёт между партиями."""
        self.inventory.clear()
        self.keys.clear()
        self.has_mask = False

    def update(self, dt: float, game_map) -> None:
        """dt - секунды."""
        keys = pygame.key.get_pressed()
        self._rotate(keys, dt)
        self._move(keys, dt, game_map)

    def _rotate(self, keys, dt: float) -> None:
        speed = settings.player.Rot_speed
        if keys[pygame.K_LEFT] or keys[pygame.K_q]:
            self.angle -= speed * dt
        if keys[pygame.K_RIGHT]:
            self.angle += speed * dt

    def _move(self, keys, dt: float, game_map) -> None:
        sin_a = math.sin(self.angle)
        cos_a = math.cos(self.angle)
        step = settings.player.Speed * dt
        dx, dy = 0.0, 0.0

        if keys[pygame.K_w] or keys[pygame.K_UP]:        # вперёд
            dx += cos_a * step
            dy += sin_a * step
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:      # назад
            dx -= cos_a * step
            dy -= sin_a * step
        if keys[pygame.K_a]:                             # шаг влево
            dx += sin_a * step
            dy -= cos_a * step
        if keys[pygame.K_d]:                             # шаг вправо
            dx -= sin_a * step
            dy += cos_a * step

        # По осям отдельно, чтобы скользить вдоль стен
        if not self.hits_wall(self.x + dx, self.y, game_map):
            self.x += dx
        if not self.hits_wall(self.x, self.y + dy, game_map):
            self.y += dy

    def hits_wall(self, x: float, y: float, game_map) -> bool:
        """Хитбокс - четыре точки на расстоянии radius: углы стен больше не срезаются."""
        radius = settings.player.Radius
        points = ((x + radius, y), (x - radius, y), (x, y + radius), (x, y - radius))
        return any(game_map.is_blocked(point_x, point_y) for point_x, point_y in points)