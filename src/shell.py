import engine

def get_rows_cols() -> tuple[int, int]:
    rows = int(input())
    cols = int(input())

    return rows, cols

def get_initial_board(rows: int, cols: int) -> list[str]:
    field = input()
    if field == 'EMPTY':
        return []
    elif field == 'CONTENTS':
        data = []
        for _ in range(rows):
            line = input()
            data.append(line)
        return data

def get_action() -> str:
    action = input().strip()
    return action

def display_board(game: engine.GameState) -> None:
    rows = game.rows()
    columns = game.columns()
    board = game.board()

    for r in range(rows):
        print('|', end='')
        for c in range(columns):
            print(_translate_cell(board[r][c]), end='')
        print('|')

    print(f" {'---' * columns} ")

def _translate_cell(cell: engine.Cell) -> str:
    '''Converts a Cell into its display-string form based on its state.'''
    state = cell.state
    jewel = cell.jewel
    if state == 0:
        return '   '
    elif state == 1:
        return f'[{jewel}]'
    elif state == 2:
        return f'|{jewel}|'
    elif state == 3:
        return f' {jewel} '
    elif state == 4:
        return f'*{jewel}*'



def run_game() -> None:
    rows, cols = get_rows_cols()
    game = engine.GameState(rows, cols)

    data = get_initial_board(rows, cols)
    if data != []:
        game.load(data)
    
    display_board(game)

    while True:
        action = get_action()
        
        try:
            if action == '':
                game.tick()
            elif action.startswith('F'):
                col = int(action.split()[1])
                jewels = action.split()[2:]
                faller = engine.Faller(col, jewels)
                game.spawn_faller(faller)
            elif action == 'R':
                game.rotate_faller()
            elif action == '<':
                game.move_faller_left()
            elif action == '>':
                game.move_faller_right()
            elif action == 'Q':
                game.end()
                break
        except engine.IllegalAction:
            pass

        display_board(game)

        if game.game_over():
            print('GAME OVER')
            break

if __name__ == '__main__':
    run_game()