
from ludo import *


def make_move_atoqaz(PLAYERS: List[Player], board: pd.DataFrame, moveable_pieces: List[int]):
    piece2move = min(moveable_pieces)
    return piece2move