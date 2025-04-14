import Solver
import Position

if __name__ == "__main__":
    solver = Solver.Solver()
    
    try:
        while True:
            P = Position.Position()
            s = input()
            
            if P.play_seq(s) != len(s):
                print(f"haha ngu vl choi sai roi")
            else:
                scores = solver.analyze(P)
                print(*scores, sep=" ")
    except EOFError:
        pass