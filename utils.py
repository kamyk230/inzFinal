import tkinter as tk
from tkinter import messagebox
import pandas as pd

def show_error_message(title, message):
    root = tk.Tk()
    root.withdraw()
    messagebox.showerror(title, message)
    root.destroy()

def load_class_list(file_path="coco.txt"):
    try:
        with open(file_path, "r") as file:
            class_list = file.read().strip().split("\n")
        return class_list
    except FileNotFoundError:
        show_error_message("Błąd", f"Plik '{file_path}' nie został znaleziony.")
        return []

def save_to_excel(data, save_path):
    df = pd.DataFrame(data)
    try:
        df.to_excel(save_path, index=False)
        print(f"Dane zostały zapisane do {save_path}")
    except Exception as e:
        show_error_message("Błąd zapisu", f"Nie udało się zapisać pliku: {e}")
