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
* `tracker.py` – Implementacja algorytmu śledzenia obiektów na podstawie środków ciężkości (Centroid Tracker). Oblicza odległości między detekcjami na kolejnych klatkach i zarządza unikalnymi identyfikatorami.
* `model_handler.py` – Klasa zarządzająca wczytywaniem i obsługą modeli YOLO, odpowiedzialna za transfer modelu na odpowiednie urządzenie obliczeniowe (CPU/GPU).
* `utils.py` – Zbiór funkcji pomocniczych, wykorzystywanych do ładowania nazw klas, eksportu danych do plików Excel oraz wyświetlania komunikatów o błędach.
