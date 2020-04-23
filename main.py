from ludo import Ludo, Player
from player_functions import *

from profiler import profile



@profile
def measure_time(PLAYERS, N):
    ludo = Ludo()
    for n in range(N):
        ludo.play(PLAYERS, display=False)


def make_statistics(PLAYERS, N):
    wins = {}
    ludo = Ludo()
    for n in range(N):
        winner = ludo.play(PLAYERS, display=False)[0]

        func_name = winner.function.__name__
        if func_name not in wins:
            wins[func_name] = 1
        else:
            wins[func_name] += 1

    wins = {k: v for k, v in sorted(wins.items(), key=lambda item: item[1], reverse=True)}

    print(wins)


if __name__ == "__main__":
    PLAYERS = [
        Player("One", move_naive),
        Player("Two", move_random),
        Player("Three", move_random),
        Player("Four", move_naive),
    ]
    # PLAYERS = [
    #     Player("One", move_semi_manual),
    #     Player("Two", move_semi_manual),
    #     Player("Three", move_semi_manual),
    #     # Player("Four", move_semi_manual),
    # ]
    
    # measure_time(PLAYERS, N=1500)
    make_statistics(PLAYERS, N=100)

    # ludo = Ludo()
    # winner = ludo.play(PLAYERS=PLAYERS, display=False, n_players_to_finish=4)
    # print(winner)
