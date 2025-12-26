import json
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo

GAME_DATA_PATH = Path('data/games.json')
LEADERBOARD_DATA_PATH = Path('data/leaderboard.json')


        
def user_exists(username: str) -> bool:
    data = _load_data(LEADERBOARD_DATA_PATH)
    return any(record['username'] == username for record in data)

def get_leaderboard(start: int = 1, end: int = 9) -> list[dict]:
    data = _load_data(LEADERBOARD_DATA_PATH)
    return data[start-1:end+1]

def save_new_entry(username: str, score: int, time: int, level: int) -> None:
    game_data = _load_data(GAME_DATA_PATH)

    game_data.append({
        "timestamp": _get_current_timestamp(),
        "username": username,
        "score": score,
        "time": time,
        "level": level
    })
    _save_data(GAME_DATA_PATH, game_data)

    leaderboard_data = _load_data(LEADERBOARD_DATA_PATH)

    user_record = next((item for item in leaderboard_data if item['username'] == username), None)

    if user_record:
        # if the user exists
        if score > user_record['score']:
            user_record['score'] = score
            user_record['time'] = time
            user_record['level'] = level
    else:
        leaderboard_data.append({
            "username": username,
            "score": score,
            "time": time,
            "level": level
        })

    leaderboard_data.sort(key=lambda x: x['score'], reverse=True)

    for i, record in enumerate(leaderboard_data):
        record['placement'] = i + 1

    _save_data(LEADERBOARD_DATA_PATH, leaderboard_data)

def _load_data(file_path: Path) -> list[dict]:
    if not file_path.exists():
        return []
    with file_path.open('r', encoding='utf-8') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []
        
def _save_data(file_path: Path, data: list[dict]) -> None:
    with file_path.open('w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)

def _get_current_timestamp() -> str:
    pst_now = datetime.now(ZoneInfo('America/Los_Angeles'))
    return pst_now.strftime('%B %d, %Y %I:%M %p %Z')