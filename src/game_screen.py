import pygame
import random

from constants import *
import helpers
import engine
import shell
import data_manager



class GameOver(Exception):
    pass



class GameScreen:
    def __init__(self, username):
        self._rows = 13
        self._cols = 6
        self._cell_size = 0.9 / self._rows
        self._board_width = self._cell_size * self._cols
        self._board_height = self._cell_size * self._rows
        self._surface = pygame.display.get_surface()

        self._username = username

        self._state = engine.GameState(self._rows, self._cols)

        self._tick_count = 0
        self._normal_tick_interval = INITIAL_TICK_INTERVAL
        self._current_tick_interval = INITIAL_TICK_INTERVAL

        self._frame_count = 0
        self._level = 1

        self._show_matches = True

        self._next_faller = self._create_random_faller()

        self._draw()

    def _create_random_faller(self) -> engine.Faller:
        '''Creates and spawns a new faller with random jewels in a valid column'''
        game = self._state
        board = game.board()

        num_col_filled = 0
        while True:
            col = random.randint(1, self._cols)
            if board[0][col - 1].jewel is None:
                break
            else:
                num_col_filled += 1
                
                # when all the columns are filled, sets 'col' to an arbitrary number and let the game mechanics handle the error/gameover sequence
                if num_col_filled == game.columns():
                    col = 1
                    break
            
        convert = {'0': 'R',
                   '1': 'O',
                   '2': 'Y',
                   '3': 'G',
                   '4': 'B',
                   '5': 'P',
                   '6': 'W'}
        jewels = []
        for _ in range(3):
            rand = str(random.randint(0, 4))
            jewels.append(convert[rand])

        faller = engine.Faller(col, jewels)

        return faller
        
    def display(self) -> None:
        pygame.display.flip()

    def _draw(self) -> None:
        '''Redraws the entire game screen and update the display'''
        surface = self._surface

        surface.fill(BACKGROUND_COLOR)

        self._draw_next_faller_view()
        self._draw_current_score()
        self._draw_total_score()
        self._draw_time_label()
        self._draw_time()
        self._draw_level()
        self._draw_username()
        self._draw_leaderboard()
        self._draw_board()

    def _str_to_color(self, color: str) -> pygame.Color:
        '''Converts a jewel character code to its corresponding pygame Color'''
        convert = {'R': pygame.Color(250, 90, 90),
                   'O': pygame.Color(250, 160, 90),
                   'Y': pygame.Color(250, 220, 90),
                   'G': pygame.Color(60, 140, 60),
                   'B': pygame.Color(90, 145, 210),
                   'P': pygame.Color(110, 75, 200),
                   'W': pygame.Color(200, 200, 200)}
        
        return convert[color]
    
    def _draw_board(self) -> None:
        '''Renders the game board and its jewels, optionally hiding matched cells during blinking'''
        surface = self._surface
        
        rows = self._rows
        cols = self._cols
        cell_size = self._cell_size
        board_width = self._board_width
        board_height = self._board_height

        left = 0.5 - board_width / 2
        top = 0.5 - board_height / 2

        winw, winh = surface.get_size()

        board_rect = pygame.Rect(winw * left, winh * top, winw * board_width, winh * board_height)
        pygame.draw.rect(surface, BOARD_COLOR, board_rect)

        board = self._state.board()
        # shell.display_board(self._state)
        for r in range(rows):
            for c in range(cols):
                x = left + c * cell_size
                y = top + r * cell_size
                cell_rect = pygame.Rect(winw * x, winh * y, winw * cell_size, winh * cell_size)

                pygame.draw.rect(surface, CELL_BORDER_COLOR, cell_rect, width=1)

                cell = board[r][c]

                if not self._show_matches and cell.state == 4:   # match
                    continue

                if cell.jewel is not None:
                    jewel_color = self._str_to_color(cell.jewel)
                    pygame.draw.ellipse(surface, jewel_color, cell_rect)

                if cell.state == 2:    # landed
                    pygame.draw.ellipse(surface, LANDED_COLOR, cell_rect, width=3)

    def _draw_next_faller_view(self) -> None:
        surface = self._surface

        cell_size = self._cell_size
        board_width, board_height = self._board_width, self._board_height

        left = (0.5 - board_width / 2) - (3/2 * cell_size)
        top = 0.5 - board_height / 2
        
        winw, winh = surface.get_size()

        view_rect = pygame.Rect(winw * left, winh * top, winw * cell_size, winh * (3 * cell_size))
        pygame.draw.rect(surface, BOARD_COLOR, view_rect)

        next_faller = self._next_faller
        for n in range(3):
            x = left
            y = top + n * cell_size
            cell_rect = pygame.Rect(winw * x, winh * y, winw * cell_size, winh * cell_size)

            pygame.draw.rect(surface, CELL_BORDER_COLOR, cell_rect, width=1)

            jewel_color = self._str_to_color(next_faller.get_jewel(n).jewel)
            pygame.draw.ellipse(surface, jewel_color, cell_rect)
    
    def _draw_current_score(self) -> None:
        game = self._state
        surface = self._surface
        
        cell_size = self._cell_size
        board_width, board_height = self._board_width, self._board_height

        left = (0.5 - board_width / 2) - (3 * cell_size)
        top = (0.5 - board_height / 2) + (7/2 * cell_size)
        
        winw, winh = surface.get_size()

        rect = pygame.Rect(winw * left, winh * top, winw * (5/2 * cell_size), winh * cell_size)
        pygame.draw.rect(surface, BOARD_COLOR, rect)

        current_score = game.current_points()

        if current_score > 0:
            font = pygame.font.Font(MICRO_FONT, int(winh * (cell_size * 1.5)))
            text = font.render(str(current_score), True, FONT_COLOR)

            text_rect = text.get_rect()
            text_rect.right = rect.right
            text_rect.centery = rect.centery

            surface.blit(text, text_rect)

    def _draw_text(self, left: float, top: float, text: str, width: float = None, align_right: bool = False, draw_bounding_rect: bool = False) -> None:
        surface = self._surface
        winw, winh = surface.get_size()
        
        cell_size = self._cell_size

        if width is None:
            width = 2 * cell_size
        
        bounding_rect = pygame.Rect(winw * left, winh * top, winw * width, winh * (1/2 * cell_size))
        if draw_bounding_rect:
            pygame.draw.rect(surface, BOARD_COLOR, bounding_rect)

        font = pygame.font.Font(MICRO_FONT, int(winh * (5/8 * cell_size)))
        font_text = font.render(text, True, FONT_COLOR)

        text_rect = font_text.get_rect()

        text_rect.centery = bounding_rect.centery
        if align_right:
            text_rect.right = bounding_rect.right - (0.005 * winw)
        else:
            text_rect.left = bounding_rect.left + (0.005 * winw)
            
        surface.blit(font_text, text_rect)

    def _draw_total_score(self) -> None:
        game = self._state
        
        cell_size = self._cell_size
        board_width, board_height = self._board_width, self._board_height

        left = (0.5 - board_width / 2) - (5/2 * cell_size)
        label_top = (0.5 - board_height / 2) + (5 * cell_size)
        score_top = label_top + (1/2 * cell_size)

        self._draw_text(left, label_top, 'SCORE', align_right=True)

        total_score = game.total_points()
        self._draw_text(left, score_top, str(total_score), align_right=True, draw_bounding_rect=True)

    def _draw_time_label(self) -> None:
        
        left = (0.5 - self._board_width / 2) - (5/2 * self._cell_size)
        top = (0.5 - self._board_height / 2) + (13/2 * self._cell_size)

        self._draw_text(left, top, 'TIME', align_right=True)

    def _draw_time(self) -> None:
        cell_size = self._cell_size
        board_width, board_height = self._board_width, self._board_height

        left = (0.5 - board_width / 2) - (5/2 * cell_size)
        top = (0.5 - board_height / 2) + (7 * cell_size)

        self._draw_text(left, top, helpers._frames_to_str(self._frame_count), align_right=True, draw_bounding_rect=True)
    
    def _draw_level(self) -> None:
        cell_size = self._cell_size
        board_width, board_height = self._board_width, self._board_height

        left = (0.5 - board_width / 2) - (5/2 * cell_size)
        label_top = (0.5 - board_height / 2) + (8 * cell_size)
        level_top = label_top + (1/2 * cell_size)

        self._draw_text(left, label_top, 'LEVEL', align_right=True)
        self._draw_text(left, level_top, str(self._level), align_right=True, draw_bounding_rect=True)

    def _draw_username(self) -> None:
        cell_size = self._cell_size
        board_width, board_height = self._board_width, self._board_height

        left = (0.5 + board_width / 2) + (1/2 * cell_size)
        label_top = 0.5 - board_height / 2
        
        if self._username:
            label_text_str = 'USERNAME'

            user_top = label_top + (1/2 * cell_size)

            self._draw_text(left, user_top, self._username, draw_bounding_rect=True)

        else:
            label_text_str = 'PRACTICE ROUND'

        self._draw_text(left, label_top, label_text_str)

    def _draw_leaderboard(self) -> None:
        cell_size = self._cell_size
        board_width, board_height = self._board_width, self._board_height

        left = (0.5 + board_width / 2) + (1/2 * cell_size)
        label_top = (0.5 - board_height / 2) + (3/2 * cell_size)

        self._draw_text(left, label_top, 'LEADERBOARD')

        scores = data_manager.get_leaderboard()

        row_height = 0.05
        rank_w = 0.5 * cell_size
        name_w = 2 * cell_size
        score_w = 1 * cell_size

        for i, entry in enumerate(scores):
            y = label_top + (1/2 * cell_size) + (i * row_height)

            rank_text = f'{entry['placement']}.'
            self._draw_text(left, y, rank_text, width=rank_w)

            self._draw_text(left + rank_w, y, entry['username'], width=name_w)

            score_text = str(entry['score'])
            self._draw_text(left + rank_w + name_w, y, score_text, align_right=True, width=score_w)



        
    def handle_events(self, events: list[pygame.event.Event]) -> None:
        for event in events:
            if event.type == pygame.KEYDOWN:
                game = self._state

                def safe_call(func) -> None:
                    try:
                        func()
                        if game.faller() is not None and game.faller().state() == 2:
                            self._tick_count = 0
                    except engine.IllegalAction as e:
                        print(e)
                    finally:
                        self._draw()
                        pygame.display.flip()

                if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                    safe_call(game.move_faller_left)
                elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                    safe_call(game.move_faller_right)
                elif event.key == pygame.K_UP or event.key == pygame.K_w:
                    safe_call(game.rotate_faller)
                elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                    if game.faller() is not None and game.faller().state() == 1 and game.has_match() is False:
                        self._current_tick_interval = FAST_TICK_INTERVAL
            
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_DOWN or event.key == pygame.K_s:
                    self._current_tick_interval = self._normal_tick_interval

    def update(self) -> None:
        self._tick_count += 1
        self._frame_count += 1

        self._draw_time()

        self._level = (self._frame_count // 900) + 1
        self._normal_tick_interval = max(MIN_NORMAL_TICK_INTERVAL, int(INITIAL_TICK_INTERVAL * (0.95)**(self._level - 1)))
        
        game = self._state
        if game.has_match():
            self._draw_board()
            self._show_matches = not self._show_matches
            tick_interval = self._normal_tick_interval
        else:
            tick_interval = self._current_tick_interval

        if self._tick_count >= tick_interval:
            self._tick_count = 0

            # if there is an active faller or if there is a match
            if game.faller() is not None or game.has_match() is True:
                game.tick()
                self._show_matches = True
            else:
                game.spawn_faller(self._next_faller)
                self._next_faller = self._create_random_faller()
            
            self._draw()
        
        if game.game_over():
            raise GameOver()

    def final_score_time_level(self) -> tuple[int, int, int]:
        return self._state.total_points(), self._frame_count, self._level