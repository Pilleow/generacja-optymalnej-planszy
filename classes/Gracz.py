import random
import networkx as nx

from classes.Kostka import Kostka
from classes.Karta import Karta
from classes.Praca import Praca


class Gracz:
    def __init__(self, mapa: nx.DiGraph, sciezka: list = None, init_morale: int = 0, init_pieniadze: int = 0, init_dzieci: int = 0) -> None:
        self.mapa = mapa
        self.sciezka = sciezka
        self.morale = init_morale
        self.pieniadze = init_pieniadze
        self.dzieci = init_dzieci
        self.praca = None
        self.modyfikator_wyplaty = 0

        self.pozycja = 0
        self.nastepna_pozycja = 0
        self.dystans_do_nastepnej = 0
        self.liczba_ruchow = 0
        self.skonczyl = False

    def rusz_sie(self, kostka: Kostka):
        if self.dystans_do_nastepnej <= 0:
            self.pozycja = self.nastepna_pozycja
        if self.skonczyl or len(list(self.mapa.neighbors(self.pozycja))) == 0:
            self.skonczyl = True
            return
        if self.pozycja == self.nastepna_pozycja:
            self.nastepna_pozycja = self._ogarnij_gdzie_isc()
            self.dystans_do_nastepnej = self.mapa.get_edge_data(self.pozycja, self.nastepna_pozycja)["weight"]

        self.dystans_do_nastepnej = max(0, self.dystans_do_nastepnej - kostka.rzuc())
        self.liczba_ruchow += 1
        # Póki co jest to zaprogramowane tak, że gracz ZAWSZE zatrzymuje się na wierzchołkach grafu.
        # W prawdziwej grze jest tak, że gracz wybiera ścieżkę, ale można to zmienić.

    def _ogarnij_gdzie_isc(self):
        if self.sciezka is None:
            return random.choice(list(self.mapa.neighbors(self.pozycja)))
        else:
            i = self.sciezka.index(self.pozycja)
            return self.sciezka[i + 1]

    def wykonaj_karte(self, karta: Karta):
        self.morale = max(0, self.morale + karta.morale)
        self.pieniadze = max(0, self.pieniadze + karta.pieniadze)
        self.dzieci = max(0, self.dzieci + karta.dzieci)
        self.modyfikator_wyplaty += karta.wyplata

    def nowa_praca(self, nowa_praca: Praca) -> None:
        self.praca = nowa_praca
        self.modyfikator_wyplaty = 0

    def oblicz_wynik(self):
        return self.morale + self.pieniadze // 15 + self.dzieci
