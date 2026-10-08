# Tic-Tac-Toe: OOP Redesign

## Working agreement (important)
- The user is **learning OOP** and writes **all the code themselves, line by line**.
- Claude does **not** write or edit project code unless explicitly asked.
- Claude's role: explain concepts, answer "why", and **review** code the user writes (point out issues and explain them; the user makes the fix).
- Keep answers short and to the point when the user asks for "names only" or "no detail".

## Background
- The reference code is **only these three files** in `/Users/iqbal/Desktop/my_project/`:
  - `game.py`: `Board`, `Game` (logic; tested correct across all 255,168 possible games)
  - `interface.py`: curses `Interface` + `main()` loop
  - `tic_tac_toe_class_base.py`: an older print/input version. Use **only its `Interface` class** (`display_board`, `get_input`, `show_message`) as the base for the text interface. Ignore its `Game` and `Board`, which are replaced by `game.py`.
- Do not use any other file in that folder as a reference.
- About 80% of the new design is moving and renaming existing code; the rest is small new methods.

## Goal
Run `python main.py` → it asks which interface to use (curses or text) → the same `Game`/`Board` works with either interface.

## File structure
```
main.py               → asks user, creates Game + chosen interface, creates Controller, calls run()
game.py               → Game, Board
curses_interface.py   → CursesInterface, Cursor
text_interface.py     → TextInterface
controller.py         → Controller
```

## Entities (attributes and methods, names only)

### Board (game.py)
- Attributes: `size`, `cells`
- Methods: `is_valid_move`, `place_mark`, `get_cell`, `is_full`, `get_line_owner`

### Game (game.py)
- Constants: `IN_PROGRESS`, `WON`, `DRAW`
- Attributes: `board`, `players`, `current_player`, `status`, `winner`
- Methods: `make_move`, `check_winner`, `check_draw`, `switch_player`, `is_over`, `reset`

### Cursor (curses_interface.py)
- Attributes: `row`, `column`, `size`
- Methods: `move_up`, `move_down`, `move_left`, `move_right`, `selected_cell`

### CursesInterface (curses_interface.py)
- Attributes: `stdscr`, `window`, `cursor`, `box_height`, `box_width`, `window_height`, `window_width`
- Methods: shared methods (below) + `draw_board`, `draw_message`, `draw_cursor`, `refresh`, `check_terminal_size`

### TextInterface (text_interface.py)
- Methods: shared methods (below)

### Shared interface methods (every interface has these)
- `display(game)`: show the board and status
- `get_move(game)`: return a cell number 1–9, or "quit"
- `show_message(text)`

### Controller (controller.py)
- Attributes: `game`, `interface` (exactly ONE, whichever main.py chose), `running`
- Methods: `run`, `handle_move`, `quit`

## Relations
| From | To | Relationship |
|---|---|---|
| Controller | Game | has-a |
| Controller | interface | has-a (one, passed in by main.py) |
| Game | Board | has-a (owns it, creates it) |
| CursesInterface | Cursor | has-a (owns it) |
| Interfaces | Game | use, read-only (game passed into methods) |
| Controller | Board | none (only through Game) |
| Board | anything | none |

## Import rules
| File | Imports |
|---|---|
| `game.py` | nothing from the project |
| `curses_interface.py` | curses (+ `Game` only for constants) |
| `text_interface.py` | nothing (+ `Game` only for constants) |
| `controller.py` | nothing |
| `main.py` | everything |
- Imports only point downward. Never import upward (it causes circular imports and means the design has tangled).

## Key decisions and why
- **Board stores and reports, Game decides.** Board knows only facts about itself (valid cell? empty? full? line of same symbol?). Game owns the rules (turns, win, draw, game over). Test: "Would this be true if nobody were playing?" → Board.
- `place_mark` = put a symbol in a cell (Board). `make_move` = a full turn with rules (Game), which calls `place_mark`.
- `place_mark` returns True/False (a taken cell is a normal user mistake). `get_cell` raises an error on a bad cell (that can only be a code bug).
- `get_line_owner` must skip lines of empty cells. Game checks for a line **before** checking for a full board (the 9th move can be a win).
- **Composition, not inheritance:** a game *has a* board; it is not one. Inheritance would expose `place_mark` on Game and let callers skip the rules.
- **No Player class** (removed): players are plain symbols "X"/"O". Add a Player later only for names, scores, or an AI opponent.
- **No GameStatus class** (removed): status values are constants inside Game; `status` holds one of them. Replaces `game_over`.
- **Cursor lives inside the curses interface:** it exists only because of arrow keys. The text interface has no cursor.
- **Controller holds one interface** and calls only the shared methods, so any interface works. main.py makes the choice.
- `Board.size` (3) is the single source of truth for grid size; Cursor gets the number, not the board.
- Python style: group related classes per file, not one file per class.

## Bugs found in testing the original code (to fix during the rebuild)
1. **Flicker:** `refresh()` erases and repaints the whole screen on every keypress (~1,571 bytes per arrow press). Fix: `stdscr.noutrefresh()` + `window.noutrefresh()` + `curses.doupdate()`, which cut it to 4 bytes.
2. **Small-terminal crash:** `_curses.error` when the terminal has fewer than ~12 rows or ~31 columns. Fix: `check_terminal_size` in every refresh. Also, `curses.newwin` can fail if the terminal is smaller than the window.
3. Minor: `switch_player` hardcodes "X"/"O" (should use `players`); no feedback when a taken cell is chosen; no restart; non-int input raises TypeError in Board.
- Note for testing curses in a pty: arrow keys are sent as `ESC O A/B/C/D` (application mode), not `ESC [ A/B/C/D`.

## Learning plan (one step at a time; run the game and commit after each)
0. `git init` and commit a starting point.
1. **Board**: rename/add methods; test with `test_board.py` (no curses).
2. **Game**: constants + `status`, new `make_move`, `is_over`, `reset`; test with `test_game.py`.
3. **Cursor**: extract it from the interface; test with `test_cursor.py`.
4. **CursesInterface**: drawing only; shared methods; owns Cursor.
5. **TextInterface**: adapt the `Interface` from `tic_tac_toe_class_base.py` (`display_board` → `display`, `get_input` → `get_move`, `show_message` stays). It must receive `game` instead of creating or storing its own board, and read cells through `get_cell`. Note: the old board stored "1"–"9" in empty cells; the new board stores "", so the text interface should show the cell number itself when `get_cell` returns "".
6. **Controller + main.py**: main asks which interface, then runs.
7. **Fixes**: flicker, terminal-size check.

Rules while coding: say a method's job in one sentence before writing it; ask "whose data is this?" before adding an attribute; test without curses whenever possible.

## Progress
- [ ] Step 0
- [ ] Step 1 Board
- [ ] Step 2 Game
- [ ] Step 3 Cursor
- [ ] Step 4 CursesInterface
- [ ] Step 5 TextInterface
- [ ] Step 6 Controller + main.py
- [ ] Step 7 Fixes
