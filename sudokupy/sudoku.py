import logging
from typing import List, Tuple, Set, Optional

from sudokupy.utils import (
    Subset,
    SudokuError,
    Board,
    Puzzle,
    find_block_index,
    find_adjacent_blocks,
    sudoku_coordinates,
    subset_coordinates,
    sudoku_indices,
    sudoku_numbers,
)

logger = logging.getLogger(__name__)


class Sudoku:
    """
    A sudoku puzzle.
    """

    def __init__(self, board: Board) -> None:
        """
        :param board: An array of possibilities for all sudoku cells.
        """
        self.board = board

    @classmethod
    def from_puzzle(cls, puzzle: Puzzle) -> "Sudoku":
        board = []
        for puzzle_row in puzzle:
            board_row = []
            for item in puzzle_row:
                board_item: List[int] = (
                    [1, 2, 3, 4, 5, 6, 7, 8, 9] if item == 0 else [item]
                )
                board_row.append(board_item)

            board.append(board_row)

        return Sudoku(board=board)

    def solve_sudoku(self, allow_guessing: bool) -> None:
        logger.info("Solving the following sudoku:")
        print(self)
        self.solve_deterministically()

        if self._is_complete():
            logger.info("Completed sudoku:")
            print(self)
            if not self._is_correct():
                raise SudokuError("Sudoku is not correct.")

            return

        # the sudoku wasn't deterministically solvable:
        logger.info("Can't solve sudoku deterministically, this is how far I got:")
        print(self)
        if not allow_guessing:
            logger.info("Not allowed to guess, so this is me done.")
            return

        self._solve_with_guessing(current_guess_locations=[])

        if self._is_complete():
            logger.info("Completed sudoku:")
            print(self)
            if not self._is_correct():
                raise SudokuError("Sudoku is not correct.")

            return

        else:
            raise Exception("Sudoku is not complete, strange ....")

    def solve_deterministically(self) -> None:
        """
        Solve the sudoku without making any guesses.

        :return: Nothing.
        """
        while True:
            refined_successfully = self.refine_possibilities()
            applied_successfully = self.apply_n_numbers_in_n_spaces()
            # if neither methods yielded any progress, then we are done (either complete, or just stuck)
            if not (refined_successfully or applied_successfully):
                break

    def refine_possibilities(self) -> bool:
        """
        Apply standard 'is number possible?' to every possibility on the board until we stop making progress.

        :return: Whether this method successfully made progress.
        """
        updated = False
        while True:
            # this is just a tag to break/continue the outer while-loop from within the nested loops:
            refined = False

            for location in sudoku_coordinates():
                for possible_number in self[location]:
                    if not self._is_number_possible(
                        number=possible_number, location=location
                    ):
                        # if we find that a number on the board is not possible, we remove it from the board
                        # and then restart the board-iteration:
                        self[location].pop(self[location].index(possible_number))
                        updated = True
                        refined = True
                        break

                # if there are no possible numbers in this location, something wrong has happened:
                if not self[location]:
                    raise SudokuError(f"No possible numbers for cell {location}.")

                # break back to continue the while-loop if we made a refinement:
                if refined:
                    break

            # start again if we made a refinement:
            if refined:
                continue

            # this code runs if we ran through the whole sudoku without making a refinement:
            break

        return updated

    def apply_n_numbers_in_n_spaces(self) -> bool:
        """
        If there are n numbers that can all go (exclusively) into n spaces,
        then no other number can go in one of those spaces.

        :return: Whether the method reduced the possibilities.
        """
        for subset in Subset:
            for index in sudoku_indices():
                for number in sudoku_numbers():
                    # this is just a flag used to break this loop from within the nested loop:
                    skip_number = False

                    number_locations = self._possible_locations_in_subset(
                        subset=subset, index=index, number=number
                    )
                    n = len(number_locations)
                    numbers = [number]
                    for other_number in sudoku_numbers():
                        # only look at other numbers:
                        if other_number == number:
                            continue

                        # we are looking for len(numbers) == n, so if len(numbers) > n, we are too far:
                        if len(numbers) > n:
                            skip_number = True
                            break

                        other_locations = self._possible_locations_in_subset(
                            subset=subset, index=index, number=other_number
                        )
                        # check equality of location sets by first comparing lengths and then literal contents:
                        if len(other_locations) != n or any(
                            location not in number_locations
                            for location in other_locations
                        ):
                            continue

                        # other_number has the same possible locations as number, so we can add it:
                        numbers.append(other_number)

                    if skip_number:
                        continue

                    # this is the condition we are looking for:
                    if len(numbers) == n:
                        # go ahead and remove any other numbers from these locations:
                        for location in number_locations:
                            if len(self[location]) > n:
                                self[location] = numbers
                                return True

        return False

    def _solve_with_guessing(
        self, current_guess_locations: List[Tuple[int, int]]
    ) -> None:
        # first check to run a deterministic solve (have to put this here so that the recursion works properly):
        if current_guess_locations:
            self.solve_deterministically()
            if self._is_complete():
                return

        guess_location = self._find_best_guess_location(
            current_guess_locations=current_guess_locations
        )
        current_guess_locations.append(guess_location)
        guesses = self[guess_location].copy()
        logger.info(f"Guessing at {guess_location} {guesses}.")
        # save state then start guessing:
        saved_board = self._copy_board()
        for guess in guesses:
            logger.info(f"Guessing {guess} -> {guess_location}.")
            self[guess_location] = [guess]
            try:
                self._solve_with_guessing(
                    current_guess_locations=current_guess_locations,
                )

            except SudokuError:
                # the guess was obviously wrong, so undo changes and go to the next guess
                logger.info(
                    f"{guess} -> {guess_location} must've been wrong, reverting."
                )
                self.board = saved_board
                continue

            # the guess was good and we finished:
            if self._is_complete():
                return

        # if we get here, that means we tried every possibility in the guess location and none of them worked:
        raise SudokuError(
            f"No valid guesses at {guess_location}, something must have went wrong."
        )

    def _is_number_possible(
        self,
        number: int,
        location: Tuple[int, int],
    ) -> int:
        # just in case, we make sure to never add an extra possibility (only remove):
        if number not in self[location]:
            logger.warning(f"Checking to add possible {number} to {location}.")
            return False

        # if we have already 'filled this number in', we just do a naive-check to make sure it's not a mistake:
        if self[location] == [number]:
            for subset in Subset:
                index = subset.index(location=location)
                if self._subset_contains_number(
                    subset=subset,
                    index=index,
                    number=number,
                    location=location,
                ):
                    logger.debug(
                        f"{number} can't go into {location} because it's already in {subset} {index}."
                    )
                    return False

            return True

        # first check if it's already present in the block:
        already_in_block = self._block_already_contains_number(
            number=number, location=location
        )
        if already_in_block:
            logger.debug(
                f"{number} can't go at {location} because it's already in the block."
            )
            return False

        # if it's not ruled out by block, check axial ruling:
        ruled_out = self._axial_ruling(number=number, location=location)
        if ruled_out:
            logger.debug(f"{number} is axially ruled out from {location}.")
            return False

        else:
            logger.debug(f"{number} can maybe go at {location}.")
            return True

    def _axial_ruling(
        self,
        number: int,
        location: Tuple[int, int],
    ) -> bool:
        """
        Check if a number is ruled out from a location by presence (either real or inferred) in
        another block but same row/column.

        :param number: The number to check.
        :param location: The location to check.
        :return: Whether the number is ruled out (i.e., definitely not possible) from the location.
        """
        block_index = find_block_index(location=location)
        for direction in (Subset.ROW, Subset.COLUMN):
            index = direction.index(location=location)
            all_possible_indices = set()
            for adjacent_block_index in find_adjacent_blocks(
                block_index=block_index,
                direction=direction,
            ):
                possible_indices = self._possible_indices_in_block(
                    block_index=adjacent_block_index,
                    axis=direction.axis(),
                    number=number,
                )
                if possible_indices == {index}:
                    return True

                all_possible_indices |= possible_indices

            if len(all_possible_indices) == 2 and index in all_possible_indices:
                return True

        return False

    def _is_correct(self) -> bool:
        """
        Check if a sudoku is complete and correct.

        :return: Whether the sudoku is correct.
        """
        for subset in Subset:
            for index in sudoku_indices():
                for number in sudoku_numbers():
                    if not self._subset_contains_number(
                        subset=subset, index=index, number=number, location=None
                    ):
                        logger.warning(f"{subset} {index} does not contain a {number}")
                        return False

        return True

    def _is_complete(self) -> bool:
        """
        Check if a sudoku is complete, i.e., all cells are filled in.

        :return: Whether the sudoku is complete.
        """
        for location in sudoku_coordinates():
            if len(self[location]) != 1:
                return False

        return True

    def _find_best_guess_location(
        self, current_guess_locations: List[Tuple[int, int]]
    ) -> Tuple[int, int]:
        # used to track the min number of options in a cell across the whole board:
        min_options = 10

        # loop through, looking for a cell with only 2 options, and update min_options in the process:
        for location in sudoku_coordinates():
            if location in current_guess_locations:
                continue

            n = len(self[location])
            if n == 2:
                return location

            if 1 < n < min_options:
                min_options = n

        # if we get here, there are no cells with only 2 options, so we take one with min_options:
        for location in sudoku_coordinates():
            if len(self[location]) == min_options:
                return location

        raise Exception("No guesses, maybe sudoku is complete?")

    def _possible_locations_in_subset(
        self, subset: Subset, index: int, number: int
    ) -> List[Tuple[int, int]]:
        possible_locations = []
        for location in subset_coordinates(subset=subset, index=index):
            if number in self[location]:
                possible_locations.append(location)

        return possible_locations

    def _possible_indices_in_block(
        self, block_index: int, axis: int, number: int
    ) -> Set[int]:
        possible_indices = set()
        for location in subset_coordinates(subset=Subset.BLOCK, index=block_index):
            if number in self[location]:
                possible_indices |= {location[axis]}

        return possible_indices

    def _subset_contains_number(
        self,
        subset: Subset,
        index: int,
        number: int,
        location: Optional[Tuple[int, int]],
    ) -> bool:
        for other_location in subset_coordinates(subset=subset, index=index):
            # if a location is specified, then we are looking to see if the number exists somewhere else:
            if location is not None and other_location == location:
                continue

            if self[other_location] == [number]:
                return True

        return False

    def _block_already_contains_number(
        self, number: int, location: Tuple[int, int]
    ) -> bool:
        block_index = find_block_index(location=location)
        for other_location in subset_coordinates(
            subset=Subset.BLOCK,
            index=block_index,
        ):
            if other_location == location:
                continue

            if self[other_location] == [number]:
                logger.debug(
                    f"There is already a {number} in block {block_index} at {location}."
                )
                return True

        logger.debug(f"There is no {number} in block {block_index}.")
        return False

    def _copy_board(self) -> Board:
        return [
            [cell_possibilities.copy() for cell_possibilities in board_row]
            for board_row in self.board
        ]

    def __getitem__(self, item: Tuple[int, int]) -> List[int]:
        return self.board[item[0]][item[1]]

    def __setitem__(self, key: Tuple[int, int], value: List[int]) -> None:
        self.board[key[0]][key[1]] = value

    def __str__(self) -> str:
        horizontal_line = "-------------------------"
        sudoku_str = ""
        for x in sudoku_indices():
            if x % 3 == 0:
                sudoku_str += f"{horizontal_line}\n"

            line = ""
            for y in sudoku_indices():
                if y % 3 == 0:
                    line += "| "

                if len(self[(x, y)]) == 1:
                    line += f"{self[(x, y)][0]}"
                else:
                    line += " "

                line += " "

            line += "|"
            sudoku_str += f"{line}\n"

        sudoku_str += horizontal_line
        return sudoku_str

    def __repr__(self) -> str:
        return str(self)
