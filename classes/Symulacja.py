import random
import networkx as nx

from classes.Gracz import Gracz
from classes.Pola import Pola
from classes.Praca import Praca
from classes.Kostka import Kostka


class Symulacja:
    def __init__(self, mapa: nx.DiGraph, numer_symulacji: int, karty: dict, rodzic: object = None, szansa_mutacji: int = 0.05) -> None:
        self.mapa = mapa
        self.karty = karty
        self.numer_symulacji = numer_symulacji
        self.rodzic = rodzic
        self.gracze = []
        if self.rodzic is not None:
            self.genom = self._wygeneruj_genom(rodzic.genom, szansa_mutacji)
        else:
            self.genom = self._wygeneruj_genom()
        self.pola_mapy = self.wygeneruj_pola_z_genomu()

    def _nowy_genom(self) -> object:
        # generuje listę [17, 63, 48, 91, 26, 73, ..., 37, 52], która dla każdej ścieżki przyporządkowuje
        # integer od 1 do 100. Ten integer określa jakie jest prawdopodobieństwo wystąpienia określonego
        # rodzaju pola na ścieżce.
        out = {}
        for u, v in self.mapa.edges():
            out[f"{u} {v}"] = random.uniform(1, 100)
        return out

    def _mutuj_genom(self, genom: object, szansa_mutacji: float) -> object:
        delta = random.randint(1, 5)
        for chromosom in genom:
            if random.uniform(0, 1) <= szansa_mutacji:
                genom[chromosom] = min(100, max(1, genom[chromosom] + random.randint(-delta, delta)))
        return genom

    def _wygeneruj_genom(self, genom_rodzica: object = None, szansa_mutacji: float = 0.05) -> object:
        if genom_rodzica is None:
            return self._nowy_genom()
        else:
            return self._mutuj_genom(genom_rodzica, szansa_mutacji)

    def wygeneruj_pola_z_genomu(self) -> dict:
        # klucze to wierzchołki "[u] [v]" gdzie u to Gracz.pozycja, v to Gracz.nastepna_pozycja.
        # wartości to lista pól dla danej ścieżki, gdzie indeksy to Gracz.dystans_do_nastepnej - 1.
        # Wykorzystuje zmodyfikowaną wersję rozkładu normalnego do wybrania pól występujących
        # na ścieżce.

        a = 14
        m = 22
        n = 15.5
        k = 1.570397548089
        e = 2.718281828459
        pi = 3.141592653589
        r_norm = lambda x, b: (k/((2*pi)**0.5)) * (e**(-0.5*((x-b)/a)**2))
        # wizualizacja w pliku rozklad_normalny.png

        out = {}
        for u, v, dystans in self.mapa.edges(data="weight"):
            wybrane_rodzaje_pol = []
            while len(wybrane_rodzaje_pol) <= dystans // 2:
                for pole in [Pola.DZIECKO, Pola.WYPLATA, Pola.CZERWONA, Pola.NEUTRALNA, Pola.ZIELONA]:
                    prawdopodobienstwo = random.uniform(0, 1)
                    if prawdopodobienstwo > 0.3:  # todo tutaj się zmienia prawdopodobieństwo pola
                        wybrane_rodzaje_pol.append(pole)

            while dystans < len(wybrane_rodzaje_pol):  # tu może walnąć IndexError
                wybrane_rodzaje_pol.pop()

            step = dystans // len(wybrane_rodzaje_pol)
            out[f"{u} {v}"] = [Pola.NEUTRALNA for _ in range(dystans)]
            for d in range(1, dystans - 1, step):
                out[f"{u} {v}"][d] = (wybrane_rodzaje_pol.pop())
                if len(wybrane_rodzaje_pol) == 0:
                    break
        return out

    def przeprowadz_symulacje_jednej_gry(self, liczba_graczy: int, mozliwe_sciezki: list):
        for numer_gracza in range(liczba_graczy):
            self.gracze.append(Gracz(self.mapa, mozliwe_sciezki[numer_gracza] if liczba_graczy == 60 else None))
        skonczyli = set()
        while len(skonczyli) < liczba_graczy:
            for gracz in self.gracze:
                if gracz.skonczyl:
                    skonczyli.add(gracz)
                    continue
                gracz.rusz_sie(Kostka())
                if gracz.skonczyl:
                    continue

                pole = self.pola_mapy[f"{gracz.pozycja} {gracz.nastepna_pozycja}"][gracz.dystans_do_nastepnej - 1]
                if pole in [Pola.ZIELONA, Pola.NEUTRALNA, Pola.CZERWONA]:
                    gracz.wykonaj_karte(random.choice(self.karty[pole]))
                elif pole == Pola.DZIECKO:
                    gracz.dzieci += 1
                elif pole == Pola.WYPLATA:
                    if gracz.praca is None:
                        gracz.praca = Praca("TEMP", random.randint(10, 20))
                    else:
                        gracz.pieniadze += gracz.praca.wyplata + gracz.modyfikator_wyplaty

    def przeprowadz_ocene(self) -> dict:
        def zbuduj_info_gracza(g):
            return {
                "wynik": g.oblicz_wynik(),
                "morale": g.morale,
                "pieniadze": g.pieniadze // 15,
                "dzieci": g.dzieci,
                "liczba_ruchow": g.liczba_ruchow
            }

        ocena = {
            "ocena": 0,
            "genom": self.genom,
            "najlepszy_gracz": None,
            "najgorszy_gracz": None,
        }
        min_wynik_gracz = self.gracze[0]
        max_wynik_gracz = self.gracze[0]
        for gracz in self.gracze:
            w = gracz.oblicz_wynik()
            if w < min_wynik_gracz.oblicz_wynik():
                min_wynik_gracz = gracz
            elif w > max_wynik_gracz.oblicz_wynik():
                max_wynik_gracz = gracz
        ocena["najlepszy_gracz"] = zbuduj_info_gracza(max_wynik_gracz)
        ocena["najgorszy_gracz"] = zbuduj_info_gracza(min_wynik_gracz)

        # Ocena bierze pod uwagę różnicę wyników graczy oraz różnicę między ilością poszczególnych współczynnników.
        # Można wyrzucić branie pod uwagę różnicy wyników jeżeli jeden z współczynników będzie przeważał.
        for k in ["wynik", "morale", "pieniadze", "dzieci"]:
            ocena["ocena"] += abs(ocena["najlepszy_gracz"][k] - ocena["najgorszy_gracz"][k])
        return ocena
