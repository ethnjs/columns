import pygame

from constants import *

class StartGame(Exception):
    def __init__(self, username: str):
        self.username = username

class StartScreen():
    def __init__(self):
        self._surface = pygame.display.get_surface()

        # STATES
        #   0 -> Press ENTER to Start
        #   1 -> Enter your username
        #   2 -> If no username is entered, ask if user wants to play practice round
        #   3 -> If username already exists, ask if user wants to continue 
        #   4 -> Start Game
        self._state = 0

        self._username_text = ''

        self._yes_no = True

    def display(self) -> None:
        self._surface.fill(BACKGROUND_COLOR)

        self._draw_title()

        state_methods = {
            0: self._draw_enter_to_start,
            1: self._draw_username_input,
            2: self._draw_practice_round_yes_no,
            3: self._draw_username_exists_continue_yes_no
        }

        method = state_methods.get(self._state)
        if method:
            method()

        pygame.display.flip()

    def _draw_text(self, top: float, text_str: str, font_size: float, font_style: str = MICRO_FONT, font_color: pygame.Color = FONT_COLOR) -> None:
        surface = self._surface
        winw, winh = surface.get_size()

        font = pygame.font.Font(font_style, int(font_size * winh))
        text = font.render(text_str, True, font_color)

        text_rect = text.get_rect()
        text_rect.centerx = winw / 2
        text_rect.top = top * winh

        surface.blit(text, text_rect)

    def _draw_title(self) -> None:
        self._draw_text(0.1, 'COLUMNS', 0.3)

    def _draw_enter_to_start(self) -> None:
        self._draw_text(0.5, 'PRESS [ENTER] TO START', 0.1)

    def _draw_username_input(self) -> None:
        self._draw_text(0.5, 'ENTER USERNAME:', 0.075)

        display_text = self._username_text + '_'
        self._draw_text(0.575, display_text, 0.1)
    
    def _draw_yes_no(self, top: float, font_size: float, font_style: str = MICRO_FONT, font_color: pygame.Color = FONT_COLOR) -> None:
        options = ['YES', 'NO']
        for i, text in enumerate(options):
            offset = -0.15 if i == 0 else 0.15
            is_selected = (i == 0 and self._yes_no) or (i == 1 and not self._yes_no)

            self._draw_option(top, offset, is_selected, text, font_size, font_style=font_style, font_color=font_color)
    
    def _draw_option(self, top: float, offset: float, is_selected: bool, text_str: str, font_size: float, font_style: str = MICRO_FONT, font_color: pygame.Color = FONT_COLOR) -> None:
        surface = self._surface
        winw, winh = surface.get_size()

        font = pygame.font.Font(font_style, int(font_size * winh))
        
        display_str = f'> {text_str} <' if is_selected else text_str

        text = font.render(display_str, True, font_color)
        
        text_rect = text.get_rect()
        text_rect.centerx = (winw / 2) + (offset * winw)
        text_rect.top = top * winh

        surface.blit(text, text_rect)

    def _draw_practice_round_yes_no(self) -> None:
        self._draw_text(0.5, 'NO USERNAME ENTERED!', 0.05)
        self._draw_text(0.55, 'Do you want to play a practice round?', 0.05)

        self._draw_yes_no(0.6, 0.1)

    def _draw_username_exists_continue_yes_no(self) -> None:
        self._draw_text(0.5, 'USERNAME EXISTS ALREADY!', 0.05)
        self._draw_text(0.55, f'Would you like to continue as {self._username_text}', 0.04)

        self._draw_yes_no(0.6, 0.1)

    def handle_events(self, events: list[pygame.event.Event]) -> None:
        state_methods = {
            0: self._state0_events,
            1: self._state1_events,
            2: self._state2_3_events,
            3: self._state2_3_events
        }

        method = state_methods.get(self._state)
        if method:
            method(events)

    def _state0_events(self, events: list[pygame.event.Event]) -> None:
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    self._state = 1
    
    def _state1_events(self, events: list[pygame.event.Event]) -> None:
        for event in events:
            if event.type == pygame.KEYDOWN:
                accepted_chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
                if event.unicode.upper() in accepted_chars:
                    self._username_text += event.unicode.lower()
                elif event.key == pygame.K_BACKSPACE and len(self._username_text) > 0:
                    self._username_text = self._username_text[:-1]
                elif event.key == pygame.K_RETURN:
                    if not self._username_text:
                        self._yes_no = True
                        self._state = 2
                    else:
                        self._yes_no = False
                        self._state = 3

    def _state2_3_events(self, events: list[pygame.event.Event]) -> None:
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    self._yes_no = True
                elif event.key == pygame.K_RIGHT:
                    self._yes_no = False
                elif event.key == pygame.K_RETURN:
                    if self._yes_no:
                        self._state = 4
                    else:
                        self._state = 1

    def update(self) -> None:
        if self._state == 4:
            raise StartGame(self._username_text) 
