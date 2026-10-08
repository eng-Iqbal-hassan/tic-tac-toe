import curses

from game import Game
from controller import Controller
from curses_interface import CursesInterface
from text_interface import TextInterface


def ask_interface() -> str:
    while True:
        choice = input("Choose an interface: 1) curses  2) text: ").strip().lower()

        if choice in ("1", "curses"):
            return "curses"
        if choice in ("2", "text"):
            return "text"

        print("Please enter 1 or 2.")


def run_curses(stdscr) -> None:
    # Make the terminal cursor visible
    curses.curs_set(1)

    game = Game()
    interface = CursesInterface(stdscr, game.board.size)
    Controller(game, interface).run()


def main() -> None:
    choice = ask_interface()

    if choice == "curses":
        curses.wrapper(run_curses)
    else:
        game = Game()
        interface = TextInterface()
        Controller(game, interface).run()


if __name__ == "__main__":
    main()
