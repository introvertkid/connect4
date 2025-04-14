import Solver
import Position
import Book

if __name__ == "__main__":
    solver = Solver.Solver()
    
    try:
        while True:
            filename = "NegamaxSolver/7x6.book"
            P = Position.Position()
            s = input()
            solver.load_book(filename)

            if len(s) == 0:
                break
            elif P.play_seq(s) != len(s):
                print(f"haha ngu vl choi sai roi")
            else:
                scores = solver.analyze(P)
                print(*scores, sep=" ")
    except EOFError:
        pass