import pygame
import columns
import shell
import random

class ResetTickCount(Exception):
    pass

_INITIAL_SIZE = (700, 700)
_FRAME_RATE = 30

_BACKGROUND_COLOR = pygame.Color(20, 20, 20)
_BOARD_COLOR = pygame.Color(0, 0 , 0)
_CELL_BORDER_COLOR = pygame.Color(40, 40, 40)
_LANDED_COLOR = pygame.Color(255, 255, 255)


class ColumnsGame:
    def __init__(self):
        self._rows = 13
        self._cols = 6
        self._cell_size = 0.9 / self._rows
        self._board_width = self._cell_size * self._cols
        self._board_height = self._cell_size * self._rows

        self._running = True
        self._state = columns.GameState(self._rows, self._cols)

        self._next_faller = self._create_random_faller()

    def run(self) -> None:
        pygame.init()

        try:
            self._resize_surface(_INITIAL_SIZE)

            clock = pygame.time.Clock()

            game = self._state

            self._display_screen()

            tick_count = 0
            show_matches = True
            while self._running:
                clock.tick(_FRAME_RATE)
                tick_count += 1

                try:
                    self._handle_events()
                except ResetTickCount:
                    tick_count = 0

                if game.has_match():
                    self._draw_board(show_matches=show_matches)
                    pygame.display.flip()
                    show_matches = not show_matches

                if tick_count == 15:
                    tick_count = 0
                    
                    # if there is an active faller or if there is a match
                    if game.faller() is not None or game.has_match() is True:
                        game.tick()
                        show_matches = True
                    else:
                        game.spawn_faller(self._next_faller)
                        self._next_faller = self._create_random_faller()
                        
                    self._display_screen()

                if game.game_over():
                    self._running = False

        finally:
            pygame.quit()

    def _resize_surface(self, size: tuple[int, int]) -> None:
        '''Resizes the game window to the given size.'''
        pygame.display.set_mode(size, pygame.RESIZABLE)

    def _display_screen(self) -> None:
        '''Redraws the entire game screen and update the display'''
        surface = pygame.display.get_surface()

        surface.fill(_BACKGROUND_COLOR)

        self._draw_next_faller_view()
        self._draw_board()

        pygame.display.flip()

    def _draw_board(self, show_matches=False) -> None:
        '''Renders the game board and its jewels, optionally hiding matched cells during blinking'''
        surface = pygame.display.get_surface()
        
        rows = self._rows
        cols = self._cols
        cell_size = self._cell_size
        board_width = self._board_width
        board_height = self._board_height

        left = 0.5 - board_width / 2
        top = 0.5 - board_height / 2

        winw, winh = surface.get_size()

        board_rect = pygame.Rect(winw * left, winh * top, winw * board_width, winh * board_height)
        pygame.draw.rect(surface, _BOARD_COLOR, board_rect)

        board = self._state.board()
        shell.display_board(self._state)
        for r in range(rows):
            for c in range(cols):
                x = left + c * cell_size
                y = top + r * cell_size
                cell_rect = pygame.Rect(winw * x, winh * y, winw * cell_size, winh * cell_size)

                pygame.draw.rect(surface, _CELL_BORDER_COLOR, cell_rect, width=1)

                cell = board[r][c]

                if not show_matches and cell.state == 4:   # match
                    continue

                if cell.jewel is not None:
                    jewel_color = self._str_to_color(cell.jewel)
                    pygame.draw.ellipse(surface, jewel_color, cell_rect)

                if cell.state == 2:    # landed
                    pygame.draw.ellipse(surface, _LANDED_COLOR, cell_rect, width=3)

    def _draw_next_faller_view(self) -> None:
        surface = pygame.display.get_surface()

        cell_size = self._cell_size
        board_width, board_height = self._board_width, self._board_height

        left = (0.5 - board_width / 2) - (3/2 * cell_size)
        top = 0.5 - board_height / 2
        
        winw, winh = surface.get_size()

        view_rect = pygame.Rect(winw * left, winh * top, winw * cell_size, winh * (3 * cell_size))
        pygame.draw.rect(surface, _BOARD_COLOR, view_rect)

        next_faller = self._next_faller
        for n in range(3):
            x = left
            y = top + n * cell_size
            cell_rect = pygame.Rect(winw * x, winh * y, winw * cell_size, winh * cell_size)

            pygame.draw.rect(surface, _CELL_BORDER_COLOR, cell_rect, width=1)

            jewel_color = self._str_to_color(next_faller.get_jewel(n).jewel)
            pygame.draw.ellipse(surface, jewel_color, cell_rect)



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

    def _handle_events(self) -> None:
        '''Processes all pending pygame events and apply user inputs to game actions'''
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._running = False
            elif event.type == pygame.VIDEORESIZE:
                self._resize_surface(event.size)
                self._display_screen()
            elif event.type == pygame.KEYDOWN:
                game = self._state
                if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                    try:
                        game.move_faller_left()
                    except columns.IllegalAction as e:
                        print(e)
                elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                    try:
                        game.move_faller_right()
                    except columns.IllegalAction as e:
                        print(e)
                elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                    game = self._state
                    if game.faller() is not None and game.faller().state() == 1 and game.has_match() is False:
                        while True:
                            game.tick()
                            self._display_screen()
                            if game.faller().state() == 2:
                                break
                        game.tick()
                        raise ResetTickCount()
                elif event.key == pygame.K_SPACE:
                    try:
                        game.rotate_faller()
                    except columns.IllegalAction as e:
                        print(e)
                self._display_screen()

    def _create_random_faller(self) -> columns.Faller:
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

        faller = columns.Faller(col, jewels)

        return faller

if __name__ == '__main__':
    ColumnsGame().run()