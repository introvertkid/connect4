import asyncio
from fastapi import FastAPI, HTTPException
import uvicorn
from pydantic import BaseModel
from typing import List, Optional
from fastapi.middleware.cors import CORSMiddleware
from AI_logic import get_best_move

app = FastAPI()

# http://127.0.0.1:8080/docs
# ngrok http 8080

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class GameState(BaseModel):
    board: List[List[int]]
    current_player: int
    valid_moves: List[int]

class AIResponse(BaseModel):
    move: int

@app.get("/api/test")
async def health_check():
    return {"status": "ok", "message": "Server is running"}

@app.post("/api/connect4-move")
async def make_move(game_state: GameState) -> AIResponse:
    try:
        print(f"Nhận yêu cầu: Player {game_state.current_player}, Valid Moves: {game_state.valid_moves}")
        if not game_state.valid_moves:
            # Không có nước đi hợp lệ nào được cung cấp từ client
            print("Lỗi: Không có nước đi hợp lệ nào được cung cấp trong yêu cầu.")
            raise HTTPException(status_code=400, detail="Không có nước đi hợp lệ nào được cung cấp.")

        # Gọi hàm logic AI (đảm bảo hàm này xử lý lỗi nội bộ nếu có)
        selected_move = get_best_move(game_state.board, game_state.current_player, game_state.valid_moves)

        # Kiểm tra xem AI có trả về nước đi hợp lệ không
        # (Điều chỉnh logic này dựa trên cách get_best_move_cpp báo lỗi)
        if selected_move == -1 or selected_move not in game_state.valid_moves:
            print(f"Lỗi: AI trả về nước đi không hợp lệ ({selected_move}) hoặc không tìm thấy nước đi.")
            # Quyết định xử lý: có thể chọn nước đi ngẫu nhiên hoặc báo lỗi
            # Ví dụ: báo lỗi
            raise HTTPException(status_code=500, detail=f"Lỗi xử lý AI: Không thể xác định nước đi hợp lệ. AI trả về {selected_move}")
            # Hoặc chọn ngẫu nhiên (không khuyến khích nếu AI lỗi):
            # print("Cảnh báo: AI lỗi, chọn nước đi ngẫu nhiên.")
            # selected_move = random.choice(game_state.valid_moves)

        print(f"AI đã chọn nước đi: {selected_move}")
        await asyncio.sleep(1.0)

        print("Đã hết thời gian chờ. Gửi phản hồi.")
        return AIResponse(move=selected_move)

    # Xử lý lỗi cụ thể hơn nếu cần
    except HTTPException as he:
        # Log lỗi HTTPException nếu muốn, rồi raise lại
        print(f"HTTP Exception: {he.status_code} - {he.detail}")
        raise he
    except Exception as e:
        # Log các lỗi không mong muốn khác
        print(f"Lỗi không mong muốn xảy ra: {e}")
        # Trả về lỗi server chung
        raise HTTPException(status_code=500, detail=f"Lỗi máy chủ nội bộ khi xử lý yêu cầu: {e}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)