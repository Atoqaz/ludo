from ludo import *
from random import choice

ludo = Ludo()


def move_semi_manual(PLAYERS: List[Player], board: np.array, moveable_pieces: List[int], turn: int, dice_roll: int):
    if len(moveable_pieces) == 1:
        return moveable_pieces[0]
    else:
        piece2move = -1
        while piece2move not in moveable_pieces:
            try:
                piece2move = int(input(f"Select piece to move {moveable_pieces}: "))
            except ValueError:
                piece2move = -1
        return piece2move


def move_naive(PLAYERS: List[Player], board: np.array, moveable_pieces: List[int], turn: int, dice_roll: int):
    piece2move = min(moveable_pieces)
    return piece2move


def move_random(PLAYERS: List[Player], board: np.array, moveable_pieces: List[int], turn: int, dice_roll: int):
    piece2move = choice(moveable_pieces)
    return piece2move


def move_max_score(PLAYERS: List[Player], board: np.array, moveable_pieces: List[int], turn: int, dice_roll: int):
    if len(moveable_pieces) == 1:
        return moveable_pieces[0]
    else:
        max_score = 0
        piece = 0
        for x in moveable_pieces:
            new_board = ludo.move_piece(
                board=board, turn=turn, moveable_pieces=moveable_pieces, dice_roll=dice_roll, piece2move=x
            )
            score = new_board.sum(axis=0)[turn]
            if score > max_score:
                max_score = score
                piece2move = x
    return piece2move
