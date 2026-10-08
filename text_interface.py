from game import Game


class TextInterface:
    def display(self, game: Game) -> None:
        # An empty cell shows its own number, so the player knows what to type
        cells = []
        for cell in range(1, 10):
            value = game.board.get_cell(cell)
            cells.append(value if value != "" else str(cell))

        print(f" {cells[0]} | {cells[1]} | {cells[2]} ")
        print("---+---+---")
        print(f" {cells[3]} | {cells[4]} | {cells[5]} ")
        print("---+---+---")
        print(f" {cells[6]} | {cells[7]} | {cells[8]} ")

        if game.status == Game.WON:
            self.show_message(f"Player {game.winner} wins!")
        elif game.status == Game.DRAW:
            self.show_message("It's a draw!")

    def get_move(self, game: Game):
        if game.is_over():
            input("Press Enter to exit: ")
            return "quit"

        while True:
            text = input(f"{game.current_player}, enter your move (1-9) or q to quit: ")

            if text.strip().lower() == "q":
                return "quit"

            try:
                return int(text)
            except ValueError:
                self.show_message("Please enter a valid integer between 1 and 9.")

    def show_message(self, text: str) -> None:
        print(text)
