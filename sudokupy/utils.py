import random
import logging
from enum import Enum
from typing import List, Iterator, TypeAlias, Tuple, Optional


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
            for i in sudoku_indices():
                yield index, i

        case Subset.COLUMN:
            for i in sudoku_indices():
                yield i, index

        case Subset.BLOCK:
            corner_row, corner_column = find_corner_row_and_column(block_index=index)
            for i in range(corner_row, corner_row + 3):
                for j in range(corner_column, corner_column + 3):
                    yield i, j

        case _:
            raise NotImplementedError(f"Unrecognised subset: {subset}")


def sudoku_coordinates() -> Iterator[Tuple[int, int]]:
    for x in sudoku_indices():
        for y in sudoku_indices():
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


def sudoku_indices() -> Iterator[int]:
    for index in range(9):
        yield index


def sudoku_numbers() -> Iterator[int]:
    for number in range(1, 10):
        yield number


def empty_puzzle() -> Puzzle:
    return [[0 for _ in sudoku_indices()] for __ in sudoku_indices()]


def range_random(start: int, end: int, n: Optional[int] = None) -> List[int]:
    if n is None:
        n = end - start

    if n > end - start:
        raise ValueError(
            f"Can't sample {n} from {start} -> {end} (only {end - start} available)."
        )

    ordered_numbers = [i for i in range(start, end)]
    random_numbers = []
    for _ in range(n):
        index = random.randint(0, len(ordered_numbers) - 1)
        random_numbers.append(ordered_numbers.pop(index))

    return random_numbers


def sudoku_coordinates_random() -> Iterator[Tuple[int, int]]:
    for x in range_random(0, 9):
        for y in range_random(0, 9):
            yield x, y


def generate_diagonal_puzzle() -> Puzzle:
    puzzle: Puzzle = [[0 for _ in sudoku_indices()] for __ in sudoku_indices()]
    # can randomly fill the blocks of the leading diagonal:
    for block_index in (0, 4, 8):
        random_numbers = [rn for rn in range_random(1, 10)]
        i = 0
        for x, y in subset_coordinates(subset=Subset.BLOCK, index=block_index):
            puzzle[x][y] = random_numbers[i]
            i += 1

    return puzzle


def block_indices_to_axial_indices(
    block_index: int, block_subindex: int
) -> Tuple[int, int]:
    corner_row, corner_column = find_corner_row_and_column(block_index=block_index)
    extra_rows = block_subindex // 3
    extra_columns = block_subindex % 3
    return corner_row + extra_rows, corner_column + extra_columns
