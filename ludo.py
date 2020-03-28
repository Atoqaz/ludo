import pandas as pd
import numpy as np
from typing import List
from random import randint
from colorama import init
from colorama import Fore, Back
import os


class ColorTerminal:
    def __init__(self):
        init()

    def b(self, text: str) -> str:
        return Fore.BLUE + text + Fore.RESET

    def r(self, text: str) -> str:
        return Fore.RED + text + Fore.RESET

    def g(self, text: str) -> str:
        return Fore.GREEN + text + Fore.RESET

    def m(self, text: str) -> str:
        return Fore.MAGENTA + text + Fore.RESET

    def B(self, text: str) -> str:
        return Back.BLUE + text + Back.RESET

    def R(self, text: str) -> str:
        return Back.RED + text + Back.RESET

    def G(self, text: str) -> str:
        return Back.GREEN + text + Back.RESET

    def M(self, text: str) -> str:
        return Back.MAGENTA + text + Back.RESET


class Ludo:
    def __init__(self):
        self.ct = ColorTerminal()
        self.board = self._create_board()
        self.stars = [6, 12, 19, 25, 32, 38, 45, 51]
        self.globes = [1, 9, 14, 22, 27, 35, 40, 48]
        self.goal_pos = 57
        self.offset = 13

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
        board = board.rename(columns={0: "blue", 1: "red", 2: "green", 3: "magenta"})

        self.board_order = {
            "blue": ["red", "green", "magenta"],
            "red": ["green", "magenta", "blue"],
            "green": ["magenta", "blue", "red"],
            "magenta": ["blue", "red", "green"],
        }
        return board

    def get_moveable_pieces(self, board: pd.DataFrame, player_turn: str, dice_roll: str) -> List[int]:
        if dice_roll == "star":
            all_in_start = (board.loc[:, [player_turn]] == 0).values.all()
            if all_in_start:
                return []
            else:
                mask = board[player_turn] < self.stars[-1]
                return board.loc[mask].index.values
        elif dice_roll == "globe":
            mask = board[player_turn] < self.globes[-1]
            return board.loc[mask].index.values
        else:
            mask = (board[player_turn] > 0) & (board[player_turn] < self.goal_pos)
            return board.loc[mask].index.values

    def effecting_others(self, board: pd.DataFrame, player_turn: str, location: int) -> dict:
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

    def move_piece(self, board: pd.DataFrame, player_turn: str, dice_roll: str, piece2move: int) -> pd.DataFrame:
        moveable_pieces = self.get_moveable_pieces(board=board, dice_roll=dice_roll, player_turn=player_turn)

        if piece2move not in moveable_pieces:
            raise ValueError(f"Unable to move piece {piece2move} for {player_turn} player")

        if dice_roll == "star":
            new_pos = self.get_next_object_pos(objects=self.stars, current_pos=board.loc[piece2move, player_turn])
        elif dice_roll == "globe":
            new_pos = self.get_next_object_pos(objects=self.globes, current_pos=board.loc[piece2move, player_turn])
        else:
            new_pos = min(board.loc[piece2move, player_turn] + int(dice_roll), self.goal_pos)

        effected_pieces = self.effecting_others(board, player_turn, new_pos)

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

    def get_next_object_pos(self, objects: list, current_pos: int) -> int:
        for object_pos in objects:
            if object_pos > current_pos:
                return object_pos
        return None

    def roll_dice(self) -> str:
        rand_num = randint(1, 6)
        if rand_num == 3:
            dice_roll = "star"
        elif rand_num == 5:
            dice_roll = "globe"
        else:
            dice_roll = str(rand_num)
        return dice_roll

    def board_to_abs_pos(self, board: pd.DataFrame) -> pd.DataFrame:
        """ Gets the absolute position of the pieces

            0-3:    Blue start
            4-7:    Red start
            8-11:   Green start
            12-15:  Magenta start

            16-67:  Main board, starting at blue globus
            
            68-73:  Blue arm
            74-79:  Red arm
            80-85:  Green arm
            86-91:  Magenta arm
        """
        board_abs = board.copy(deep=True)
        for col in board_abs.columns:
            board_abs[col].values[:] = 0

        i = 0
        for player, column in board.iteritems():
            for j, val in enumerate(column):
                if val == 0:
                    real_pos = j + i * 4

                elif val >= 52:
                    real_pos = 16 + val + i * 6
                else:
                    real_pos = 16 + (val + i * self.offset - 1) % 52

                board_abs.loc[j, player] = real_pos
            i += 1

        return board_abs


if __name__ == "__main__":
    ludo = Ludo()
