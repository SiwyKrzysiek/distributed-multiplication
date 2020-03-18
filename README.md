# Procesy rozproszone sieciowo

Przetwarzanie równoległe rozproszone bez specjalnych mechanizmów synchronizacji i komunikacji między węzłami. Problem przetwarzania równoległego do rozwiązania - dystrybucja dużego zbioru danych wejściowych.

> Uwaga: wątki w Pythonie nie wykorzystują własności wieloprocesorowych o ile nie zostaną specjalnie zaimplementowane, napisane w sposób rozproszony, ze względu na [Global Interpreter Lock](https://wiki.python.org/moin/GlobalInterpreterLock).

W zadaniu wykorzystam moduł języka Python - [multiprocessing](https://docs.python.org/2/library/multiprocessing.html) (dostępny w bibliotece standardowej języka Python). Multiprocessing pozwala w języku Python na lokalne oraz zdalne przetwarzanie równoległe. Lokalnie pozwala w sposób efektywny uniknąć GIL, poprzez wykorzystanie podprocesów zamiast wątków.

## Spis treści

- [Procesy rozproszone sieciowo](#procesy-rozproszone-sieciowo)
  - [Spis treści](#spis-treści)
  - [Opis zadania](#opis-zadania)
    - [Do zbadania eksperymentalnie](#do-zbadania-eksperymentalnie)
    - [Do przeanalizowania](#do-przeanalizowania)

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