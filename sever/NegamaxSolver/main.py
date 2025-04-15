import Solver
import Position
import time

if __name__ == "__main__":
    print("Loading book...")
    start = time.time()

    filename = "7x6.book"
    solver = Solver.Solver()
    solver.load_book(filename)

    print(f"Loaded book after {time.time() - start}")
    
    try:
        while True:
            P = Position.Position()
            s = input("choi mm di: ")

            if P.play_seq(s) != len(s):
                print(f"haha ngu vl choi sai roi")
            else:
                start = time.time()
                scores = solver.analyze(P)
                print(*scores, sep=" ")
                print(f"Analysis done after {time.time() - start}")
            
    except EOFError:
        pass