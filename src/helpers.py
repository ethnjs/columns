import time

from constants import *

def _frames_to_str(frames: int) -> str:
    sec = frames // FRAME_RATE
    return time.strftime('%M:%S', time.gmtime(sec)) + f'.{(frames % FRAME_RATE):02d}'