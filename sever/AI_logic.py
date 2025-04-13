import torch
import numpy as np
from model import DQN  # model MLP bạn đã define
from connect4_env import Connect4Env  # nếu có

# Load model
model = DQN(input_dim=42, output_dim=7)
model.load_state_dict(torch.load("dqn_player1.pth", map_location=torch.device('cpu')))
model.eval()


# def get_best_move(board: list[list[int]], valid_moves: list[int]) -> int:
#     state = np.array(board).flatten().astype(np.float32)
#     state_tensor = torch.tensor(state, dtype=torch.float32).unsqueeze(0)
#     with torch.no_grad():
#         q_values = model(state_tensor)
#         q_values = q_values.numpy().flatten()
#         for i in range(len(q_values)):
#             if i not in valid_moves:
#                 q_values[i] = -np.inf
#         return int(np.argmax(q_values))


def get_best_move(model, board: list[list[int]], valid_moves: list[int]) -> int:
    if not valid_moves:
        return None
    state = np.array(board).flatten().astype(np.float32)
    state_tensor = torch.tensor(state, dtype=torch.float32).unsqueeze(0)

    with torch.no_grad():
        q_values = model(state_tensor)[0]
        valid_q_values = q_values[valid_moves]
        best_index = torch.argmax(valid_q_values).item()
        return valid_moves[best_index]
