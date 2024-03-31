import csv
import time
import json
import pprint
import random
import pygame
import datetime
import threading
import networkx as nx
from tqdm import tqdm

from classes.Pola import Pola
from classes.Karta import Karta
from classes.Symulacja import Symulacja

# ---------------------------------------- TUTAJ ZMIENNE GLOBALNE ---------------------------------------------------- #

LICZBA_SYMULACJI_NA_ITERACJE = 30
LICZBA_ITERACJI = 200
SZANSA_MUTACJI = .5
# jeżeli poniższe = 60, ścieżki graczy będą pobrane z sciezki.json i wszystkie drogi zostaną sprawdzone
LICZBA_GRACZY = 60


# ---------------------------------------- TUTAJ WYKONANIE PROGRAMU -------------------------------------------------- #

def main():
    # część 0 - ładujemy mapę i karty -------------------------------------------------------------------------------- #
    mapa = nx.DiGraph()
    with open("mapa_jako_graf.csv", 'r', encoding="utf-8") as f:
        csv_f = csv.reader(f, delimiter=" ")
        for row in csv_f:
            mapa.add_edge(int(row[0]), int(row[2]), weight=int(row[1]))

    with open("sciezki.json", "r", encoding="utf-8") as f:
        sciezki = json.load(f)

    karty = {
        Pola.ZIELONA: [],
        Pola.NEUTRALNA: [],
        Pola.CZERWONA: []
    }
    for l in [["zielone", Pola.ZIELONA], ["niebieskie", Pola.NEUTRALNA], ["czerwone", Pola.CZERWONA]]:
        with open(f"karty/{l[0]}.csv", 'r', encoding="utf-8") as f:
            csv_f = csv.reader(f, delimiter=" ")
            for row in csv_f:
                if not row[0].isnumeric():
                    continue
                karty[l[1]].append(Karta(int(row[0]), int(row[1]), int(row[2]), int(row[3])))

    # część 1 - wykonujemy symulację --------------------------------------------------------------------------------- #
    najlepsze_symulacje = []
    symulacje_aktualnej_iteracji = []

    def jedna_symulacja(i, szansa_mutacji):
        symulacja = Symulacja(mapa, numer_symulacji, karty, najlepsze_symulacje[-1] if i > 0 else None, szansa_mutacji)
        symulacja.przeprowadz_symulacje_jednej_gry(LICZBA_GRACZY, sciezki)
        symulacja.przeprowadz_ocene()
        symulacje_aktualnej_iteracji.append(symulacja)

    def pygame_loop_preview():
        pozycje_pol = {
            "0 1": [[269, 131], [308, 124]],
            "1 2": [[347, 114], [371, 105], [394, 90], [419, 81], [452, 76]],
            "1 3": [[322, 150], [348, 150], [374, 146], [401, 146], [422, 154]],
            "3 2": [[446, 119], [452, 94], [452, 76]],
            "3 4": [[424, 202]],
            "2 5": [[480, 69], [506, 65], [532, 60], [558, 61], [584, 67]],
            "4 5": [[454, 188], [476, 174], [498, 159], [520, 144], [540, 127], [558, 108], [574, 87], [584, 67]],
            "4 6": [[452, 222], [477, 210], [498, 196], [520, 180], [542, 164], [564, 150], [587, 137], [622, 128]],
            "5 6": [[614, 88], [622, 128]],
            "5 7": [[590, 53], [616, 49], [642, 58], [665, 70], [689, 92]],
            "6 7": [[652, 113], [674, 100], [689, 92]],
            "6 8": [[620, 161], [636, 176], [663, 179]],
            "7 9": [[714, 104], [736, 117], [760, 132]],
            "8 7": [[664, 159], [678, 137], [689, 113], [689, 92]],
            "8 9": [[693, 178], [719, 175], [744, 164], [760, 132]],
            "9 10": [[795, 143], [822, 145], [848, 141], [885, 135]],
            "9 11": [[761, 101], [774, 78], [798, 61]],
            "10 11": [[883, 100], [869, 78], [845, 65], [819, 64], [798, 61]],
            "11 12": [[307, 49]],
            "12 13": [[283, 50], [257, 53], [231, 59], [207, 71], [184, 85], [148, 95]],
            "13 15": [[132, 63], [116, 41], [111, 17], [85, 23], [68, 44], [63, 70], [61, 104]],
            "13 14": [[145, 123], [149, 148], [142, 172], [116, 177], [90, 182], [63, 186], [37, 190], [11, 194]],
            "14 15": [[10, 166], [16, 141], [34, 120], [61, 104]]
        }
        kolory_pol = {
            Pola.ZIELONA: "#8ee671",
            Pola.CZERWONA: "#fa5959",
            Pola.NEUTRALNA: "#5a96fd",
            Pola.DZIECKO: "#9471e5",
            Pola.WYPLATA: "#fed663"
        }

        size = 24
        for k in pozycje_pol:
            for i in range(len(pozycje_pol[k])):
                pozycje_pol[k][i][0] *= 2
                pozycje_pol[k][i][1] *= 2
                pozycje_pol[k][i][0] -= size // 2
                pozycje_pol[k][i][1] -= size // 2
                pozycje_pol[k][i].extend([size, size])

        pygame.init()
        display = pygame.display.set_mode((899 * 2, 233 * 2))
        sprite = pygame.image.load("mapa.png").convert()
        sprite = pygame.transform.smoothscale(sprite, (899 * 2, 233 * 2))
        runloop = True

        while runloop:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    runloop = False
            display.blit(sprite, (0, 0))
            if len(najlepsze_symulacje) == 0:
                continue
            ns = najlepsze_symulacje[-1]
            for sciezka in pozycje_pol:
                pola = ns.pola_mapy[sciezka]
                for i in range(len(pola) - 1, -1, -1):
                    pygame.draw.rect(
                        display, kolory_pol[ns.pola_mapy[sciezka][i]],
                        pozycje_pol[sciezka][i]
                    )

            pygame.display.update()

            if len(najlepsze_symulacje) == LICZBA_ITERACJI - 1:
                ocena = najlepsze_symulacje[-1].przeprowadz_ocene()
                name = f"generated_maps/map_{ocena['ocena']}_at_{datetime.datetime.now().strftime('%Y_%m_%d_%H_%M_%S')}"
                with open(f"{name}.png", "w+") as _:
                    pass
                pygame.image.save(display, f"{name}.png")
                with open(f"{name}.json", "w+", encoding="utf-8") as f:
                    json.dump(ocena, f, indent=2)
        pygame.quit()

    pygame_thread = threading.Thread(target=pygame_loop_preview).start()

    while True:
        najlepsze_symulacje = []
        symulacje_aktualnej_iteracji = []
        for iteracja in tqdm(range(LICZBA_ITERACJI)):
            symulacje_aktualnej_iteracji.clear()
            threads = []
            for numer_symulacji in range(LICZBA_SYMULACJI_NA_ITERACJE):
                if numer_symulacji == 1:
                    threads.append(threading.Thread(target=lambda: jedna_symulacja(iteracja, 0)))
                else:
                    threads.append(threading.Thread(target=lambda: jedna_symulacja(iteracja, SZANSA_MUTACJI)))
                threads[-1].start()
            while len(threads) > 0:
                for thread in threads:
                    thread.join()
                    if not thread.is_alive():
                        threads.remove(thread)

            polepszone = False
            if iteracja != 0:
                najlepsza_symulacja = najlepsze_symulacje[-1]
                najlepsza_symulacja_ocena = najlepsze_symulacje[-1].przeprowadz_ocene()
            else:
                najlepsza_symulacja = symulacje_aktualnej_iteracji[0]
                najlepsza_symulacja_ocena = symulacje_aktualnej_iteracji[0].przeprowadz_ocene()
            for sym in symulacje_aktualnej_iteracji:
                ocena = sym.przeprowadz_ocene()
                if ocena["ocena"] < najlepsza_symulacja_ocena["ocena"]:  # tutaj znak nierówności definiuje
                    polepszone = True                                    # czy bierzemy najlepszy czy najgorszy
                    najlepsza_symulacja_ocena = ocena
                    najlepsza_symulacja = sym
            najlepsze_symulacje.append(najlepsza_symulacja)
            if polepszone:
                print(f"\n\n# ------------ ITERACJA {iteracja} ------------- #")
                pprint.pprint(najlepsza_symulacja_ocena, indent=2)
        time.sleep(2)


if __name__ == "__main__":
    main()
