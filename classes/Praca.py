from classes.Karta import Karta


class Praca:
    def __init__(self, identyfikator, wyplata: int = 15) -> None:
        self.wyplata = wyplata
        self.talia_kart = []

    def dodaj_karte(self, karta: Karta) -> None:
        self.talia_kart.append(karta)
