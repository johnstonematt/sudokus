# Sudokus

A Python repo for solving and generating [Sudoku puzzles](https://en.wikipedia.org/wiki/Sudoku), 
inspired by the following [LeetCode problem](https://leetcode.com/problems/sudoku-solver/).

In general, I am prioritising logical conciseness over pure performance 
(i.e., runtime, memory usage, etc.), but within reason of course.

## Solving Techniques

The `Sudoku` class employs two solving techniques, one a purely "deterministic" technique in which a number is 
only entered if the program is 100% certain that it is correct, and another which involves making a guess and trying 
to solve from there (reverting on the guess if the puzzle turns out to be unsolvable).

When generating sudoku puzzles (such as the unfinished puzzle one might find in a newspaper), the goal is to generate 
a puzzle of sufficient difficulty which can be solved deterministically.

### Input Format

The program reads a Sudoku as a row-by-row array of integers, where 0 represents and empty space.

```python
sudoku_puzzle = [
    [5, 3, 0, 0, 7, 0, 0, 0, 0],
    [6, 0, 0, 1, 9, 5, 0, 0, 0],
    [0, 9, 8, 0, 0, 0, 0, 6, 0],
    [8, 0, 0, 0, 6, 0, 0, 0, 3],
    [4, 0, 0, 8, 0, 3, 0, 0, 1],
    [7, 0, 0, 0, 2, 0, 0, 0, 6],
    [0, 6, 0, 0, 0, 0, 2, 8, 0],
    [0, 0, 0, 4, 1, 9, 0, 0, 5],
    [0, 0, 0, 0, 8, 0, 0, 7, 9]
]
```

