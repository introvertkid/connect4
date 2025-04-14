import math

def med(min:int, max:int) -> int:
        return (min + max) // 2

def has_factor(n, min, max) -> bool:
    if min * min > n:
        return False
    elif min + 1 >= max:
        return n % min == 0
    else:
        return has_factor(n, min, med(min, max)) or has_factor(n, med(min, max), max)
    
def next_prime(n) -> int:
    return next_prime(n+1) if has_factor(n, 2, n) else n

def log2(n) -> int:
    return 0 if n <= 1 else log2(n//2) + 1

class TranspositionTable:
    log_size = 24
    size = next_prime(2 ** log_size)

    def __init__(self):
        self.K = [0] * self.size
        self.V = [0] * self.size

    def reset(self):
        self.K = [0] * self.size
        self.V = [0] * self.size
    def index(self, key):
        return key % self.size
    
    def put(self, key, value):
        pos = self.index(key)
        self.K[pos] = key
        self.V[pos] = value

    def get(self, key):
        pos = self.index(key)
        if self.K[pos] == key:
            return self.V[pos]
        else:
            return 0
        
    def getKeys(self):
        return self.K   
    
    def getValues(self):
        return self.V
    
    def getSize(self):
        return self.size
    
    def getKetSize(self) -> int:
        return len(self.K)
    
    def getValueSize(self) -> int:
        return len(self.V)