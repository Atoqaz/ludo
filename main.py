
from ludo import Ludo, Player
from atoqaz_fun import make_move_atoqaz

from profiler import profile


import numpy as np




@profile
def measure_time(PLAYERS, N):
    for n in range(N):
        ludo = Ludo()
        ludo.play(PLAYERS, display=False)



if __name__ == "__main__":
    pass
    PLAYERS = [
        Player("One", make_move_atoqaz),
        Player("Two", make_move_atoqaz),
        Player("Three", make_move_atoqaz),
        Player("Four", make_move_atoqaz),
    ]

    # measure_time(PLAYERS, N=100)

    ludo = Ludo()
    ludo.play(PLAYERS=PLAYERS, display=True)