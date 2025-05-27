import random

def print_board(board):
    print("\n")
    for row in board:
        print(" | ".join(row))
        print("-" * 5)
    print("\n")

def check_winner(board, player):
    for i in range(3):
        if all(cell == player for cell in board[i]):
            return True
        if all(board[j][i] == player for j in range(3)):
            return True
    if all(board[i][i] == player for i in range(3)):
        return True
    if all(board[i][2 - i] == player for i in range(3)):
        return True
    return False

def is_draw(board):
    return all(cell in ['X', 'O'] for row in board for cell in row)

def get_empty_positions(board):
    return [(r, c) for r in range(3) for c in range(3) if board[r][c] not in ['X', 'O']]

def computer_move(board):
    empty = get_empty_positions(board)
    return random.choice(empty)

def tic_tac_toe_vs_computer():
    print("Welcome to Tic Tac Toe! (You: X | Computer: O)")
    while True:
        board = [["1", "2", "3"], ["4", "5", "6"], ["7", "8", "9"]]
        human = "X"
        computer = "O"
        current_player = human
        game_over = False

        while not game_over:
            print_board(board)

            if current_player == human:
                move = input("Your move (1-9): ")

                if not move.isdigit() or int(move) < 1 or int(move) > 9:
                    print("Invalid input. Try 1-9.")
                    continue

                move = int(move) - 1
                row, col = divmod(move, 3)

                if board[row][col] in ["X", "O"]:
                    print("Position already taken.")
                    continue
            else:
                print("Computer's turn...")
                row, col = computer_move(board)

            board[row][col] = current_player

            if check_winner(board, current_player):
                print_board(board)
                if current_player == human:
                    print("🎉 You win!")
                else:
                    print("💻 Computer wins!")
                game_over = True
            elif is_draw(board):
                print_board(board)
                print("It's a draw!")
                game_over = True
            else:
                current_player = computer if current_player == human else human

        replay = input("Play again? (y/n): ").lower()
        if replay != 'y':
            break

if __name__ == "__main__":
    tic_tac_toe_vs_computer()
