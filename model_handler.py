import torch
from ultralytics import YOLO
from utils import show_error_message


class ModelHandler:
    def __init__(self, device="cpu"):
        self.device = torch.device(device)
        self.model = None

    def load_model(self, model_path):
        try:
            self.model = YOLO(model_path).to(self.device)
            print(f"Model {model_path} załadowany poprawnie na {self.device.type.upper()}.")
        except Exception as e:
            show_error_message("Błąd ładowania modelu", f"Nie udało się załadować modelu {model_path}: {e}")
            raise e

    def get_model(self, model_path='yolov8s.pt'):
        if self.model is None or self.model.task != 'detect':
            self.load_model(model_path)
        return self.model

    def load_specific_model(self, model_path):
        self.load_model(model_path)
        return self.model