import os
from typing import List
import time
import subprocess

try:
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
except NameError:
    # Xảy ra nếu chạy tương tác hoặc __file__ không được định nghĩa
    SCRIPT_DIR = os.getcwd() # Lấy thư mục làm việc hiện tại làm dự phòng
    print(f"Cảnh báo: Không thể xác định __file__, sử dụng thư mục hiện tại: {SCRIPT_DIR}")

SEVER_DIR = os.path.join(SCRIPT_DIR) # Đường dẫn đến thư mục sever
EXE_NAME = "c4solver.exe"
EXE_PATH = os.path.join(SEVER_DIR, EXE_NAME)
BOOK_PATH = os.path.join(SEVER_DIR, "7x6.book")

sequence = ""
previous_board = [[0 for _ in range(7)] for _ in range(6)]

def is_game_over(board: List[List[int]]) -> bool:
    # Check for full board (draw)
    if all(cell != 0 for row in board for cell in row):
        return True

    # Check for 4 in a row (horizontal, vertical, diagonal)
    height = len(board)
    width = len(board[0])
    for r in range(height):
        for c in range(width):
            if board[r][c] == 0:
                continue
            player = board[r][c]
            # Check right
            if c <= width - 4 and all(board[r][c+i] == player for i in range(4)):
                return True
            # Check down
            if r <= height - 4 and all(board[r+i][c] == player for i in range(4)):
                return True
            # Diagonal down-right
            if r <= height - 4 and c <= width - 4 and all(board[r+i][c+i] == player for i in range(4)):
                return True
            # Diagonal up-right
            if r >= 3 and c <= width - 4 and all(board[r-i][c+i] == player for i in range(4)):
                return True
    return False

def reset_state():
    global sequence, previous_board
    sequence = ""
    previous_board = [[0 for _ in range(7)] for _ in range(6)]

def convert_board_to_movesequence(current_board: List[List[int]]) -> str:
    """
    Chuyển đổi trạng thái bàn cờ (board) 2D thành chuỗi nước đi (move_sequence).
    Trả về chuỗi rỗng nếu board không hợp lệ hoặc không thể tái tạo.
    """
    global sequence, previous_board

    # Game over? Reset everything.
    if is_game_over(current_board):
        print("Opponent wins. Game over detected. Resetting state.")
        reset_state()
        return ""

    height = len(current_board)
    width = len(current_board[0])

    # Find the column where a new piece was added
    for col in range(width):
        for row in range(height):
            if previous_board[row][col] != current_board[row][col]:
                # There is a difference — new disc dropped
                if current_board[row][col] in [1, 2] and previous_board[row][col] == 0:
                    # Register this move
                    sequence += str(col + 1)
                    previous_board = [row[:] for row in current_board]  # update snapshot
                    break

    # If no move detected (possibly a duplicate request), just update snapshot
    previous_board = [row[:] for row in current_board]
    move_sequence = sequence

    return move_sequence

def get_best_move(board: List[List[int]], current_player: int, valid_moves: List[int]) -> int:
    global sequence, previous_board
    if not valid_moves:
        print("Cảnh báo: Không có nước đi hợp lệ nào.")
        return -1
    
    # Kiểm tra xem tất cả các ô có bằng 0 không
    is_empty_board = all(cell == 0 for row in board for cell in row)

    if is_empty_board:
        print("DEBUG: Bảng rỗng, trả về nước đi mặc định (cột giữa).")
        # Trả về cột giữa (index 3) nếu hợp lệ
        center_col = 3
        if center_col in valid_moves:
            sequence += str(center_col + 1)  # Update move history

            # Update previous_board manually to reflect our move
            for row in reversed(range(len(previous_board))):
                if previous_board[row][center_col] == 0:
                    previous_board[row][center_col] = current_player
                    break
            return center_col
        elif valid_moves: # Nếu cột giữa không hợp lệ (lạ), trả về nước hợp lệ đầu tiên
             print(f"Cảnh báo: Bảng rỗng nhưng cột giữa {center_col} không hợp lệ? Trả về {valid_moves[0]}.")
             return valid_moves[0]
        else:
             # Trường hợp cực hiếm: bảng rỗng nhưng không có nước đi hợp lệ?
             print("LỖI: Bảng rỗng nhưng không có nước đi hợp lệ nào được cung cấp.")
             return -1 # Hoặc raise lỗi

    # 1. Chuyển đổi board sang move_sequence
    move_sequence = convert_board_to_movesequence(board)
    print(f"DEBUG: Board được chuyển thành move_sequence: '{move_sequence}'")

    # *** Xử lý lỗi nếu sequence rỗng nhưng board không rỗng ***
    num_pieces_on_board = sum(1 for r in board for cell in r if cell != 0)
    if not move_sequence and num_pieces_on_board > 0:
        raise ValueError(f"LỖI: Không thể tạo move_sequence hợp lệ từ board cung cấp. Board có thể không hợp lệ.")

    scores = [-10000] * len(board[0])

    command = [EXE_PATH]

    result = subprocess.run(
        command,
        input=move_sequence,
        capture_output=True,
        text=True,
        check=True,
        encoding='utf-8',
        cwd=SEVER_DIR
    )

    output_lines = result.stdout.strip().splitlines()

    last_line = output_lines[-1].strip()
    parts = last_line.split()
    expected_parts = 1+len(board[0])
    if len(parts) < expected_parts:
            # In thêm thông tin debug nếu lỗi phân tích
        print(f"DEBUG: Số phần tử nhận được: {len(parts)}, kỳ vọng: {expected_parts}")
        print(f"DEBUG: Các phần tử: {parts}")

    score_strings = parts[1:expected_parts]
    scores = [int(s) for s in score_strings]
    print(f"DEBUG: Scores: {scores}")

    # 5. Chọn nước đi tốt nhất
    best_score = -float('inf')
    best_col = -1
    for col_index in valid_moves:
        if 0 <= col_index < len(scores):
            current_score = scores[col_index]
            if current_score > best_score:
                best_score = current_score
                best_col = col_index

    if best_col == -1:
        print("CẢNH BÁO: Không thể xác định nước đi tốt nhất valid_moves.")
        if valid_moves:
            print("DEBUG: Trả về nước đi hợp lệ đầu tiên làm dự phòng.")
            return valid_moves[0]
        else:
             raise ValueError("Không có nước đi hợp lệ và không thể xác định nước đi tốt nhất.")

    print(f"DEBUG: Nước đi tốt nhất được chọn (cột 0-based): {best_col+1} với điểm {best_score}")

    sequence += str(best_col + 1)  # Update move history

    # Update previous_board manually to reflect our move
    for row in reversed(range(len(previous_board))):
        if previous_board[row][best_col] == 0:
            previous_board[row][best_col] = current_player
            break

    # Game over? Reset everything.
    if is_game_over(previous_board):
        print("I win. Game over detected. Resetting state.")
        reset_state()

    return best_col

if __name__ == "__main__":
    board_example_valid = [
        [0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0], # Row 4
        [0, 0, 0, 1, 0, 0, 0]  # Row 5 (bottom)
    ]
    # Nước đi tiếp theo là của Player 2
    # Các cột hợp lệ (chưa đầy): 0, 1, 2, 3, 4, 5, 6 (giả sử chưa cột nào đầy)
    valid_moves_example_valid = [col for col in range(7) if board_example_valid[0][col] == 0]

    start_time_cpp = time.time()
    try:
        best_move = get_best_move(board_example_valid, 1, valid_moves_example_valid)
        print(f"\n>>> Kết quả: Nước đi tốt nhất được đề xuất là cột: {best_move}")
    except Exception as e:
        print(f"\n--- LỖI TRONG QUÁ TRÌNH KIỂM TRA ---")
        print(f"Lỗi: {e}")
        # In traceback để biết lỗi chi tiết hơn
        import traceback
        traceback.print_exc()
    end_time_cpp = time.time()
    
    print(f"--- Analysis done after: {end_time_cpp - start_time_cpp:.4f} giây ---")