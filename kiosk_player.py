import cv2
import os
import sys
import json
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from functools import partial
import time
from PIL import Image, ImageTk
from datetime import datetime
import ctypes

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

if getattr(sys, 'frozen', False):
    application_path = os.path.dirname(sys.executable)
else:
    application_path = os.path.dirname(__file__)

CONFIG_FILE = os.path.join(application_path, 'config.json')
LOG_FILE = os.path.join(application_path, 'scan_log.txt')

config_data = {
    "default_video_path": "",
    "return_to_default_id": "", 
    "trigger_videos": {}
}
proceed_to_player = False

def log_scan(card_id, video_path):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"{timestamp}, ID: {card_id}, Video: {os.path.basename(video_path)}\n"
    try:
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(log_entry)
    except Exception as e:
        print(f"Could not write to log file: {e}")

def save_settings():
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config_data, f, indent=4, ensure_ascii=False)

def load_settings():
    global config_data
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                loaded_data = json.load(f)
                if "default_video_path" in loaded_data and "trigger_videos" in loaded_data:
                    config_data = loaded_data
                    return True
        except json.JSONDecodeError: return False
    return False

def run_settings_ui():
    global config_data, proceed_to_player
    window = tk.Tk(); window.title("RFID Kiosk Player - Settings"); window.geometry("750x700"); window.configure(bg="#F0F0F0")
    style = ttk.Style(window); style.configure("TButton", font=("Segoe UI", 10)); style.configure("TLabel", font=("Segoe UI", 10), background="#F0F0F0"); style.configure("Header.TLabel", font=("Segoe UI", 12, "bold"), background="#F0F0F0")
    try:
        icon_path = resource_path('icon.ico')
        if os.path.exists(icon_path): window.iconbitmap(icon_path)
    except Exception as e: print(f"Icon could not be loaded: {e}")
    def on_closing():
        global proceed_to_player; proceed_to_player = False; window.destroy()
    window.protocol("WM_DELETE_WINDOW", on_closing)
    try:
        logo_path = resource_path('logo.png'); original_image = Image.open(logo_path); desired_width = 400; aspect_ratio = original_image.height / original_image.width; desired_height = int(desired_width * aspect_ratio); resized_image = original_image.resize((desired_width, desired_height), Image.Resampling.LANCZOS); logo_img = ImageTk.PhotoImage(resized_image); logo_label = tk.Label(window, image=logo_img, background="#F0F0F0"); logo_label.image = logo_img; logo_label.pack(pady=(20,10))
    except Exception as e: print(f"Logo could not be loaded: {e}")
    ttk.Label(window, text="Assign videos to RFID Card IDs", style="Header.TLabel").pack(pady=(0, 10))
    
    special_keys_frame = ttk.LabelFrame(window, text="Special RFID Cards", padding=10)
    special_keys_frame.pack(fill='x', padx=10)
    ttk.Label(special_keys_frame, text="Card ID to return to Default Video:").pack(side="left", padx=(0,10))
    default_key_var = tk.StringVar(value=config_data.get("return_to_default_id", ""))
    default_key_entry = ttk.Entry(special_keys_frame, textvariable=default_key_var, width=20)
    default_key_entry.pack(side="left")

    default_frame = ttk.LabelFrame(window, text="Default Loop Video", padding=10); default_frame.pack(padx=10, pady=10, fill="x")
    default_path_var = tk.StringVar(value=config_data.get("default_video_path", "Not selected."))
    def select_default_video():
        file_path = filedialog.askopenfilename(title="Select Default Video", filetypes=(("Video Files", "*.mp4 *.avi *.mkv"),));
        if file_path: default_path_var.set(file_path)
    ttk.Label(default_frame, textvariable=default_path_var, width=70).grid(row=0, column=0, sticky="ew", padx=5); ttk.Button(default_frame, text="Select...", command=select_default_video).grid(row=0, column=1); default_frame.grid_columnconfigure(0, weight=1)
    trigger_frame = ttk.LabelFrame(window, text="Trigger Videos (Assigned to RFID Cards)", padding=10); trigger_frame.pack(padx=10, pady=5, fill="both", expand=True)
    canvas = tk.Canvas(trigger_frame, bg="#FFFFFF", highlightthickness=0); scrollbar = ttk.Scrollbar(trigger_frame, orient="vertical", command=canvas.yview); scrollable_frame = ttk.Frame(canvas)
    scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))); canvas.create_window((0, 0), window=scrollable_frame, anchor="nw"); canvas.configure(yscrollcommand=scrollbar.set); canvas.pack(side="left", fill="both", expand=True); scrollbar.pack(side="right", fill="y")
    ttk.Label(scrollable_frame, text="RFID Card ID", font=("Segoe UI", 10, "bold")).grid(row=0, column=0, padx=5); ttk.Label(scrollable_frame, text="Video File Path", font=("Segoe UI", 10, "bold")).grid(row=0, column=1, padx=5); ttk.Label(scrollable_frame, text="Loops", font=("Segoe UI", 10, "bold")).grid(row=0, column=2, padx=5)
    ui_rows = []
    def add_trigger_row(key="", video_path="", loops=1):
        row_num = len(ui_rows) + 1; frame = ttk.Frame(scrollable_frame); frame.grid(row=row_num, column=0, columnspan=5, sticky='ew', pady=2)
        key_entry = ttk.Entry(frame, width=20); key_entry.insert(0, key); key_entry.grid(row=0, column=0, padx=5)
        path_label = ttk.Label(frame, text=f"...{os.path.basename(video_path)}" if video_path else "Not selected.", width=40); path_label.video_path = video_path; path_label.grid(row=0, column=1, sticky="ew", padx=5)
        loops_spinbox = ttk.Spinbox(frame, from_=1, to=100, width=5); loops_spinbox.set(loops); loops_spinbox.grid(row=0, column=2, padx=5)
        def _select_video():
            file_path = filedialog.askopenfilename(title="Select Trigger Video")
            if file_path: path_label.config(text=f"...{os.path.basename(file_path)}"); path_label.video_path = file_path
        ttk.Button(frame, text="Select...", command=_select_video).grid(row=0, column=3, padx=5)
        def _delete_row(): frame.destroy(); ui_rows.remove(row_data)
        ttk.Button(frame, text="X", width=3, command=_delete_row).grid(row=0, column=4, padx=5)
        row_data = {'frame': frame, 'key': key_entry, 'path_label': path_label, 'loops': loops_spinbox}; ui_rows.append(row_data); frame.grid_columnconfigure(1, weight=1)
    for key, data in config_data.get("trigger_videos", {}).items(): add_trigger_row(key, data.get("path", ""), data.get("loops", 1))
    buttons_frame = ttk.Frame(window, padding=10); buttons_frame.pack(side="bottom", fill="x")
    ttk.Button(buttons_frame, text="Add RFID Trigger", command=add_trigger_row).pack(side="left")
    def save_and_start():
        global config_data, proceed_to_player
        if not default_path_var.get() or not os.path.exists(default_path_var.get()): messagebox.showerror("Error", "Please select a valid Default Loop Video."); return
        
        current_settings = { 
            "default_video_path": default_path_var.get(), 
            "return_to_default_id": default_key_var.get().strip(),
            "trigger_videos": {} 
        }
        for row in ui_rows:
            key = row['key'].get().strip(); path = getattr(row['path_label'], 'video_path', None); loops = int(row['loops'].get())
            if key and path and os.path.exists(path): current_settings["trigger_videos"][key] = {"path": path, "loops": loops}
        
        config_data = current_settings; save_settings(); proceed_to_player = True; window.destroy()
    ttk.Button(buttons_frame, text="Save and Start Player", command=save_and_start).pack(side="right")
    window.mainloop()

def start_player():
    if not config_data.get("default_video_path"): return
    try:
        ctypes.windll.user32.ShowCursor(0)
    except Exception as e: print(f"Could not hide cursor (ctypes): {e}")

    WINDOW_NAME = "Kiosk Player"
    cv2.namedWindow(WINDOW_NAME, cv2.WND_PROP_FULLSCREEN)
    cv2.setWindowProperty(WINDOW_NAME, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    
    default_video_path = config_data["default_video_path"]
    trigger_videos = config_data["trigger_videos"]
    return_to_default_id = config_data.get("return_to_default_id", "")

    current_video_path = default_video_path
    is_default_video = True; loop_count = 0; required_loops = 0

    cap = cv2.VideoCapture(current_video_path)
    if not cap.isOpened(): messagebox.showerror("Error", f"Could not open video file:\n{current_video_path}"); ctypes.windll.user32.ShowCursor(1); return
        
    fps = cap.get(cv2.CAP_PROP_FPS)
    if not (1 <= fps <= 120): fps = 30
    frame_duration = 1.0 / fps
    
    rfid_buffer = ""; last_frame_time = time.time()

    while True:
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q') or key == 27: break
            
        if key == 13:
            pressed_key = rfid_buffer.strip()
            rfid_buffer = ""
            
            if return_to_default_id and pressed_key == return_to_default_id:
                if not is_default_video:
                    is_default_video = True; current_video_path = default_video_path; cap.release(); cap = cv2.VideoCapture(current_video_path)
                    if not cap.isOpened(): break
                    fps = cap.get(cv2.CAP_PROP_FPS);
                    if not (1 <= fps <= 120): fps = 30
                    frame_duration = 1.0 / fps; last_frame_time = time.time()
            
            elif pressed_key in trigger_videos:
                video_info = trigger_videos[pressed_key]
                new_video_path = video_info["path"]
                log_scan(pressed_key, new_video_path)
                if not is_default_video and current_video_path == new_video_path:
                    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                elif is_default_video or current_video_path != new_video_path:
                    if os.path.exists(new_video_path):
                        current_video_path = new_video_path; is_default_video = False; loop_count = 0; required_loops = video_info["loops"]; cap.release(); cap = cv2.VideoCapture(current_video_path)
                        if not cap.isOpened(): break
                        fps = cap.get(cv2.CAP_PROP_FPS);
                        if not (1 <= fps <= 120): fps = 30
                        frame_duration = 1.0 / fps; last_frame_time = time.time()
        
        elif key != 255 and key != 13:
            try: rfid_buffer += chr(key)
            except: pass
        
        time_since_last_frame = time.time() - last_frame_time
        if time_since_last_frame >= frame_duration:
            last_frame_time = time.time()
            ret, frame = cap.read()
            if not ret:
                if is_default_video: cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                else:
                    loop_count += 1
                    if loop_count < required_loops: cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    else:
                        is_default_video = True; current_video_path = default_video_path; cap.release(); cap = cv2.VideoCapture(current_video_path)
                        if not cap.isOpened(): break
                        fps = cap.get(cv2.CAP_PROP_FPS);
                        if not (1 <= fps <= 120): fps = 30
                        frame_duration = 1.0 / fps
                continue
            cv2.imshow(WINDOW_NAME, frame)
            
    cap.release()
    cv2.destroyAllWindows()
    try:
        ctypes.windll.user32.ShowCursor(1)
    except Exception as e: print(f"Could not show cursor (ctypes): {e}")

if __name__ == "__main__":
    if load_settings(): start_player()
    else:
        run_settings_ui()
        if proceed_to_player: start_player()