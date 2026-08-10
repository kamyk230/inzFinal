# Program do analizy natężenia ruchu drogowego (Python + YOLOv8 + OpenCV)

Aplikacja napisana w języku Python służąca do analizy natężenia ruchu drogowego. Przyjmuje na wejściu zrealizowane wcześniej nagranie bądź strumień na żywo z kamery a następnie zlicza przejeżdżające pojazdy. Po przeanalizowaniu nagrania program ma możliwość zapisać zgromadzone dane w arkuszu kalkulacyjnym.

## Wymagania i instalacja

Aby uruchomić projekt, wymagany jest Python w wersji przynajmniej 3.10. Reszta zależności znajduje się w pliku requirements.txt.
Instalacja biblioteki systemowej dla interfejsu graficznego oraz wymaganych pakietów:
```bash
sudo apt-get install python3-tk
pip install opencv-python
pip install ultralytics
pip install pandas
pip install openpyxl
pip install torch==1.13.0+cu121 torchvision==0.14.0+cu121 torchaudio==0.13.0+cu121 -f [https://download.pytorch.org/whl/cu121/torch_stable.html](https://download.pytorch.org/whl/cu121/torch_stable.html)
```
## Struktura projektu

Projekt składa się z następujących modułów:

* `main.py` – Główny skrypt uruchamiający aplikację i inicjalizujący interfejs użytkownika.
* `gui.py` – Definicja i obsługa okna aplikacji w oparciu o bibliotekę Tkinter. Odpowiada za parametry konfiguracyjne (wybór urządzenia, modelu, rozdzielczości, itp.) oraz delegację zadań.
* `analysis.py` – Główny silnik przetwarzania wideo. Odpowiada za odczyt klatek z OpenCV, uruchamianie inferencji, logikę zliczania obiektów przekraczających wirtualną linię oraz agregację danych do eksportu.
* `tracker.py` – Implementacja algorytmu śledzenia obiektów na podstawie środków ciężkości. Oblicza odległości między detekcjami na kolejnych klatkach i zarządza unikalnymi identyfikatorami.
* `model_handler.py` – Klasa zarządzająca wczytywaniem i obsługą modeli YOLO, odpowiedzialna za transfer modelu na odpowiednie urządzenie obliczeniowe (CPU/GPU).
* `utils.py` – Zbiór funkcji pomocniczych, wykorzystywanych do ładowania nazw klas, eksportu danych do plików Excel oraz wyświetlania komunikatów o błędach.
## Instrukcja obsługi

1. Uruchomienie aplikacji:
Aby włączyć program, należy uruchomić główny skrypt z poziomu terminala, będąc w głównym katalogu projektu:
```bash
python main.py
```
Konfiguracja w panelu GUI:

Urządzenie: Wybierz obliczenia na CPU lub GPU (wymaga kompatybilnej karty graficznej NVIDIA i zainstalowanego środowiska CUDA).

Parametry badawcze: Wybierz wariant modelu YOLOv8, docelową rozdzielczość analizy oraz próg pewności (Confidence). Opcjonalnie włącz tryb FP16 dla przyspieszenia obliczeń.

Linia zliczająca: Wpisz pozycję linii w pikselach, wybierz jej orientację (pozioma/pionowa) i zweryfikuj prawidłowość ustawienia używając przycisku podglądu.

Źródło wideo: Wczytaj z dysku plik wideo lub zaznacz opcję użycia kamery.

Tryb pracy: Wybierz "Display" dla samego podglądu na żywo lub "Record" w celu przeprowadzenia analizy z automatycznym zapisem wyników do pliku arkusza kalkulacyjnego .xlsx.

Kontrola analizy:
Po skonfigurowaniu parametrów naciśnij "URUCHOM ANALIZĘ". W trakcie działania programu aktywne okno podglądu reaguje na skróty klawiszowe:

Spacja – pauzuje i wznawia analizę,

Q – przerywa analizę i zamyka okno podglądu.
