import cv2
import time
import torch
from model_handler import ModelHandler
from utils import load_class_list, save_to_excel, show_error_message


def run_analysis(app):
    # 1. Pobieranie parametrów badawczych z GUI
    selected_model_name = app.model_type_var.get()
    res_string = app.resolution_var.get()
    try:
        target_w, target_h = map(int, res_string.split('x'))
    except:
        target_w, target_h = 1024, 576

    conf_threshold = app.conf_threshold_var.get()
    use_fp16 = app.use_fp16_var.get()

    app.message_queue.put(f"KONFIGURACJA BADAWCZA:")
    app.message_queue.put(f"Model: {selected_model_name}")
    app.message_queue.put(f"Rozdzielczość: {target_w}x{target_h}")
    app.message_queue.put(f"Confidence: {conf_threshold}")
    app.message_queue.put(f"Frame Skip: {app.frame_skip}")
    app.message_queue.put(f"FP16: {'TAK' if use_fp16 else 'NIE'}")

    # 2. Inicjalizacja modelu
    model_handler = ModelHandler(device=app.device_var.get())
    try:
        model = model_handler.load_specific_model(selected_model_name)
    except Exception as e:
        show_error_message("Błąd ładowania modelu", str(e))
        return

    # Otwieranie źródła wideo
    source = app.source if not app.use_camera_var.get() else 0
    cap = cv2.VideoCapture(source)
    if not cap.isOpened():
        app.message_queue.put("Nie można otworzyć źródła wideo.")
        return

    fps = cap.get(cv2.CAP_PROP_FPS)
    fps = fps if fps != 0 else 30
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    # Inicjalizacja liczników
    counter_up = counter_down = counter_right = counter_left = 0
    directions = {}
    start_time = time.time()
    frame_count = minute_count = 0
    traffic_data = []

    class_list = load_class_list()
    if not class_list:
        cap.release()
        return

    app.message_queue.put("Rozpoczęto analizę... (SPACJA = PAUZA)")
    orientation = app.line_orientation.get()
    bbox_id = []
    inference_times = []

    paused = False

    # Funkcja pomocnicza do rysowania tekstu z obrysem
    def draw_text_outlined(img, text, pos, font_scale=0.7, thickness=2, color=(255, 255, 255)):
        cv2.putText(img, text, pos, cv2.FONT_HERSHEY_SIMPLEX, font_scale, (0, 0, 0), thickness + 3)
        cv2.putText(img, text, pos, cv2.FONT_HERSHEY_SIMPLEX, font_scale, color, thickness)

    while cap.isOpened():
        if hasattr(app, 'stop_analysis_flag') and app.stop_analysis_flag:
            app.message_queue.put("Analiza zatrzymana")
            break
        if not paused:
            ret, frame = cap.read()
            if not ret:
                break

            # SKALOWANIE
            frame_resized = cv2.resize(frame, (target_w, target_h))

            current_skip = app.frame_skip

            if frame_count % current_skip == 0:
                t_start = time.time()

                # INFERENCJA
                results = model.predict(frame_resized, conf=conf_threshold, half=use_fp16, verbose=False,
                                        device=app.device)

                t_end = time.time()
                inference_times.append(t_end - t_start)

                detections = results[0].boxes.data.cpu().numpy()
                detected_objects = []

                for det in detections:
                    x1, y1, x2, y2, conf, cls_id = det
                    cls_id = int(cls_id)
                    if cls_id < len(class_list):
                        c = class_list[cls_id]
                        if ('car' in c and app.vehicle_choices["Samochody"].get()) or \
                                ('truck' in c and app.vehicle_choices["Ciężarówki"].get()) or \
                                ('motorcycle' in c and app.vehicle_choices["Motocykle"].get()):
                            detected_objects.append([int(x1), int(y1), int(x2), int(y2)])

                bbox_id = app.tracker.update(detected_objects)

                for bbox in bbox_id:
                    x3, y3, x4, y4, id = bbox
                    cx, cy = (x3 + x4) // 2, (y3 + y4) // 2

                    if id not in directions:
                        directions[id] = {'prev_cx': cx, 'prev_cy': cy, 'crossed': False}
                    else:
                        if not directions[id]['crossed']:
                            if orientation == "pozioma" and (
                                    app.line_position - app.offset < cy < app.line_position + app.offset):
                                if cy > directions[id]['prev_cy']:
                                    counter_down += 1
                                elif cy < directions[id]['prev_cy']:
                                    counter_up += 1
                                directions[id]['crossed'] = True
                            elif orientation == "pionowa" and (
                                    app.line_position - app.offset < cx < app.line_position + app.offset):
                                if cx > directions[id]['prev_cx']:
                                    counter_right += 1
                                elif cx < directions[id]['prev_cx']:
                                    counter_left += 1
                                directions[id]['crossed'] = True
                        directions[id]['prev_cx'] = cx
                        directions[id]['prev_cy'] = cy

            frame_count += 1
            current_time_video = frame_count / fps

            if current_time_video >= (minute_count + 1) * 60:
                avg_inf = sum(inference_times) / len(inference_times) if inference_times else 0
                fps_proc = 1.0 / avg_inf if avg_inf > 0 else 0

                row = {
                    "Czas": f"{minute_count + 1}:00",
                    "Model": selected_model_name,
                    "Res": f"{target_w}x{target_h}",
                    "FPS_Inferencji": round(fps_proc, 2),
                    "FP16": "TAK" if use_fp16 else "NIE"
                }
                if orientation == "pozioma":
                    row.update({"W górę": counter_up, "W dół": counter_down})
                else:
                    row.update({"W prawo": counter_right, "W lewo": counter_left})

                traffic_data.append(row)
                counter_up = counter_down = counter_right = counter_left = 0
                minute_count += 1
                inference_times = []

            if frame_count % 30 == 0:
                app.message_queue.put(f"Klatka: {frame_count}/{total_frames}")

        # RYSOWANIE
        if app.mode == "display":
            display_frame = frame_resized.copy()

            if paused:
                draw_text_outlined(display_frame, "PAUZA (Spacja aby wznowic)", (50, 50), font_scale=1, thickness=2,
                                   color=(0, 0, 255))

            if app.show_bboxes_var.get():
                for bbox in bbox_id:
                    x3, y3, x4, y4, id = bbox
                    cv2.rectangle(display_frame, (x3, y3), (x4, y4), (0, 255, 0), 2)
                    draw_text_outlined(display_frame, str(id), (x3, y3 - 10), font_scale=0.5, thickness=1)

            if orientation == "pozioma":
                cv2.line(display_frame, (0, app.line_position), (target_w, app.line_position), (0, 255, 255), 2)
                draw_text_outlined(display_frame, f'Up: {counter_up}', (10, 50), font_scale=0.8, thickness=2)
                draw_text_outlined(display_frame, f'Down: {counter_down}', (10, 90), font_scale=0.8, thickness=2)

            elif orientation == "pionowa":
                cv2.line(display_frame, (app.line_position, 0), (app.line_position, target_h), (0, 255, 255), 2)
                draw_text_outlined(display_frame, f'Left: {counter_left}', (10, 50), font_scale=0.8, thickness=2)
                draw_text_outlined(display_frame, f'Right: {counter_right}', (10, 90), font_scale=0.8, thickness=2)

            cv2.imshow("Panel Badawczy", display_frame)

            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord(' '):
                paused = not paused

    cap.release()
    cv2.destroyAllWindows()

    if app.mode == "record" and app.save_path:
        total_real_time = time.time() - start_time
        traffic_data.append({
            "Czas": "PODSUMOWANIE",
            "Model": f"Czas całk.: {round(total_real_time, 2)}s",
            "Res": "",
            "FPS_Inferencji": "",
            "FP16": ""
        })
        save_to_excel(traffic_data, app.save_path)
        app.message_queue.put(f"Zapisano wyniki do {app.save_path}")

    app.message_queue.put("Badanie zakończone.")