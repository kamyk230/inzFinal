import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox, Checkbutton, IntVar, Radiobutton, Scale, OptionMenu, \
    StringVar, Spinbox
from tracker import Tracker
from analysis import run_analysis
from utils import show_error_message
import torch
import queue
import cv2


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Konfiguracja analizy - Panel Badawczy")
        self.geometry("750x1100")
        self.resizable(False, False)
        self.console_output = tk.Text(self, height=60, width=50, state="disabled")
        self.console_output.pack(side="right", padx=10, pady=10)

        self.device_var = tk.StringVar(value="cpu")
        self.gpu_available = torch.cuda.is_available()
        self.device = torch.device("cpu")

        self.use_camera_var = IntVar()
        self.model = None
        self.tracker = Tracker()
        self.source = None
        self.line_position = None
        self.line_orientation = tk.StringVar(value="pozioma")
        self.frame_skip = 1
        self.offset = 10
        self.mode = None
        self.save_path = None
        self.vehicle_choices = {"Samochody": tk.BooleanVar(value=True), "Ciężarówki": tk.BooleanVar(),
                                "Motocykle": tk.BooleanVar()}
        self.reset_interval_minutes = 1
        self.show_bboxes_var = tk.BooleanVar(value=True)

        # ZMIENNE BADAWCZE
        self.model_type_var = tk.StringVar(value="yolov8s.pt")
        self.resolution_var = tk.StringVar(value="1024x576")
        self.conf_threshold_var = tk.DoubleVar(value=0.25)
        self.use_fp16_var = tk.BooleanVar(value=False)
        self.skip_frames_var = tk.IntVar(value=1)

        self.stop_analysis_flag = False

        self.message_queue = queue.Queue()
        self.initialize_ui()
        self.process_queue()

    def initialize_ui(self):
        # Sekcja wyboru cpu/gpu
        device_label = tk.Label(self, text="Wybierz urządzenie:")
        device_label.pack(pady=(5, 0), anchor="w", padx=10)

        device_frame = tk.Frame(self, padx=10, pady=2)
        device_frame.pack(pady=2, padx=10, fill="x")

        tk.Radiobutton(device_frame, text="CPU", variable=self.device_var, value="cpu").pack(anchor="w")
        self.gpu_radiobutton = tk.Radiobutton(device_frame, text="GPU", variable=self.device_var, value="cuda")
        if self.gpu_available:
            self.gpu_radiobutton.pack(anchor="w")
            self.device_var.set("cuda")
        else:
            self.gpu_radiobutton.pack(anchor="w")
            self.gpu_radiobutton.config(state="disabled")
            tk.Label(device_frame, text="GPU nie jest dostępne").pack(anchor="w")

        tk.Button(device_frame, text="Zastosuj Urządzenie", command=self.apply_device_selection).pack(pady=2,
                                                                                                      anchor="w")
        self.device_info_label = tk.Label(self, text=f"Używane urządzenie: {self.device_var.get().upper()}")
        self.device_info_label.pack(pady=2, anchor="w", padx=10)

        research_label = tk.Label(self, text="--- PARAMETRY BADAWCZE ---", font=("Arial", 10, "bold"))
        research_label.pack(pady=(10, 5), anchor="center")

        research_frame = tk.Frame(self, padx=10, pady=5, borderwidth=1, relief="solid")
        research_frame.pack(pady=5, padx=10, fill="x")

        tk.Label(research_frame, text="Wybierz Model (Architektura):").pack(anchor="w")
        models = ["yolov8n.pt", "yolov8s.pt", "yolov8m.pt"]
        OptionMenu(research_frame, self.model_type_var, *models).pack(anchor="w", fill="x")

        tk.Label(research_frame, text="Rozdzielczość Analizy (Wymagane wielokrotności 32):").pack(anchor="w",
                                                                                                  pady=(5, 0))
        resolutions = ["1280x736", "1024x576", "960x544", "640x384", "480x288"]
        OptionMenu(research_frame, self.resolution_var, *resolutions).pack(anchor="w", fill="x")

        tk.Label(research_frame, text="Próg Pewności (Confidence):").pack(anchor="w", pady=(5, 0))
        Scale(research_frame, variable=self.conf_threshold_var, from_=0.05, to=0.95, resolution=0.05,
              orient="horizontal").pack(fill="x")

        tk.Checkbutton(research_frame, text="Użyj FP16 (Half-Precision) [Zalecane GPU]",
                       variable=self.use_fp16_var).pack(anchor="w", pady=(5, 0))

        mode_label = tk.Label(self, text="Wybierz tryb pracy aplikacji:")
        mode_label.pack(pady=(10, 0), anchor="w", padx=10)
        mode_frame = tk.Frame(self, padx=10, pady=5)
        mode_frame.pack(pady=5, padx=10, fill="x")
        tk.Button(mode_frame, text="Display (Podgląd)", command=lambda: self.set_mode("display")).pack(side="left",
                                                                                                       padx=5)
        tk.Button(mode_frame, text="Record (Zapis do Excel)", command=lambda: self.set_mode("record")).pack(side="left",
                                                                                                            padx=5)

        tk.Label(self, text="Konfiguracja Linii Zliczającej:").pack(pady=(10, 0), anchor="w", padx=10)
        line_frame = tk.Frame(self, padx=10, pady=5)
        line_frame.pack(pady=5, padx=10, fill="x")
        tk.Radiobutton(line_frame, text="Pozioma", variable=self.line_orientation, value="pozioma").pack(anchor="w")
        tk.Radiobutton(line_frame, text="Pionowa", variable=self.line_orientation, value="pionowa").pack(anchor="w")
        tk.Label(line_frame, text="Pozycja (piksele):").pack(anchor="w")
        self.line_position_entry = tk.Entry(line_frame)
        self.line_position_entry.pack(fill="x")

        tk.Button(line_frame, text="👁 Pokaż podgląd linii", command=self.preview_line_position, bg="#e0f7fa").pack(
            fill="x", pady=5)

        tk.Label(self, text="Pojazdy:").pack(pady=(5, 0), anchor="w", padx=10)
        vehicle_frame = tk.Frame(self, padx=10, pady=2)
        vehicle_frame.pack(pady=2, padx=10, fill="x")
        for vehicle, var in self.vehicle_choices.items():
            Checkbutton(vehicle_frame, text=vehicle, variable=var).pack(anchor="w")

        tk.Label(self, text="Analizuj co N-tą klatkę (1 = każdą, 2 = co drugą...):").pack(pady=(5, 0), anchor="w",
                                                                                          padx=10)
        speed_frame = tk.Frame(self, padx=10, pady=2)
        speed_frame.pack(pady=2, padx=10, fill="x")

        Spinbox(speed_frame, from_=1, to=60, textvariable=self.skip_frames_var, width=5).pack(side="left")
        tk.Label(speed_frame, text="(Większa wartość = szybciej, ale mniej dokładnie)").pack(side="left", padx=5)

        tk.Label(self, text="Źródło wideo:").pack(pady=(5, 0), anchor="w", padx=10)
        source_frame = tk.Frame(self, padx=10, pady=2)
        source_frame.pack(pady=2, padx=10, fill="x")
        tk.Button(source_frame, text="Plik wideo", command=self.select_source).pack(side="left", padx=5)
        Checkbutton(source_frame, text="Kamera", variable=self.use_camera_var).pack(side="left", padx=10)

        viz_frame = tk.Frame(self, padx=10, pady=5)
        viz_frame.pack(pady=5, padx=10, fill="x")
        Checkbutton(viz_frame, text="Pokazuj bounding boxy", variable=self.show_bboxes_var).pack(anchor="w")
        tk.Button(viz_frame, text="Interwał zapisu (min)", command=self.set_reset_interval).pack(anchor="w")

        tk.Button(self, text="URUCHOM ANALIZĘ", bg="#dddddd", command=lambda: self.start_analysis()).pack(pady=10,
                                                                                                          padx=10,
                                                                                                          fill="x")
        tk.Button(self, text="ZATRZYMAJ ANALIZĘ", bg="#ffaaaa", command=self.stop_analysis).pack(pady=5, padx=10,
                                                                                                 fill="x")
        tk.Button(self, text="Zamknij", command=self.destroy).pack(pady=5, padx=10, fill="x")

    def apply_device_selection(self):
        selected_device = self.device_var.get()
        self.device = torch.device(selected_device)
        self.device_info_label.config(text=f"Używane urządzenie: {selected_device.upper()}")
        self.show_message("Urządzenie", f"Wybrano urządzenie: {selected_device.upper()}")
        if self.model is not None:
            del self.model
            self.model = None

    def set_mode(self, mode):
        self.mode = mode
        if mode == "record":
            self.save_path = filedialog.asksaveasfilename(defaultextension=".xlsx",
                                                          filetypes=[("Pliki Excel", "*.xlsx")],
                                                          title="Zapisz wyniki jako")
        self.show_message("Tryb pracy", f"Ustawiono tryb: {mode}")

    def set_reset_interval(self):
        val = simpledialog.askinteger("Interwał", "Podaj minuty:", minvalue=1, maxvalue=60)
        if val: self.reset_interval_minutes = val

    def select_source(self):
        if self.use_camera_var.get() == 0:
            self.source = filedialog.askopenfilename(filetypes=[("Video", "*.mp4 *.avi *.mov *.mkv")])
            if self.source: self.show_message("Wideo", "Wybrano plik.")
        else:
            self.source = 0

    def show_message(self, title, message):
        self.console_output.configure(state="normal")
        self.console_output.insert("end", f"[{title}]: {message}\n")
        self.console_output.configure(state="disabled")
        self.console_output.see("end")

    def preview_line_position(self):
        # Walidacja wejścia
        if not self.source and self.use_camera_var.get() == 0:
            messagebox.showerror("Błąd", "Najpierw wybierz źródło wideo!")
            return

        try:
            line_pos = int(self.line_position_entry.get())
        except ValueError:
            messagebox.showerror("Błąd", "Wpisz poprawną pozycję linii (liczbę).")
            return

        try:
            target_w, target_h = map(int, self.resolution_var.get().split('x'))
        except:
            target_w, target_h = 1024, 576

        source = self.source if not self.use_camera_var.get() else 0
        cap = cv2.VideoCapture(source)
        if not cap.isOpened():
            messagebox.showerror("Błąd", "Nie można otworzyć wideo.")
            return

        ret, frame = cap.read()
        cap.release()

        if ret:
            frame_resized = cv2.resize(frame, (target_w, target_h))
            orientation = self.line_orientation.get()

            if orientation == "pozioma":
                cv2.line(frame_resized, (0, line_pos), (target_w, line_pos), (0, 0, 255), 2)
                cv2.putText(frame_resized, f"Y={line_pos}", (10, line_pos - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7,
                            (0, 0, 255), 2)
            else:
                cv2.line(frame_resized, (line_pos, 0), (line_pos, target_h), (0, 0, 255), 2)
                cv2.putText(frame_resized, f"X={line_pos}", (line_pos + 10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.7,
                            (0, 0, 255), 2)

            cv2.imshow("PODGLAD LINII (Wcisnij dowolny klawisz aby zamknac)", frame_resized)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
        else:
            messagebox.showerror("Błąd", "Nie udało się pobrać klatki z wideo.")

    def start_analysis(self):
        try:
            self.frame_skip = int(self.skip_frames_var.get())
            if self.frame_skip < 1: self.frame_skip = 1
        except:
            self.frame_skip = 1


        self.offset = 10 + (self.frame_skip * 3)

        self.show_message("Konfiguracja", f"Analiza co {self.frame_skip}. klatkę. Offset linii: +/- {self.offset}px")

        try:
            val = int(self.line_position_entry.get())
            if 0 < val < 2000:
                self.line_position = val
            else:
                raise ValueError
        except:
            self.show_message("Błąd", "Niepoprawna pozycja linii.")
            return

        if not self.mode:
            self.show_message("Błąd", "Wybierz tryb (Display/Record).")
            return
        if not self.source and self.use_camera_var.get() == 0:
            self.show_message("Błąd", "Brak źródła wideo.")
            return

        import threading
        self.stop_analysis_flag = False
        analysis_thread = threading.Thread(target=run_analysis, args=(self,))
        analysis_thread.start()

    def stop_analysis(self):
        self.stop_analysis_flag = True
        self.show_message("Akcja", "Zatrzymano")

    def process_queue(self):
        try:
            while True:
                msg = self.message_queue.get_nowait()
                self.show_message("INFO", msg)
        except queue.Empty:
            pass
        self.after(100, self.process_queue)