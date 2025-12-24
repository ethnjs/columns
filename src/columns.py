from dataclasses import dataclass



# Raised when the board is created with an invalid number of rows
class InvalidBoardRows(Exception):
    pass

# Raised when the board is created with an invalid number of columns
class InvalidBoardColumns(Exception):
    pass

# Raised when the initial field data does not match the board size
class InvalidInitialFieldDimensions(Exception):
    pass

# Raised when a game action is not allowed in the current state
class IllegalAction(Exception):
    pass

# Raised when a faller is created or used with invalid parameters
class InvalidFaller(Exception):
    pass



@dataclass
class Cell:
    state: int   # 0 empty, 1 falling, 2 landed, 3 frozen, 4 matched
    jewel: str | None



class Faller():
    def __init__(self, col: int, jewels: list[str]) -> None:
        self._col = col - 1 
        self._jewels = self._validate_faller(jewels)
        
        # STATES
        #   FALLING = 1
        #   LANDED  = 2
        #   FROZEN  = 3
        self._state = 1
        self._bottom_row = 0

        self._prev_coords = []

    def state(self) -> int:
        return self._state
    
    def bottom_row(self) -> int:
        return self._bottom_row
    
    def col(self) -> int:
        return self._col
    
    def coords(self) -> list[tuple[int, int]]:
        '''Returns the (col, row) coordinates of the faller's three jewels from top to bottom'''
        row = self._bottom_row
        col = self._col
        
        coords = []

        for _ in range(3):
            coords.insert(0, (col, row))
            row -= 1

        return coords
    
    def prev_coords(self) -> list[tuple[int, int]]:
        return self._prev_coords
    
    def update_prev_coords(self) -> None:
        self._prev_coords = self.coords()
    
    def get_jewel(self, n: int) -> Cell:
        '''Returns the nth jewel of the faller as a Cell with the current state'''
        state = self._state
        jewel = self._jewels[n]

        return Cell(state, jewel)
        
    def update_state(self, state: int) -> None:
        self._state = state

    def move_down(self) -> None:
        self._bottom_row += 1

    def rotate(self) -> None:
        self._must_not_be_frozen('rotate')

        jewels = self._jewels
        jewels.insert(0, jewels[2])
        del jewels[3]

    def move_left(self) -> None:
        self._must_not_be_frozen('move')

        self._col -= 1
        self._state = 1

    def move_right(self) -> None:
        self._must_not_be_frozen('move')

        self._col += 1
        self._state = 1

    def _validate_faller(self, jewels: list[str]) -> list[str]:
        '''Ensures the faller has exactly three one-character jewels; raise InvalidFaller otherwise'''
        if len(jewels) != 3:
            raise InvalidFaller(f'Expecting 3 jewels in the faller, received {len(jewels)}')
        
        for i, jewel in enumerate(jewels):
            if len(jewel) != 1:
                raise InvalidFaller(f'Jewel #{i + 1} in the faller has {len(jewel)} characters, expecting 1')
            
        return jewels
    
    def _must_not_be_frozen(self, action: str) -> None:
        '''Raises IllegalAction if attempting the given action while the faller is frozen'''
        if self._state == 3:
            raise IllegalAction(f'Cannot {action} a frozen faller.')
        


class GameState():
    def __init__(self, rows: int, columns: int) -> None:
        # true number of rows and columns
        self._rows = rows
        self._columns = columns
        
        # the game board is stored as a column-major 2D list of Cells
        self._board = self._create_empty_game_board()

        self._faller = None

        self._matches = set()
        self._matches_count = 0
        self._has_match = False

        self._turn_num = 1
        self._total_points = 0
        # adds to total points and resets after every new faller
        self._current_points = 0

        self._game_over = False

    def _create_empty_game_board(self) -> list[list[Cell]]:
        '''Returns a new empty board; raises an error if row/column counts are invalid'''
        rows = self._rows
        cols = self._columns
        
        if rows < 4:
            raise InvalidBoardRows(f'Board must have at least 4 rows, but {rows} were provided.')
        if cols < 3:
            raise InvalidBoardColumns(f'Board must have at least 3 columns, but {cols} were provided.')
        
        board = [[Cell(0, None) for _ in range(rows)] for _ in range(cols)]
        
        return board

    def rows(self) -> int:
        return self._rows
    
    def columns(self) -> int:
        return self._columns
    
    def board(self) -> list[list[Cell]]:
        '''Returns the board as a row-major 2D list of Cells'''
        rows = self._rows
        cols = self._columns
        row_board = [[self._board[c][r] for c in range(cols)] for r in range(rows)]
        return list(row_board)
    
    def load(self, data: list[str]) -> None:
        '''Loads initial field data, apply gravity, and mark any initial matches'''
        self._load(data)

        self._apply_gravity()

        self._find_and_mark_matches()

    def _load(self, data: list[str]) -> None:
        '''Populates the board using raw input lines; spaces create empty cells'''
        self._validate_initial_field_data(data)
        
        jewels = [[char for char in line] for line in data]

        for r in range(self._rows):
            for c in range(self._columns):
                jewel = jewels[r][c]
                if jewel != ' ':
                    self._board[c][r] = Cell(3, jewel)
                else:
                    self._board[c][r] = Cell(0, None)

    def _validate_initial_field_data(self, data) -> None:
        '''Ensures initial field data matches the board's expected dimensions'''
        if len(data) != self._rows:
            raise InvalidInitialFieldDimensions(f'Expected {self._rows} rows, got {len(data)}')
        
        for r, line in enumerate(data):
            if len(line) != self._columns:
                raise InvalidInitialFieldDimensions(f'Row {r + 1} expected {self._columns} columns, got {len(line)}')

    def spawn_faller(self, faller: Faller) -> None:
        '''Spawns a new faller in the given column; raises an error if illegal or space is blocked'''
        col = faller.col()

        if self._faller is not None:
            raise IllegalAction('Cannot spawn a new faller when one is still active.')
            
        if self._has_match is True:
            raise IllegalAction('Cannot spawn a new faller when all matches are not cleared.')
        
        if self._board[col][0].jewel is not None:
            self._game_over = True
            raise IllegalAction(f'Cannot spawn faller, column {col + 1} is full')

        self._faller = faller
        self._update_faller_state()
        self._update_board()

        self._total_points += self._current_points
        print(f'Current Points: {self._current_points}')
        print(f'Total Points: {self._total_points}')
        self._current_points = 0
        self._turn_num = 1
    
    def tick(self) -> None:
        '''Advances the game one step: move faller, resolve matches, or freeze as needed'''
        faller = self._faller

        if self._has_match:
            self._clear_matches()
            self._has_match = False

            # calculate current points
            self._current_points += 2**self._turn_num * 100 * self._matches_count
            self._turn_num += 1

            if faller != None:
                offboard = self._check_offboard_frozen_jewels()
                
                if offboard != []:
                    self._resolve_offboard_frozen_jewels(offboard)
                else:
                    # if the matches are now all cleared and there are no more offboard jewels,
                    # faller is now completely frozen and on the board
                    self._faller = None

            self._apply_gravity()
            self._find_and_mark_matches()

            if self._has_match:
                self._game_over = False
            else:
                # catches the special case where there are two offboard frozen jewels and one frozen jewel
                # in a match on the board. after the next tick, there is another match with the second jewel
                # from the bottom of the faller (the first jewel is cleared) and there is still one offboard
                # frozen jewel. this makes sure faller is set to NONE when there is no matches left.
                self._faller = None
            
        elif faller is not None:
            # updates state before movement to detect landing on spawn
            self._update_faller_state()

            # Falling state
            if faller.state() == 1:
                faller.move_down()
                self._update_faller_state()
                
            self._update_board()

            # If the faller is frozen this tick
            if faller.state() == 3:

                self._find_and_mark_matches()

                # if there are matches, handle the matches first
                if self._has_match:
                    return
                else:
                    offboard = self._check_offboard_frozen_jewels()
                    # if there are no matches and there are still offboard frozen jewels -> game over
                    if offboard != []:
                        self._game_over = True
                    
                    # if there are no matches and there is no offboard frozen jewels,
                    # faller is now completely frozen and on the board
                    self._faller = None
        
    def _check_offboard_frozen_jewels(self) -> list[Cell]:
        '''Returns any frozen faller jewels whose coordinates lie above row 0'''
        faller = self._faller

        offboard = [] # only need to handle the column the faller is in

        for n, (_, r) in enumerate(faller.coords()):
            if r < 0:
                cell = faller.get_jewel(n)
                offboard.append(cell)

        return offboard

    def _resolve_offboard_frozen_jewels(self, offboard: list[Cell]) -> None:
        '''Places offboard jewels into the column, adjusts faller position, or triggers game over'''
        rows = self._rows
        cols = self._columns
        board = self._board
        faller = self._faller

        combined = offboard + board[faller.col()]
        jewels = []
        spaces = 0
        for cell in combined:
            if cell.jewel is None:
                spaces += 1
            else:
                jewels.append(cell)

        for _ in range(spaces):
            faller.move_down()

        # if there are more jewels than rows, game over
        if len(jewels) > rows:
            self._game_over = True
            extras = len(jewels) - rows
            new_col = jewels[extras:]
        else:
            empties = rows - len(jewels)
            new_col = [Cell(0, None) for _ in range(empties)] + jewels

        self._board[faller.col()] = new_col
        offboard.clear()

    def rotate_faller(self) -> None:
        '''Rotates the active faller's jewels; raises an error if no faller is active'''
        if self._faller is None:
            raise IllegalAction('Cannot rotate — no active faller.')
            
        self._faller.rotate()
        self._update_board()

    def move_faller_left(self) -> None:
        '''Moves the active faller left if the column is free; raise error otherwise'''
        faller = self._faller
        if self._faller is None:
            raise IllegalAction('Cannot move left — no active faller.')

        left_col = 0
        if faller.col() == left_col:
            raise IllegalAction('Faller is in left-most column, cannot move left.')
        
        board = self._board
        for c, r in faller.coords():
            if r >= 0 and board[c-1][r].jewel is not None:
                raise IllegalAction(f'Cell ({c-1}, {r}) is occupied — cannot move faller left.')
        
        faller.move_left()
        self._update_faller_state()
        self._update_board()
            
    def move_faller_right(self) -> None:
        '''Moves the active faller right if the column is free; raise error otherwise'''
        faller = self._faller
        if self._faller is None:
            raise IllegalAction('Cannot move right — no active faller.')

        right_col = self._columns - 1
        if faller.col() == right_col:
            raise IllegalAction('Faller is in right-most column, cannot move right.')
        
        board = self._board
        for c, r in faller.coords():
            if r >= 0 and board[c+1][r].jewel is not None:
                raise IllegalAction(f'Cell ({c+1}, {r}) is occupied — cannot move faller right.')
        
        faller.move_right()
        self._update_faller_state()
        self._update_board()

    def faller(self) -> Faller | None:
        return self._faller
        
    def has_match(self) -> bool:
        return self._has_match
    
    def current_points(self) -> int:
        return self._current_points
    
    def total_points(self) -> int:
        return self._total_points
    
    def game_over(self) -> bool:
        return self._game_over
    
    def end(self) -> None:
        '''Force the game into game over state'''
        self._game_over = True

    def _apply_gravity(self) -> None:
        '''Lets jewels fall within each column by sliding non-empty cells downward'''
        rows = self._rows
        columns = self._columns
        board = self._board

        for c in range(columns):
            for r in range(rows - 1):
                if board[c][r].jewel is not None and board[c][r+1].jewel is None:
                    del board[c][r+1]
                    board[c].insert(0, Cell(0, None))

    def _find_and_mark_matches(self) -> None:
        '''Finds all matches and marks them; update has_match accordingly'''
        self._find_matches()
        matches = self._matches

        self._has_match = True if matches else False

        self._mark_matches()

    def _find_matches(self) -> None:
        '''Returns a set of coordinates of all jewels forming runs of 3+ in any direction'''
        matches = set()
        count = 0

        rows = self._rows
        columns = self._columns
        board = self._board

        directions = [
            (1, 0), # horizontal
            (0, 1), # vertical
            (1, 1), # diagonal down-right
            (1, -1) # diagonal up-right
        ]

        for c in range(columns):
            for r in range(rows):
                jewel = board[c][r].jewel
                if jewel is None: # skips empty cells
                    continue

                for dx, dy in directions:
                    # skips cell if there is not enough space to make a run of 3
                    if dx == 1 and c > columns - 3:
                        continue # horizontal or diagonal run would go off the board
                    if dy == 1 and r > rows - 3:
                        continue # vertical or diagonal down-right would go off the board
                    if dy == -1 and r < 2:
                        continue # diagonal up-right would go off the board

                    run = [(c, r)]
                    x, y = c + dx, r + dy

                    while 0 <= x < columns and 0 <= y < rows and board[x][y].jewel == jewel:
                        run.append((x, y))
                        x += dx
                        y += dy

                    if len(run) >= 3:
                        matches.update(run)
                        count += 1
        
        self._matches = matches
        self._matches_count = count
    
    def _mark_matches(self) -> None:
        '''Mark the given coordinates as matched (state = 4)'''
        matches = self._matches
        for c, r in matches:
            self._board[c][r].state = 4

    def _clear_matches(self) -> None:
        '''Removes all matched cells with the matched state'''
        matches = self._matches
        for c, r in matches:
            self._board[c][r] = Cell(0, None)

    def _update_board(self) -> None:
        '''Redraw the faller's current cells on the board and clear its previous positions'''
        board = self._board
        faller = self._faller

        for c, r in faller.prev_coords():
            if r >= 0:
                if board[c][r].state == 1 or board[c][r].state == 2:
                    board[c][r] = Cell(0, None)

        self._faller.update_prev_coords()

        for n, coords in enumerate(faller.coords()):
            c, r = coords
            if r >= 0:
                board[c][r] = faller.get_jewel(n)

    def _update_faller_state(self) -> None:
        '''Updates the faller's state (falling → landed → frozen) based on its surroundings'''
        faller = self._faller
        state = faller.state()
        landed = self._is_faller_landed()
        
        if state == 1 and landed:
            faller.update_state(2)
        elif state == 2:
            if landed:
                faller.update_state(3)
            else:
                faller.update_state(1)

    def _is_faller_landed(self) -> bool:
        '''Returns True if the faller is resting on the board bottom or another jewel'''
        faller = self._faller
        board_bot_row = self._rows - 1
        faller_bot_row = faller.bottom_row()
        
        if faller_bot_row == board_bot_row:
            return True
        
        board = self._board
        faller_col = faller.col()
        if board[faller_col][faller_bot_row + 1].jewel is not None:
            return True
        
        return False

