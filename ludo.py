import pandas as pd
import numpy as np
from typing import List
from random import randint, choice
from dataclasses import dataclass
from time import sleep
import copy
import os

from multiprocessing import Process

# import tkinter as tk
from PIL import Image  # , ImageTk




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
        # self._plot_setup()

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

    def _plot_setup(self):
        self.img_board = Image.open("board/board.png")
        img_blue = Image.open("board/blue.png")
        img_red = Image.open("board/red.png")
        img_green = Image.open("board/green.png")
        img_orange = Image.open("board/orange.png")
        self.pieces = [img_blue, img_red, img_green, img_orange]
        self.plot_offset = [(-14, -14), (7, -14), (-14, 7), (7, 7)]
        # Start places
        self.board_pos = [(700, 140), (700, 700), (140, 700), (140, 140)]
        # Part of blue path
        self.board_pos += [(476, 84 + 56 * x) for x in range(5)]
        # Red path
        self.board_pos += [(532 + 56 * x, 364) for x in range(6)]
        self.board_pos += [(812, 420)]
        self.board_pos += [(812 - 56 * x, 476) for x in range(6)]
        # # Green path
        self.board_pos += [(476, 532 + 56 * x) for x in range(6)]
        self.board_pos += [(420, 812)]
        self.board_pos += [(364, 812 - 56 * x) for x in range(6)]
        # # Orange path
        self.board_pos += [(308 - 56 * x, 476) for x in range(6)]
        self.board_pos += [(28, 420)]
        self.board_pos += [(28 + 56 * x, 364) for x in range(6)]
        # Blue path
        self.board_pos += [(364, 308 - 56 * x) for x in range(6)]
        self.board_pos += [(420 + 56 * x, 28) for x in range(2)]
        # Blue arm
        self.board_pos += [(420, 84 + 56 * x) for x in range(6)]
        # Red arm
        self.board_pos += [(756 - 56 * x, 420) for x in range(6)]
        # Green arm
        self.board_pos += [(420, 756 - 56 * x) for x in range(6)]
        # Orange arm
        self.board_pos += [(84 + 56 * x, 420) for x in range(6)]

    def display_board(self, board: pd.DataFrame) -> None:
        # window = tk.Tk()
        # imagefile = "board/board.png"
        # img = ImageTk.PhotoImage(Image.open(imagefile))
        # lbl = tk.Label(window, image = img).pack()
        # window.mainloop()

        board_abs = self.board_to_abs_pos(board=board)
        displayed_board = copy.deepcopy(self.img_board)

        i = 0  # color/column index
        for player, column in board_abs.iteritems():
            for j, val in enumerate(column):
                displayed_board.paste(self.pieces[i], self._add_tup(self.board_pos[val], self.plot_offset[j]))
            i += 1

        displayed_board.show()

    def multiplot(self):
        p = Process(target=self.display_board, kwargs={"board": self.board})
        p.start()
        moves = self.get_moveable_pieces(board=self.board, color_turn="blue", dice_roll="globe")
        piece = input(f"Select piece to move: {moves} ")
        print(f"Moving piece: {piece}")
        p.join()

    def testing(self):
        # Temporary
        # self.color_turn = "blue"
        # self.dice_roll = "star"

        # self.board.loc[[0], ["blue"]] = 2
        # self.board.loc[[1], ["blue"]] = 14

        # for i in range(3):
        #     self.display_board(board=self.board)

        color_turn = "blue"

        dice_roll = self._roll_dice(board=self.board,color_turn=color_turn)
        self.board = self.move_piece(board=self.board, color_turn=color_turn, dice_roll=dice_roll, piece2move=0)
        print(self.board)

    def get_moveable_pieces(self, board: pd.DataFrame, color_turn: str, dice_roll: str) -> List[int]:
        if dice_roll == "star":
            mask = (board[color_turn] < self.stars[-1]) & (board[color_turn] > 0)
            return board[mask].index.tolist()
        elif dice_roll == "globe":
            mask = board[color_turn] < self.globes[-1]
            return board[mask].index.tolist()
        else:
            mask = (board[color_turn] > 0) & (board[color_turn] < self.goal_pos)
            return board[mask].index.tolist()

    def _effecting_others(self, board: pd.DataFrame, color_turn: str, location: int) -> dict:
        if location <= 51:
            for i, enemy in enumerate(self.board_order[color_turn], 1):
                pos = (location - i * self.offset - 1) % 52 + 1
                enemy_in_spot = board.loc[:, enemy] == pos
                if enemy_in_spot.any():
                    pieces = enemy_in_spot.index[enemy_in_spot].tolist()
                    return {enemy: pieces}
        return None

    def move_piece(
        self, board: pd.DataFrame, color_turn: str, moveable_pieces: List[int], dice_roll: str, piece2move: int
    ) -> pd.DataFrame:
        if piece2move not in moveable_pieces:
            raise ValueError(f"Unable to move piece {piece2move} for {color_turn} player")

        if dice_roll == "star":
            new_pos = self._get_next_object_pos(objects=self.stars, current_pos=board.loc[piece2move, color_turn])
        elif dice_roll == "globe":
            new_pos = self._get_next_object_pos(objects=self.globes, current_pos=board.loc[piece2move, color_turn])
        else:
            new_pos = min(board.loc[piece2move, color_turn] + int(dice_roll), self.goal_pos)

        effected_pieces = self._effecting_others(board, color_turn, new_pos)
        if effected_pieces == None:
            # No enemy piece on location
            board.loc[piece2move, color_turn] = new_pos
        else:
            enemy = next(iter(effected_pieces))
            pieces = effected_pieces[enemy]
            if (new_pos == 1) or (len(pieces) == 1 and (new_pos not in self.globes[1:])):
                # Player piece takes enemy position, enemy get moved to start
                board.loc[piece2move, color_turn] = new_pos
                for piece in pieces:
                    board.loc[piece, enemy] = 0
            else:  # More than one piece on the position
                # Player piece get moved to start
                board.loc[piece2move, color_turn] = 0

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

    def _roll_dice(self, board: pd.DataFrame, color_turn: str):
        if (board.loc[:, color_turn] == 0).all():
            for count in range(3):
                dice_roll = self._roll_dice_single()
                if dice_roll == "globe":
                    break
        else:
            dice_roll = self._roll_dice_single()
        return dice_roll
        # return choice(["globe","6"])

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

    def _get_next_player(self, colors: List[str], color_turn: str):
        return colors[(colors.index(color_turn) + 1) % len(colors)]

    def _get_used_items(self, full: list, subset: list):
        used = full
        unused = list(set(full) - set(subset))
        for item in unused:
            full.remove(item)
        return used

    def _detect_win(self, board: pd.DataFrame, player: Player) -> bool:
        for i, score in enumerate(board.mean()):
            if score == self.goal_pos:
                # os.system("cls" if os.name == "nt" else "clear")
                # print("\n--- GAME OVER ---\n")
                # print(f"The winner is {player.name} from the {board.columns[i]} team")
                return True
        return False

    def _initialize_game(self, PLAYERS: List[Player]):
        # Give players a color
        n_players = len(PLAYERS)
        if n_players >= 2 and n_players <= 4:
            colors = np.random.choice(self.board.columns.tolist(), n_players, replace=False)

            color_to_player_idx = {}
            for i, player in enumerate(PLAYERS):
                player.color = colors[i]
                color_to_player_idx[colors[i]] = i

            colors_in_play = self._get_used_items(full=self.board.columns.tolist(), subset=colors)
        else:
            raise ValueError(f"Player count should be between 2 and 4, but it is set to {n_players}")

        return colors, colors_in_play, color_to_player_idx

    def play(self, PLAYERS: List[Player], display=True):
        colors, colors_in_play, color_to_player_idx = self._initialize_game(PLAYERS=PLAYERS)

        # Select starting player
        color_turn = np.random.choice(colors, 1)[0]
        # Start game
        while True:
            dice_roll = self._roll_dice(board=self.board, color_turn=color_turn)

            player = PLAYERS[color_to_player_idx[color_turn]]
            # Display information:
            if display:
                os.system("cls" if os.name == "nt" else "clear")
                print(self.board)
                print(f"{player.name} ({color_turn}) rolled: {dice_roll}")

            # Get options and move player piece
            moveable_pieces = self.get_moveable_pieces(board=self.board, color_turn=color_turn, dice_roll=dice_roll)
            if moveable_pieces:
                while True:
                    if player.function == None:
                        piece2move = int(input(f"Select piece to move {moveable_pieces}: "))
                    else:
                        piece2move = player.function(PLAYERS=PLAYERS, board=self.board, moveable_pieces=moveable_pieces)
                    if piece2move in moveable_pieces:
                        break

                self.board = self.move_piece(
                    board=self.board,
                    moveable_pieces=moveable_pieces,
                    color_turn=color_turn,
                    dice_roll=dice_roll,
                    piece2move=piece2move,
                )

                if self._detect_win(board=self.board, player=player):
                    break
            else:
                if display:
                    print("Sorry, you could not move any pieces this turn")
                    sleep(1.5)

            # Give extra turn if globe is rolled
            if dice_roll != "globe":
                color_turn = self._get_next_player(colors_in_play, color_turn)
            else:
                if display:
                    print("You get an extra turn")




# if __name__ == "__main__":
#     PLAYERS = [
#         Player("Atoqaz", None),
#         Player("SupDeus", None),
#         Player("QuantumCat", None),
#         Player("Manual input", None),
#     ]

#     ludo = Ludo()
#     ludo.play(PLAYERS=PLAYERS, display=False)
