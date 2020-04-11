from ludo import Ludo, Player
from player_functions import *

from profiler import profile

import numpy as np


@profile
def measure_time(PLAYERS, N):
    for n in range(N):
        ludo = Ludo()
        ludo.play(PLAYERS, display=False)


def make_statistics(PLAYERS, N):
    wins = {}
    for n in range(N):
        ludo = Ludo()
        winner = ludo.play(PLAYERS, display=False)

        func_name = winner.function.__name__
        if func_name not in wins:
            wins[func_name] = 1
        else:
            wins[func_name] += 1

    print(wins)


if __name__ == "__main__":
    # PLAYERS = [
    #     Player("One", move_max_score),
    #     Player("Two", move_naive),
    #     Player("Three", move_naive),
    #     Player("Four", move_random),
    # ]
    PLAYERS = [
        Player("One", move_semi_manual),
        Player("Two", move_semi_manual),
        Player("Three", move_semi_manual),
        Player("Four", move_semi_manual),
    ]
    
    # measure_time(PLAYERS, N=100)
    # make_statistics(PLAYERS, N=200)

    ludo = Ludo()
    winner = ludo.play(PLAYERS=PLAYERS, display=True)
    # print(winner)
