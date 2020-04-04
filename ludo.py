import pandas as pd
import numpy as np
from typing import List
from random import randint, choice
from dataclasses import dataclass
from time import sleep
import copy
import os


@dataclass()
class Player:
    name: str
    function: str
    color: str = None

    def __repr__(self):
        return f"[Name: {self.name}, Function: {self.function}, Color: {self.color}]"


class Ludo:
    def __init__(self):
        self.board = self._create_board()
        self.stars = [6, 12, 19, 25, 32, 38, 45, 51]
        self.globes = [1, 9, 14, 22, 27, 35, 40, 48]
        self.goal_pos = 57
        self.offset = 13  # Offset between teams on the board

    def _create_board(self) -> pd.DataFrame:
        """ The board is the position of the 4 pieces for each team.
            The position can range from 0 to 57
            The position is relative to each player.

            0:      Start
            1-51:   Board
            52-56:  Individual arm
            57:     End

        """
        board_array = np.zeros((4, 4), dtype=int)
        board = pd.DataFrame(board_array)
        board = board.rename(columns={0: "blue", 1: "red", 2: "green", 3: "orange"})

        self.board_order = {
            "blue": ["red", "green", "orange"],
            "red": ["green", "orange", "blue"],
            "green": ["orange", "blue", "red"],
            "orange": ["blue", "red", "green"],
        }
        return board

    def get_moveable_pieces(self, board: pd.DataFrame, player_turn: str, dice_roll: str) -> List[int]:
        if dice_roll == "star":
            mask = (board[player_turn] < self.stars[-1]) & (board[player_turn] > 0)
            return board.loc[mask].index.tolist()
        elif dice_roll == "globe":
            mask = board[player_turn] < self.globes[-1]
            return board.loc[mask].index.tolist()
        else:
            mask = (board[player_turn] > 0) & (board[player_turn] < self.goal_pos)
            return board.loc[mask].index.tolist()

    def _effecting_others(self, board: pd.DataFrame, player_turn: str, location: int) -> dict:
        for i, enemy in enumerate(self.board_order[player_turn], 1):
            pos = location - i * self.offset
            if pos <= 0:
                return None
            enemy_in_spot = board.loc[:, enemy] == pos
            any_piece_in_spot = enemy_in_spot.any()
            if any_piece_in_spot:
                pieces = enemy_in_spot.index[enemy_in_spot].tolist()
                return {enemy: pieces}
        return None

    def move_piece(
        self, board: pd.DataFrame, player_turn: str, moveable_pieces: List[int], dice_roll: str, piece2move: int
    ) -> pd.DataFrame:
        if piece2move not in moveable_pieces:
            raise ValueError(f"Unable to move piece {piece2move} for {player_turn} player")

        if dice_roll == "star":
            new_pos = self._get_next_object_pos(objects=self.stars, current_pos=board.loc[piece2move, player_turn])
        elif dice_roll == "globe":
            new_pos = self._get_next_object_pos(objects=self.globes, current_pos=board.loc[piece2move, player_turn])
        else:
            new_pos = min(board.loc[piece2move, player_turn] + int(dice_roll), self.goal_pos)

        effected_pieces = self._effecting_others(board, player_turn, new_pos)

        if effected_pieces == None:
            # No enemy piece on location
            board.loc[piece2move, player_turn] = new_pos
        else:
            enemy = next(iter(effected_pieces))
            pieces = effected_pieces[enemy]
            if len(pieces) == 1 and (new_pos not in self.globes):
                # Player piece takes enemy position, enemy get moved to start
                board.loc[piece2move, player_turn] = new_pos
                board.loc[pieces[0], enemy] = 0
            else:
                # Player piece get moved to start
                board.loc[piece2move, player_turn] = 0

        return board

    def _get_next_object_pos(self, objects: list, current_pos: int) -> int:
        for object_pos in objects:
            if object_pos > current_pos:
                return object_pos
        return None

    def _roll_dice_single(self) -> str:
        rand_num = randint(1, 6)
        if rand_num == 3:
            dice_roll = "star"
        elif rand_num == 5:
            dice_roll = "globe"
        else:
            dice_roll = str(rand_num)
        return dice_roll

    def _roll_dice(self, board: pd.DataFrame, player_turn: str):
        if (board.loc[:, player_turn] == 0).all():
            for count in range(3):
                dice_roll = self._roll_dice_single()
                if dice_roll == "globe":
                    break
        else:
            dice_roll = self._roll_dice_single()
        return dice_roll

    def board_to_abs_pos(self, board: pd.DataFrame) -> pd.DataFrame:
        """ Gets the absolute position of the pieces

            0:    Blue start
            1:    Red start
            2:   Green start
            3:  Orange start

            4-55:  Main board, starting at blue globus, clockwise
            
            56-61:  Blue arm
            62-67:  Red arm
            68-73:  Green arm
            74-79:  Orange arm
        """
        board_abs = board.copy(deep=True)
        for col in board_abs.columns:
            board_abs[col].values[:] = 0

        i = 0  # color/column index
        for player, column in board.iteritems():
            for j, val in enumerate(column):
                if val == 0:
                    real_pos = i

                elif val >= 52:
                    real_pos = 4 + val + i * 6
                else:
                    real_pos = 4 + (val + i * self.offset - 1) % 52

                board_abs.loc[j, player] = real_pos
            i += 1

        return board_abs

    def _add_tup(self, a: tuple, b: tuple) -> tuple:
        c = tuple((x + y for x, y in zip(a, b)))
        return c

    def _get_next_player(self, colors: List[str], player_turn: str):
        return colors[(colors.index(player_turn) + 1) % len(colors)]

    def _get_used_items(self, full: list, subset: list):
        used = full
        unused = list(set(full) - set(subset))
        for item in unused:
            full.remove(item)
        return used

    def _get_player_name(self, PLAYERS: List[Player], player_turn: str):
        for player in PLAYERS:
            if player.color == player_turn:
                return player.name
        return None

    def _detect_win(self, board: pd.DataFrame) -> bool:
        for i, score in enumerate(board.mean()):
            if score == self.goal_pos:
                os.system("cls" if os.name == "nt" else "clear")
                print("\n--- GAME OVER ---\n")
                print(f"The winner is the {board.columns[i]} team")

                return True
        return False

    def play(self, PLAYERS: List[Player], display=True):
        # Give players a color
        n_players = len(PLAYERS)
        if n_players >= 2 and n_players <= 4:
            colors = np.random.choice(self.board.columns.tolist(), n_players, replace=False)

            for i, player in enumerate(PLAYERS):
                player.color = colors[i]
        else:
            raise ValueError(f"Player count should be between 2 and 4, but it is set to {n_players}")

        # Select starting player, and get teams in play
        player_turn = np.random.choice(colors, 1)[0]
        colors_in_play = self._get_used_items(full=self.board.columns.tolist(), subset=colors)
        # Start game
        while True:
            dice_roll = self._roll_dice(board=self.board, player_turn=player_turn)

            # Display information:
            if display:
                os.system("cls" if os.name == "nt" else "clear")
                print(self.board)
                player_name = self._get_player_name(PLAYERS=PLAYERS, player_turn=player_turn)
                print(f"{player_name} ({player_turn}) rolled: {dice_roll}")

            # Get options and move player piece
            moveable_pieces = self.get_moveable_pieces(board=self.board, player_turn=player_turn, dice_roll=dice_roll)
            if moveable_pieces:
                while True:
                    for player in PLAYERS:
                        if player.color == player_turn:
                            if player.function == None:
                                piece2move = int(input(f"Select piece to move {moveable_pieces}: "))
                            else:
                                piece2move = player.function(
                                    PLAYERS=PLAYERS, board=self.board, moveable_pieces=moveable_pieces
                                )
                    if piece2move in moveable_pieces:
                        break

                self.board = self.move_piece(
                    board=self.board,
                    moveable_pieces=moveable_pieces,
                    player_turn=player_turn,
                    dice_roll=dice_roll,
                    piece2move=piece2move,
                )

                if self._detect_win(board=self.board):
                    break
            else:
                if display:
                    print("Sorry, you could not move any pieces this turn")
                    sleep(1.5)

            player_turn = self._get_next_player(colors_in_play, player_turn)


def make_move_atoqaz(PLAYERS: List[Player], board: pd.DataFrame, moveable_pieces: List[int]):
    print("Atoqaz' function")
    piece2move = int(input(f"Select piece to move {moveable_pieces}: "))
    return piece2move


def make_move_supdeus(PLAYERS: List[Player], board: pd.DataFrame, moveable_pieces: List[int]):
    print("SupDeus' function")
    piece2move = int(input(f"Select piece to move {moveable_pieces}: "))
    return piece2move


def make_move_quantumcat(PLAYERS: List[Player], board: pd.DataFrame, moveable_pieces: List[int]):
    print("QuantumCats function")
    piece2move = int(input(f"Select piece to move {moveable_pieces}: "))
    return piece2move


if __name__ == "__main__":
    PLAYERS = [
        Player("Atoqaz", make_move_atoqaz),
        Player("SupDeus", make_move_supdeus),
        Player("QuantumCat", make_move_quantumcat),
        Player("Last_Player", None),
    ]

    ludo = Ludo()
    ludo.play(PLAYERS=PLAYERS)
