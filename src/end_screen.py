
class EndGame(Exception):
    pass

class RestartGame(Exception):
    pass

class EndScreen():
    def __init__(self, username: str, score: int, time: str):
        self._username = username
        self._score = score
        self._time = time