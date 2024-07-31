import numpy as np
import time

# Moves for the knight
move_x = [2, 1, -1, -2, -2, -1, 1, 2]
move_y = [1, 2, 2, 1, -1, -2, -2, -1]


def validate_move(board, row, col):
    # check if it is out of the board or already visited
    return (
        0 <= row < board.shape[0] and 0 <= col < board.shape[1] and board[row, col] == 0
    )


def get_degree(board, row, col):
    count = 0
    for i in range(8):
        new_x = row + move_x[i]
        new_y = col + move_y[i]
        if validate_move(board, new_x, new_y):
            count += 1
    return count



def solve(board, row, col, move_counter):
    if move_counter == board.size + 1:  # Adjusted for 1-based move counter
        return True

    # Generate all valid moves
    candidates = []
    for i in range(8):
        new_x = row + move_x[i]
        new_y = col + move_y[i]
        if validate_move(board, new_x, new_y):
            candidates.append((get_degree(board, new_x, new_y), new_x, new_y))

    # Sort candidates based on the degree (Warnsdorff's heuristic)
    candidates.sort(key=lambda x: x[0])

    # Try all next moves
    for _, next_x, next_y in candidates:
        board[next_x, next_y] = move_counter
        if solve(board, next_x, next_y, move_counter + 1):
            return True
        board[next_x, next_y] = 0  # Backtrack

    return False


def knights_tour(n, m, start_row, start_col):
    # Start timing
    start_time = time.time()

    # Initialize the board
    board = np.zeros((n, m))
    board[start_row, start_col] = 1

    # Solve the Knight's Tour problem
    if solve(board, start_row, start_col, 2):
        print("Solution found")
    else:
        print("No solution exists")

    # End timing
    end_time = time.time()
    elapsed_time = end_time - start_time

    print("Elapsed time:", elapsed_time, "seconds")
    print(board)


# Example usage with an 8x8 board starting at position (0, 0)
n = 8
m = 8
start_row = 0
start_col = 0

knights_tour(n, m, start_row, start_col)
