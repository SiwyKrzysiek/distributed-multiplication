# Procesy rozproszone sieciowo

<!-- Repozytorium: https://github.com/SiwyKrzysiek/distributed-multiplication -->

Przetwarzanie równoległe rozproszone bez specjalnych mechanizmów synchronizacji i komunikacji między węzłami. Problem przetwarzania równoległego do rozwiązania - dystrybucja dużego zbioru danych wejściowych.

> Uwaga: wątki w Pythonie nie wykorzystują własności wieloprocesorowych o ile nie zostaną specjalnie zaimplementowane, napisane w sposób rozproszony, ze względu na [Global Interpreter Lock](https://wiki.python.org/moin/GlobalInterpreterLock).

W zadaniu wykorzystam moduł języka Python - [multiprocessing](https://docs.python.org/2/library/multiprocessing.html) (dostępny w bibliotece standardowej języka Python). Multiprocessing pozwala w języku Python na lokalne oraz zdalne przetwarzanie równoległe. Lokalnie pozwala w sposób efektywny uniknąć GIL, poprzez wykorzystanie podprocesów zamiast wątków.

## Spis treści

- [Procesy rozproszone sieciowo](#procesy-rozproszone-sieciowo)
  - [Spis treści](#spis-treści)
  - [Opis zadania](#opis-zadania)
    - [Do zbadania eksperymentalnie](#do-zbadania-eksperymentalnie)
    - [Do przeanalizowania](#do-przeanalizowania)
  - [Realizacja zadania](#realizacja-zadania)
    - [Model systemu](#model-systemu)
    - [Przykład działania](#przykład-działania)
    - [Pomiary](#pomiary)
      - [Czas wykonania mnożeń](#czas-wykonania-mnożeń)
      - [Porównanie obliczenia na wielu maszynach z obliczeniami na jednej](#porównanie-obliczenia-na-wielu-maszynach-z-obliczeniami-na-jednej)
      - [Zbadanie prawa Amdhala](#zbadanie-prawa-amdhala)
    - [Wnioski](#wnioski)

## Opis zadania

Proszę napisać program realizujący rozproszone zadanie obliczenia iloczynu macierzy i wektora. Program powinien składać się z:

- **serwera** - tworzącego obiekt typu Manager udostępniający dwie kolejki - jedną, do której przekazywane są dane do obliczeń oraz drugą - do której przekazywane są cząstkowe rozwiązania,
- **klienta** - wczytującego dane macierzy i wektora i dzielącego dane na liczbę zadań przekazaną jako argument programu. Klient dodaje zadania do pierwszej kolejki, odbiera wyniki wrzucone do kolejki z wynikami cząstkowymi i łączy wynik w wektor w odpowiedniej kolejności,
- **programu wykonującego obliczenia** (worker) - program pobiera zadania z kolejki, tworzy określoną liczbę podprocesów (może odpowiadać np. liczbie procesorów dostępnych w danej maszynie), wykonuje obliczenia dla kolejnych odebranych zadań, wyniki dodaje do kolejki z wynikami cząstkowymi. Program proszę uruchomić również na innej maszynie/ maszynach niż na tej na której znajduje się program serwera.

### Do zbadania eksperymentalnie

1. Czas wykonywania mnożenia macierzy przez wektor przy różnych (zaproponowanych przez każdy zespół) strategiach dystrybucji danych do węzłów obliczeniowych.
2. Porównanie czasu wykonywania tego samego zadania na jednej maszynie z wieloma rdzeniami/procesorami z wykonaniem na kilku maszynach.
3. Zbadanie prawa Amdhala dla samodzielnie wygenerowanych danych testowych.   
<img src="https://render.githubusercontent.com/render/math?math=\dfrac{1}{(1-P)%2B\dfrac{P}{N}}">  
(gdzie P - proporcja programu, która może ulec zrównolegleniu, N - liczba procesorów).

Należy samodzielnie przeanalizować, która część napisanego programu może być zrównoleglona.

### Do przeanalizowania

1. Jak efektywnie przekazywać dane pomiędzy węzłami obliczeniowymi?
2. Jakiego typu zadania warto obliczać za pomocą narzędzi “process-based execution”?
3. Warto porównać z watkami.
4. Porównać uruchamianie na kilku maszynach oraz na jednej maszynie z kilkoma rdzeniami? Czy warto stosować algorytm rozproszony sieciowo? Kiedy?
5. Jak ważna w tym modelu jest prędkość komunikacji miedzy węzłami?

## Realizacja zadania

Opis wykonania zadania oraz decyzji podjętych przy projektowaniu programu.

### Model systemu

Diagram obrazujący budowę oraz opis kroków działania systemu.

<img src="./Modele/Model_dzialania_i_architektury.svg">

### Przykład działania

Pierwszym krokiem jest uruchomienie serwera. Jako argumenty można podać numer portu i klucz używany połączeniu lub zostawić wartości domyślne.

Argumenty server.py

```bash
➜ python3 server.py -h 
usage: server.py [-h] [-p PORT] [-k KEY]

optional arguments:
  -h, --help            show this help message and exit
  -p PORT, --port PORT  Set server port
  -k KEY, --key KEY     Set server key
```

Przykładowe uruchomienie

```bash
python3 server.py
```

Serwer udostępnia wspólne zasoby takie jak kolejki, które są wykorzystywane przez klienta i workerów.

Następnie można uruchomić dowolną liczbę workerów w trybie ciągłej pracy (flaga `-c`) lub klienta.

Klient wymaga podania pliku z macierzą i wektorem oraz ewentualnie adresu serwera.

```bash
➜ python3 klient.py -h                         
usage: klient.py [-h] [-a ADDRESS] [-p SERVERPORT] [-k KEY] [-t TASKS]
                 [-o OUTPUT]
                 matrix vector

positional arguments:
  matrix                Path to file with input matrix
  vector                Path to file with input vector

optional arguments:
  -h, --help            show this help message and exit
  -a ADDRESS, --address ADDRESS
                        Select server address. Defaults to localhost
  -p SERVERPORT, --serverPort SERVERPORT
                        Set server port
  -k KEY, --key KEY     Set server key
  -t TASKS, --tasks TASKS
                        Number of tasks that will be created
  -o OUTPUT, --output OUTPUT
                        Path to file in which to store results. If not
                        provided vector is just displayed.
```

Przykładowe uruchomienie

```bash
python3 klient.py A.dat X.dat -t 20 -a 127.0.0.1 -o C.dat
```

Ostatnim procesem jest uruchomienie dowolnej liczby wrokerów.

Worker przyjmuje adres serwera.

```txt
➜ python3 worker.py -h
usage: worker.py [-h] [-a ADDRESS] [-p SERVERPORT] [-k KEY] [-e]
                 [-s SUBPROCESSES]

optional arguments:
  -h, --help            show this help message and exit
  -a ADDRESS, --address ADDRESS
                        Select server address. Defaults to localhost
  -p SERVERPORT, --serverPort SERVERPORT
                        Set server port
  -k KEY, --key KEY     Set server key
  -e, --endless         Don't stop when there are no tasks
  -s SUBPROCESSES, --subprocesses SUBPROCESSES
                        Set number of subprocess used. Defaults to core count

```

Przykładowe uruchomienie

```bash
python3 worker.py -a 127.0.0.1
```

Workera można też uruchomić w trybie ciągłego oczekiwania na zadania.

```bash
python3 worker.py -a 127.0.0.1 -e
```

Po przetworzeniu wszystkich zadań _Klient_ połączy wyniki cząstkowe w wektor wynikowy. Wynik zostanie wyświetlony lub zapisany do pliku (w zależności od flagi `-o`).

Każdy z programów może być wykonywany na **innej maszynie**.

### Pomiary

#### Czas wykonania mnożeń

Pomiary czasów wykonania kolejnych etapów w zależności od liczby zadań, na jaką zostanie podzielone główne zadanie obliczeniowe.

| Lizba zadań | Czas tworzenia zadań [s] | Czas obliczeń [s]   | Czas połączenia wyników [s] |
| ----------- | ------------------------ | ------------------- | --------------------------- |
| 2           | 0.1837749481201172       | 0.38793110847473145 | 0.0015811920166015625       |
| 4           | 0.2599449157714844       | 0.18340682983398438 | 0.0017991065979003906       |
| 8           | 0.2220301628112793       | 0.2466878890991211  | 0.019262075424194336        |
| 20          | 0.21198391914367676      | 0.18560481071472168 | 0.005330801010131836        |
| 50          | 0.21490788459777832      | 0.20556020736694336 | 0.00910496711730957         |
| 100         | 0.19277095794677734      | 0.2568790912628174  | 0.015871047973632812        |
| 500         | 0.22638416290283203      | 0.3589460849761963  | 0.07500481605529785         |
| 1000        | 0.3039872646331787       | 0.4904651641845703  | 0.1397550106048584          |

#### Porównanie obliczenia na wielu maszynach z obliczeniami na jednej

Niestety nie mam dostępu do wielu maszyn. Przy próbie zalogowania się na serwer `pri2` hasło jest odrzucane, mimo że to samo hasło jest poprawne na maszynie `pri`.

#### Zbadanie prawa Amdhala

To zbadania tego prawa uruchomię program `worker.py` z różną liczbą podprocesów i sprawdzę czy wyniki odpowiadają tym przewidzianym przez prawo Amdhala.

Pomiary wykonania zadania w zależności od liczby podprocesów uruchomionych przez Worker.py (flaga `-s`).

| Ilość procesów | Czas wykonania programu | Czas wykonania obliczeń |
| -------------- | ----------------------- | ----------------------- |
| 1              | 1.3075010776519775      | 0.4550001621246338      |
| 2              | 1.1031179428100586      | 0.22890996932983398     |
| 3              | 1.0929396152496338      | 0.21912002563476562     |
| 4              | 1.0899121761322021      | 0.2120060920715332      |

Wykonanie dla jednego procesu pozwala obliczyć proporcję programu, która może ulec zrównolegleniu.  
P = 0.4550001621246338 / 1.3075010776519775 ≃ 0.34799218899438866

| Ilość procesów | Wartość prawa Amdhala | Faktyczne przyśpieszenie |
| -------------- | --------------------- | ------------------------ |
| 1              | 1.0                   | 1.0                      |
| 2              | 1.2106480288265458    | 1.1852776814791697       |
| 3              | 1.3020745047645286    | 1.1963159349415078       |
| 4              | 1.3531692459953584    | 1.1996389308099469       |

Faktyczny zysk jest mniejszy niż ten przewidziany przez prawo Amdhala. Może to wynikać z narzutów powstałych w wyniku komunikacji sieciowej.

### Wnioski

1. Przy przekazywaniu danych między węzłami należy zadbać o unikanie duplikacji danych, ponieważ spowolni to ich przesył.
2. Zadania, które można rozłożyć na niezależne podproblemy dobrze nadają się do obliczeń z zastosowaniem _process-based execution_.
3. Korzystanie z wielu procesów jest mniej wydajne niż z wątków, jednak dzięki zastosowaniu wielu procesów możliwe jest wykonywanie obliczeń rozproszonych sieciowo. Pozwala to na znaczne zwiększenie mocy obliczeniowej wykorzystywanej do rozwiązania problemu.
4. Warto zastosować algorytmy rozproszone sieciowo gdy jest potrzeba na wykorzystanie większej liczby procesorów niż jest w stanie zaoferować pojedynczy komputer. Przy obliczeniach rozproszonych sieciowo występują dodatkowe narzuty związane ze stosunkowo wolną komunikacją między węzłami, jednak pozwalają one na praktycznie dowolne skalowanie mocy obliczeniowej.
5. Waga prędkości komunikacji między węzłami jest zależna od tego jak często algorytm wymaga wymiany danych pomiędzy węzłami. Jest to jednak aspekt, na który warto zwrócić szczególną uwagę.
