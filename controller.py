class Controller:
    def __init__(self, game, interface):
        self.game = game
        self.interface = interface
        self.running = True

    def run(self) -> None:
        while self.running:
            self.interface.display(self.game)
            move = self.interface.get_move(self.game)

            if move == "quit":
                self.quit()
            else:
                self.handle_move(move)

    def handle_move(self, move: int) -> None:
        if self.game.is_over():
            return

        if not self.game.make_move(move):
            self.interface.show_message("That cell is taken or not valid. Try again.")

    def quit(self) -> None:
        self.running = False
