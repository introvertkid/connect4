import time

from fastapi import FastAPI, HTTPException
import random
import uvicorn
from pydantic import BaseModel
from typing import List, Optional
from fastapi.middleware.cors import CORSMiddleware

from AI_logic import get_best_move_cpp

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

@app.post("/api/connect4-move")
async def make_move(game_state: GameState) -> AIResponse:
    try:
        if not game_state.valid_moves:
            raise ValueError("Không có nước đi hợp lệ")


        selected_move = get_best_move_cpp(game_state.board, game_state.current_player, game_state.valid_moves)


        return AIResponse(move=selected_move)
    except Exception as e:
         print(f"Error processing request: {e}") # Log lỗi nếu có
         if game_state.valid_moves:
             # Cân nhắc trả về lỗi thay vì nước đi đầu tiên khi có lỗi AI
             # return AIResponse(move=game_state.valid_moves[0])
             raise HTTPException(status_code=500, detail=f"Lỗi xử lý AI: {e}")
         raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)