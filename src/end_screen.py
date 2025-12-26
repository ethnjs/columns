
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