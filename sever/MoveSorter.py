class MoveSorter:
    def __init__(self):
        self.width = 7
        self.entries = []

    def add(self, move, score):
        if len(self.entries) >= self.width:
            raise ValueError("error!")

        pos = len(self.entries)
        self.entries.append({'move': move, 'score': score})
        while pos > 0 and self.entries[pos - 1]['score'] > score:
            self.entries[pos] = self.entries[pos - 1]
            pos -= 1
        self.entries[pos] = {'move': move, 'score': score}

    def get_next(self):
        if self.entries:
            return self.entries.pop()['move']
        return None

    def reset(self):
        self.entries = []