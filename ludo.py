import numpy as np
from typing import List
from random import randint, choice
from dataclasses import dataclass
import copy
import os

# from time import sleep

# Image display
from PIL import Image
import matplotlib.pyplot as plt


@dataclass()
class Player:
    name: str
    function: str  # Function, not a string. I don't know the name/syntax
    team: int = None
    color: str = None

    def __repr__(self):
        return f"[Name: {self.name}, Function: {self.function}, Team idx: {self.team}, Color: {self.color}]"


class Ludo:
    def __init__(self):
        self.board = self._create_board()
        self.stars = [6, 12, 19, 25, 32, 38, 45, 51]
        self.globes = [1, 9, 14, 22, 27, 35, 40, 48]
        self.goal_pos = 57
        self.offset = 13  # Offset between teams on the board
        self.dice_star = 3  # Dice roll corresponding to a star
        self.dice_globe = 5  # Dice roll corresponding to a globe

    def _create_board(self) -> np.array:
        """ The board is the position of the 4 pieces for each team.
            The position can range from 0 to 57
            The position is relative to each player.

            0:      Start
            1-51:   Board
            52-56:  Individual arm
            57:     End

        """
        board = np.zeros((4, 4), dtype=int)
        return board

    def board_to_abs_pos(self, board: np.array) -> np.array:
        """ Gets the absolute position of the pieces

            0:      Blue start
            1:      Red start
            2:      Green start
            3:      Orange start

            4-55:   Main board, starting at blue globus, clockwise
            
            56-61:  Blue arm
            62-67:  Red arm
            68-73:  Green arm
            74-79:  Orange arm
        """
        board_abs = np.zeros((4, 4), dtype=int)

        for i in range(4):
            for j in range(4):
                val = board[i][j]
                if val == 0:
                    real_pos = j
                elif val >= 52:
                    real_pos = 4 + val + j * 6
                else:
                    real_pos = 4 + (val + j * self.offset - 1) % 52

                board_abs[i, j] = real_pos
        return board_abs

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

    def _roll_dice(self, board: np.array, turn: int):
        if (board[:, turn] == 0).all():
            for count in range(3):
                dice_roll = randint(1, 6)
                if dice_roll == self.dice_globe:
                    break
        else:
            dice_roll = randint(1, 6)
        return dice_roll

    def get_moveable_pieces(self, board: np.array, turn: int, dice_roll: int) -> List[int]:
        if dice_roll == self.dice_star:
            mask = (board[:, turn] < self.stars[-1]) & (board[:, turn] > 0)
        elif dice_roll == self.dice_globe:
            mask = board[:, turn] < self.globes[-1]
        else:
            mask = (board[:, turn] > 0) & (board[:, turn] < self.goal_pos)
        return [i for i, x in enumerate(mask) if x == True]

    def _effecting_others(self, board: np.array, turn: int, location: int) -> (int, List[int]):
        if location <= 51:
            enemies_idx = [(x + 1 + turn) % 4 for x in range(3)]
            for i, enemy_idx in enumerate(enemies_idx, 1):
                pos = (location - i * self.offset - 1) % 52 + 1
                enemy_in_spot = board[:, enemy_idx] == pos
                if enemy_in_spot.any():
                    pieces = [i for i, x in enumerate(enemy_in_spot) if x == True]
                    return enemy_idx, pieces
        return None, None

    def _get_next_object_pos(self, objects: list, current_pos: int) -> int:
        for object_pos in objects:
            if object_pos > current_pos:
                return object_pos
        return None

    def move_piece(
        self, board: np.array, turn: int, moveable_pieces: List[int], dice_roll: int, piece2move: int
    ) -> np.array:
        if piece2move not in moveable_pieces:
            raise ValueError(f"Unable to move piece {piece2move} for player {turn}")

        if dice_roll == self.dice_star:
            new_pos = self._get_next_object_pos(objects=self.stars, current_pos=board[piece2move, turn])
        elif dice_roll == self.dice_globe:
            new_pos = self._get_next_object_pos(objects=self.globes, current_pos=board[piece2move, turn])
        else:
            new_pos = min(board[piece2move, turn] + dice_roll, self.goal_pos)

        effected_enemy, effected_pieces = self._effecting_others(board=board, turn=turn, location=new_pos)
        if effected_pieces == None:
            # No enemy piece on location
            board[piece2move, turn] = new_pos
        else:
            if (new_pos == 1) or (len(effected_pieces) == 1 and (new_pos not in self.globes[1:])):
                # Player piece takes enemy position, enemy get moved to start
                board[piece2move, turn] = new_pos
                for piece in effected_pieces:
                    board[piece, effected_enemy] = 0
            else:  # More than one piece on the position
                # Player piece get moved to start
                board[piece2move, turn] = 0

        return board

    def _get_next_player(self, teams: List[int], turn: str):
        return teams[(teams.index(turn) + 1) % 4]

    def _get_used_items(self, full: list, subset: list):
        used = full
        unused = list(set(full) - set(subset))
        for item in unused:
            full.remove(item)
        return used

    def _initialize_game(self, PLAYERS: List[Player]):
        # Give players a color
        n_players = len(PLAYERS)
        if n_players >= 2 and n_players <= 4:
            teams = np.random.choice([0, 1, 2, 3], n_players, replace=False)
            colors = ["Blue", "Red", "Green", "Orange"]

            team_to_player_idx = {}
            for i, player in enumerate(PLAYERS):
                player.team = teams[i]
                player.color = colors[teams[i]]
                team_to_player_idx[teams[i]] = i

            teams_in_play = self._get_used_items(full=[0, 1, 2, 3], subset=teams)
        else:
            raise ValueError(f"Player count should be between 2 and 4, but it is set to {n_players}")

        return teams, teams_in_play, team_to_player_idx

    def _detect_win(self, board: np.array, player: Player) -> bool:
        final_pos = self.goal_pos * 4
        for i, score in enumerate(board.sum(axis=0)):
            if score == final_pos:
                os.system("cls" if os.name == "nt" else "clear")
                print("\n--- GAME OVER ---\n")
                print(f"The winner is {player.name} ({player.color})")
                return True
        return False

    def play(self, PLAYERS: List[Player], display=True):
        if display:
            self._plot_setup()

        teams, teams_in_play, team_to_player_idx = self._initialize_game(PLAYERS=PLAYERS)

        # Select starting player
        turn = np.random.choice(teams, 1)[0]
        # Start game
        while True:
            dice_roll = self._roll_dice(board=self.board, turn=turn)
            player = PLAYERS[team_to_player_idx[turn]]
            # Display information:
            if display:
                os.system("cls" if os.name == "nt" else "clear")
                self.display_board(self.board)
                print(self.board)
                print(f"{player.name} ({player.color}) rolled: {dice_roll}")

            # Get options and move player piece
            moveable_pieces = self.get_moveable_pieces(board=self.board, turn=turn, dice_roll=dice_roll)
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
                    turn=turn,
                    dice_roll=dice_roll,
                    piece2move=piece2move,
                )

                if self._detect_win(board=self.board, player=player):
                    break
            else:
                if display:
                    print("Sorry, you could not move any pieces this turn")
                    # sleep(1.5)

            # Give extra turn if globe is rolled
            if dice_roll != self.dice_globe:
                turn = self._get_next_player(teams_in_play, turn)
            else:
                if display:
                    print("You get an extra turn")

    def _add_tup(self, a: tuple, b: tuple) -> tuple:
        c = tuple((x + y for x, y in zip(a, b)))
        return c

    def display_board(self, board: np.array) -> None:
        board_abs = self.board_to_abs_pos(board=board)
        img_board = copy.deepcopy(self.img_board)

        for j in range(4):
            for i in range(4):
                val = board_abs[i][j]
                display_pos = self._add_tup(self.board_pos[val], self.plot_offset[i])
                img_board.paste(self.pieces[j], display_pos)

        plt.axis("off")
        plt.imshow(img_board)
        plt.show(block=False)


if __name__ == "__main__":
    PLAYERS = [
        Player("Zero", None),
        Player("One", None),
        Player("Two", None),
        Player("Three", None),
    ]
    ludo = Ludo()
    ludo.play(PLAYERS, display=True)
