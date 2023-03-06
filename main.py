import os
import sys
import json
import logging
from typing import List

from dotenv import load_dotenv

from sudokupy.sudoku import Sudoku
from sudokupy.utils import Puzzle, generate_diagonal_puzzle


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


def from_json() -> None:
    with open("puzzles.json", "r") as file:
        puzzles: List[Puzzle] = json.load(file)

    sudoku = Sudoku(puzzle=puzzles[1])
    try:
        sudoku.solve_sudoku(allow_guessing=True)

    except Exception:
        print(sudoku)
        raise


def generated() -> None:
    puzzle = generate_diagonal_puzzle()
    sudoku = Sudoku(puzzle=puzzle)
    try:
        sudoku.solve_sudoku(allow_guessing=True)

    except Exception:
        print(sudoku)
        raise


if __name__ == "__main__":
    generated()
