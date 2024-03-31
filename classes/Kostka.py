import random


class Kostka:
    def __init__(self, min_oczek: int = 1, max_oczek: int = 4) -> None:
        self.zakres = range(min_oczek, max_oczek)

    def rzuc(self) -> int:
        return random.choice(self.zakres)
