# Program do analizy natężenia ruchu drogowego (Python + YOLOv8 + OpenCV)

Aplikacja napisana w języku Python służąca do analizy natężenia ruchu drogowego. Przyjmuje na wejściu zrealizowane wcześniej nagranie bądź strumień na żywo z kamery a następnie zlicza przejeżdżające pojazdy. Po przeanalizowaniu nagrania program ma możliwość zapisać zgromadzone dane w arkuszu kalkulacyjnym.

## Wymagania i instalacja

Aby uruchomić projekt, wymagany jest Python w wersji przynajmniej 3.10. Reszta zależności znajduje się w pliku requirements.txt.

1. Instalacja biblioteki systemowej dla interfejsu graficznego:
```bash
sudo apt-get install python3-tk
2. Instalacja wymaganych pakietów Python:
pip install opencv-python
pip install ultralytics
pip install pandas
pip install openpyxl
3. Instalacja biblioteki PyTorch ze wsparciem dla CUDA 12.1:
pip install torch==1.13.0+cu121 torchvision==0.14.0+cu121 torchaudio==0.13.0+cu121 -f [https://download.pytorch.org/whl/cu121/torch_stable.html](https://download.pytorch.org/whl/cu121/torch_stable.html)
