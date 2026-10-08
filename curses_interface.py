import curses

from game import Game


class Cursor:
    def __init__(self, size: int):
        self.size = size
        self.row = 0
        self.column = 0

    def move_up(self) -> None:
        if self.row > 0:
            self.row -= 1

    def move_down(self) -> None:
        if self.row < self.size - 1:
            self.row += 1

    def move_left(self) -> None:
        if self.column > 0:
            self.column -= 1
        elif self.row > 0:
            # First column -> last column of the previous row
            self.row -= 1
            self.column = self.size - 1

    def move_right(self) -> None:
        if self.column < self.size - 1:
            self.column += 1
        elif self.row < self.size - 1:
            # Last column -> first column of the next row
            self.column = 0
            self.row += 1

    def selected_cell(self) -> int:
        return self.row * self.size + self.column + 1


class CursesInterface:
    def __init__(self, stdscr, size: int):
        self.stdscr = stdscr
        self.cursor = Cursor(size)

        # Dimension of each individual box
        self.box_height = 3
        self.box_width = 5

        # Window dimensions
        self.window_height = size * self.box_height + 1  # 10
        self.window_width = size * self.box_width + 1  # 16

        # Create the board at the top left
        self.window = curses.newwin(self.window_height, self.window_width, 0, 0)

        # Required for arrow keys
        self.window.keypad(True)

        # One-off message (e.g. "cell taken"), shown until the next key press
        self.message = ""

    # Shared interface methods (called by the Controller)

    def display(self, game: Game) -> None:
        self.refresh(game)

    def get_move(self, game: Game):
        while True:
            key = self.window.getch()

            if key == ord("q"):
                return "quit"

            # When the game has ended, only q does anything
            if game.is_over():
                continue

            if key == curses.KEY_RIGHT:
                self.cursor.move_right()
            elif key == curses.KEY_LEFT:
                self.cursor.move_left()
            elif key == curses.KEY_DOWN:
                self.cursor.move_down()
            elif key == curses.KEY_UP:
                self.cursor.move_up()
            elif key in (10, 13, curses.KEY_ENTER, ord(" ")):
                return self.cursor.selected_cell()

            self.refresh(game)

    def show_message(self, text: str) -> None:
        self.message = text

    # Curses-only methods

    def draw_board(self, game: Game) -> None:
        size = self.cursor.size

        # Clear previous board
        self.window.erase()

        # Draw outer board
        self.window.border()

        # Horizontal lines
        for row in range(1, size):
            y = row * self.box_height
            self.window.hline(y, 1, curses.ACS_HLINE, self.window_width - 2)

        # Vertical lines
        for column in range(1, size):
            x = column * self.box_width
            self.window.vline(1, x, curses.ACS_VLINE, self.window_height - 2)

        # Intersections
        for row in range(1, size):
            for column in range(1, size):
                y = row * self.box_height
                x = column * self.box_width
                self.window.addch(y, x, curses.ACS_PLUS)

        # Draw the symbols
        for cell in range(1, size * size + 1):
            value = game.board.get_cell(cell)
            if value == "":
                continue

            row = (cell - 1) // size
            column = (cell - 1) % size

            # Position inside the box
            y = row * self.box_height + 1
            x = column * self.box_width + 2
            self.window.addstr(y, x, value)

    def draw_message(self, game: Game) -> None:
        message_y = self.window_height + 1

        # Clear the previous message
        self.stdscr.move(message_y, 0)
        self.stdscr.clrtoeol()

        if game.status == Game.WON:
            message = f"Player {game.winner} wins! Press q to quit"
        elif game.status == Game.DRAW:
            message = "It's a draw. Press q to quit"
        else:
            message = f"Player {game.current_player}'s turn"

        self.stdscr.addstr(message_y, 0, message)

        if self.message:
            self.stdscr.addstr(message_y + 1, 0, self.message)
            self.message = ""

    def draw_cursor(self) -> None:
        y = self.cursor.row * self.box_height + 1
        x = self.cursor.column * self.box_width + 2
        self.window.move(y, x)

    def refresh(self, game: Game) -> None:
        # Clear the whole terminal
        self.stdscr.erase()

        # Draw message
        self.draw_message(game)
        self.stdscr.refresh()

        # Draw the board
        self.draw_board(game)

        # Move the cursor to the selected box
        self.draw_cursor()

        self.window.refresh()
