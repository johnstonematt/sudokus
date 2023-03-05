import logging
from typing import List, Iterator, TypeAlias, Tuple
from enum import Enum


Puzzle: TypeAlias = List[List[int]]
Board: TypeAlias = List[List[List[int]]]

logger = logging.getLogger(__name__)


class SudokuError(Exception):
    """
    Raised when there are no possible numbers for a given cell.
    """


class Subset(Enum):
    """
    Different sections of a sudoku.
    """

    ROW = "ROW"
    COLUMN = "COLUMN"
    BLOCK = "BLOCK"

    def axis(self) -> int:
        match self:
            case Subset.ROW:
                return 0

            case Subset.COLUMN:
                return 1

            case Subset.BLOCK:
                raise NotImplementedError(f"Subset {self} has no axis.")

    def index(self, location: Tuple[int, int]) -> int:
        match self:
            case Subset.ROW:
                return location[0]

            case Subset.COLUMN:
                return location[1]

            case Subset.BLOCK:
                return find_block_index(location=location)


def parse_puzzle(
    unparsed_puzzle: List[List[int | str]] | str,
) -> Puzzle:
    puzzle = []
    # handle string case:
    if isinstance(unparsed_puzzle, str):
        str_rows = unparsed_puzzle.split("\n")
        for str_row in str_rows:
            if not str_row:
                continue

            puzzle_row = []
            for char in str_row:
                if char.isdigit():
                    puzzle_row.append(int(char))

                else:
                    puzzle_row.append(0)

            puzzle.append(puzzle_row)

    # now hande list case:
    for unparsed_row in unparsed_puzzle:
        puzzle_row = []
        for item in unparsed_row:
            if isinstance(item, str):
                if item.isdecimal():
                    item = int(item)

                else:
                    item = 0

            if item not in (0, 1, 2, 3, 4, 5, 6, 7, 8, 9):
                raise ValueError(f"Unrecognised input: {item}")

            puzzle_row.append(item)

        puzzle.append(puzzle_row)

    return puzzle


def subset_coordinates(subset: Subset, index: int) -> Iterator[Tuple[int, int]]:
    match subset:
        case Subset.ROW:
            for i in range(9):
                yield index, i

        case Subset.COLUMN:
            for i in range(9):
                yield i, index

        case Subset.BLOCK:
            corner_row, corner_column = find_corner_row_and_column(block_index=index)
            for i in range(corner_row, corner_row + 3):
                for j in range(corner_column, corner_column + 3):
                    yield i, j

        case _:
            raise NotImplementedError(f"Unrecognised subset: {subset}")


def sudoku_coordinates() -> Iterator[Tuple[int, int]]:
    for x in range(9):
        for y in range(9):
            yield x, y


def find_corner_row_and_column(block_index: int) -> Tuple[int, int]:
    return 3 * (block_index // 3), 3 * (block_index % 3)


def find_adjacent_blocks(block_index: int, direction: Subset) -> Tuple[int, int]:
    match direction:
        case Subset.ROW:
            match block_index % 3:
                case 0:
                    return block_index + 1, block_index + 2

                case 1:
                    return block_index - 1, block_index + 1

                case 2:
                    return block_index - 2, block_index - 1

                case _:
                    raise ValueError(f"Nonsensical block index: {block_index}")

        case Subset.COLUMN:
            match block_index // 3:
                case 0:
                    return block_index + 3, block_index + 6

                case 1:
                    return block_index - 3, block_index + 3

                case 2:
                    return block_index - 6, block_index - 3

                case _:
                    raise ValueError(f"Nonsensical block index: {block_index}")

        case Subset.BLOCK:
            raise ValueError(f"{Subset.BLOCK} does not make sense as a direction.")


def find_block_index(location: Tuple[int, int]) -> int:
    return 3 * (location[0] // 3) + (location[1] // 3)
