from typing import Optional


class Board:
    def __init__(self):
        self.size = 3
        self.cells = [""] * (self.size * self.size)


    def is_valid_move(self, move: int) -> bool:
        if not isinstance(move, int) or move < 1 or move > 9:
            return False

        return self.cells[move - 1] == ""


    def place_mark(self, move: int, player: str) -> bool:
        if not self.is_valid_move(move):
            return False

        self.cells[move - 1] = player
        return True


    def get_cell(self, move: int) -> str:
        if not isinstance(move, int) or move < 1 or move > 9:
            raise ValueError(f"Invalid cell: {move!r} (must be 1-9)")

        return self.cells[move - 1]


    def get_line_owner(self) -> Optional[str]:
        winning_combinations = [
            (0, 1, 2),
            (3, 4, 5),
            (6, 7, 8),
            (0, 3, 6),
            (1, 4, 7),
            (2, 5, 8),
            (0, 4, 8),
            (2, 4, 6),
        ]

        for first, second, third in winning_combinations:
            if (
                self.cells[first] != ""
                and self.cells[first] == self.cells[second] == self.cells[third]
            ):
                return self.cells[first]

        return None


    def is_full(self) -> bool:
        return all(cell != "" for cell in self.cells)

class Game:
    IN_PROGRESS = "in_progress"
    WON = "won"
    DRAW = "draw"

    def __init__(self):
        self.players = ["X", "O"]
        self.board = Board()
        self.current_player = self.players[0]
        self.status = Game.IN_PROGRESS
        self.winner = None


    def reset(self) -> None:
        self.board = Board()
        self.current_player = self.players[0]
        self.status = Game.IN_PROGRESS
        self.winner = None


    def make_move(self, move: int) -> bool:
        if self.is_over():
            return False

        if not self.board.place_mark(move, self.current_player):
            return False

        # Check for a line first: the 9th move can be a win
        self.winner = self.check_winner()
        if self.winner:
            self.status = Game.WON
            return True

        if self.check_draw():
            self.status = Game.DRAW
            return True

        self.switch_player()
        return True


    def check_winner(self) -> Optional[str]:
        return self.board.get_line_owner()


    def check_draw(self) -> bool:
        return self.check_winner() is None and self.board.is_full()


    def switch_player(self) -> None:
        if self.current_player == "X":
            self.current_player = "O"
        else:
            self.current_player = "X"


    def is_over(self) -> bool:
        return self.status != Game.IN_PROGRESS
