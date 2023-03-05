import os
import sys
import json
import logging
from typing import List

from dotenv import load_dotenv

from sudokupy.sudoku import Sudoku
from sudokupy.utils import Puzzle


load_dotenv(".env.local")


# initialise logger:
logging.basicConfig(
    format='{"level": "%(levelname)s", "time": "%(asctime)s", "message": %(message)s"}',
    level=os.environ["LOG_LEVEL"],
    force=True,
    handlers=[
        logging.StreamHandler(sys.stdout),
    ],
)


def main() -> None:
    with open("puzzles.json", "r") as file:
        puzzles: List[Puzzle] = json.load(file)

    sudoku = Sudoku.from_puzzle(puzzle=puzzles[1])
    try:
        sudoku.solve_sudoku(allow_guessing=True)

    except Exception:
        print(sudoku)
        raise


if __name__ == "__main__":
    main()
