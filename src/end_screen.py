import pygame

from constants import *
import helpers

class EndGame(Exception):
    pass

class RestartGame(Exception):
    pass

class EndScreen():
    def __init__(self, username: str, score: int, time: int, level: int):
        self._username = username
        self._score = score
        # time is stored in frames
        self._time = time
        self._level = level

        self._surface = pygame.display.get_surface()

    def handle_events(self, events: list[pygame.event.Event]) -> None:
        pass

    def update(self) -> None:
        pass

    def display(self) -> None:
        self._surface.fill(BACKGROUND_COLOR)

        self._draw_game_over()

        pygame.display.flip()

    def _draw_text(self, top: float, text_str: str, font_size: float, font_style: str = MICRO_FONT, font_color: pygame.Color = FONT_COLOR) -> None:
        surface = self._surface
        winw, winh = surface.get_size()

        font = pygame.font.Font(font_style, int(font_size * winh))
        text = font.render(text_str, True, font_color)

        text_rect = text.get_rect()
        text_rect.centerx = 0.5 * winw
        text_rect.top = top * winh

        surface.blit(text, text_rect)

    def _draw_game_over(self):
        self._draw_text(0.05, 'GAME OVER', 0.2)
        self._draw_text(0.2, f'SCORE: {self._score}   TIME: {helpers._frames_to_str(self._time)}   LEVEL: {self._level}', 0.075)
