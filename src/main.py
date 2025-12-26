import pygame
from constants import *
from start_screen import StartScreen, StartGame
from game_screen import GameScreen, GameOver
from end_screen import EndScreen, EndGame, RestartGame
import data_manager



class ColumnsGame():
    def __init__(self):
        self._running = True

        self._resize_surface(INITIAL_SIZE)
        self._active_screen = StartScreen()

        self._current_user = None

    def run(self):
        pygame.init()

        try:
            clock = pygame.time.Clock()

            self._active_screen.display()

            while self._running:
                clock.tick(FRAME_RATE)

                events = pygame.event.get()
                for e in events:
                    if e.type == pygame.QUIT:
                        self._running = False
                    elif e.type == pygame.VIDEORESIZE:
                        self._resize_surface(e.size)
                        self._active_screen.display()
                
                try:
                    self._active_screen.handle_events(events)

                    self._active_screen.update()

                    self._active_screen.display()

                except StartGame as e:
                    self._current_user = e.username
                    self._active_screen = GameScreen(self._current_user)
                    self._active_screen.display()
                except GameOver:
                    score, time, level = self._active_screen.final_score_time_level()
                    username = self._current_user
                    
                    if username:
                        data_manager.save_new_entry(username, score, time, level)

                    self._active_screen = EndScreen(username, score, time, level)
                except EndGame:
                    break
                except RestartGame:
                    self._active_screen = StartScreen()
                    self._current_user = None

        finally:
            pygame.quit()

    def _resize_surface(self, size: tuple[int, int]) -> None:
        '''Resizes the game window to the given size.'''
        pygame.display.set_mode(size, pygame.RESIZABLE)

if __name__ == '__main__':
    ColumnsGame().run()