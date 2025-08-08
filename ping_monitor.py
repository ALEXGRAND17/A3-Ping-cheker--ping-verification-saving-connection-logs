import tkinter as tk
from ttkbootstrap import Style
from ttkbootstrap.constants import *
from ttkbootstrap.widgets import Entry, Spinbox, Button, Checkbutton
from ping3 import ping
import threading
import time
import os
from datetime import datetime

# Цвета
BG_COLOR = "#2b2b2b"
FG_COLOR = "#ffffff"
ACCENT_COLOR = "#3c9ee7"

# Лог-файл
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)
log_filename = datetime.now().strftime("ping_log_%Y-%m-%d_%H-%M-%S.txt")
log_path = os.path.join(LOG_DIR, log_filename)

# Глобальные переменные
running = False
paused = False
start_time = None
success_count = 0
fail_count = 0
total_pings = 0
total_response_time = 0.0

def write_log(line):
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(line + "\n")

def monitor_ping():
    global running, paused, start_time, success_count, fail_count, total_pings, total_response_time
    while running:
        if paused:
            time.sleep(0.5)
            continue

        ip = ip_entry.get()
        port = port_entry.get()
        interval = int(interval_spinbox.get())

        try:
            response = ping(ip, timeout=2)
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            uptime_sec = int(time.time() - start_time)
            uptime_str = f"{uptime_sec // 3600:02}:{(uptime_sec // 60) % 60:02}:{uptime_sec % 60:02}"

            total_pings += 1

            if response is not None:
                success_count += 1
                total_response_time += response
                avg_ping = total_response_time / success_count * 1000
                status_str = "🟢 ONLINE"
                ping_display = f"{round(response * 1000, 2)} ms"
            else:
                fail_count += 1
                avg_ping = (total_response_time / success_count * 1000) if success_count else 0
                status_str = "🔴 OFFLINE"
                ping_display = "Timeout"

            packet_loss = round(fail_count / total_pings * 100, 2) if total_pings > 0 else 0

            vals = {
                "Ping": f"📶 Ping: {ping_display}",
                "PacketLoss": f"📉 Loss: {packet_loss}%",
                "Success": f"✅ Success: {success_count}",
                "Status": f"📡 Status: {status_str}",
                "Uptime": f"⏱️ Uptime: {uptime_str}",
                "AvgPing": f"📊 AvgPing: {round(avg_ping, 2)} ms",
                "TotalPings": f"🔢 Total: {total_pings}",
                "FailCount": f"❌ Fail: {fail_count}",
                "TotalResponseTime": f"⏲️ RespTime: {round(total_response_time, 3)} s",
            }

            root.after(0, lambda: update_meter_frame(vals))

            log_entry = (f"[{timestamp}] {ip}:{port} | Ping: {ping_display} | PacketLoss: {packet_loss}% | "
                         f"Success: {success_count} | Status: {status_str} | Uptime: {uptime_str} | "
                         f"AvgPing: {round(avg_ping, 2)} ms | TotalPings: {total_pings} | "
                         f"FailCount: {fail_count} | TotalResponseTime: {round(total_response_time,3)} s")

            root.after(0, lambda: log_text.insert(tk.END, log_entry + "\n"))
            root.after(0, lambda: log_text.see(tk.END))
            write_log(log_entry)

        except Exception as e:
            err = f"Error: {e}"
            root.after(0, lambda: log_text.insert(tk.END, err + "\n"))
            root.after(0, lambda: log_text.see(tk.END))
            write_log(err)

        time.sleep(interval)

def update_meter_frame(vals):
    for widget in meter_frame.winfo_children():
        widget.destroy()

    keys = [k for k in show_vars if show_vars[k].get()]
    font_style = ("Segoe UI", 14, "bold")
    columns = 3

    for i, key in enumerate(keys):
        row = i // columns
        col = i % columns
        lbl = tk.Label(meter_frame, text=vals[key], font=font_style, bg=BG_COLOR, fg=FG_COLOR)
        lbl.grid(row=row, column=col, sticky="w", padx=10, pady=6)

def on_check_change():
    dummy_vals = {k: f"{k}: --" for k in show_vars}
    update_meter_frame(dummy_vals)

def start_monitor():
    global running, paused, start_time, success_count, fail_count, total_pings, total_response_time
    if not running:
        running = True
        paused = False
        start_time = time.time()
        success_count = 0
        fail_count = 0
        total_pings = 0
        total_response_time = 0.0
        threading.Thread(target=monitor_ping, daemon=True).start()
        status_indicator.config(text="Running...", foreground="#44ff44")

def pause_monitor():
    global paused
    paused = not paused
    status_indicator.config(text="Paused" if paused else "Running...",
                            foreground="orange" if paused else "#44ff44")

def stop_monitor():
    global running
    running = False
    status_indicator.config(text="Stopped", foreground="red")

# --- UI ---
style = Style(theme="darkly")
root = style.master
root.title("Ping Monitor")
root.geometry("1000x700")
root.configure(bg=BG_COLOR)

show_vars = {
    "Ping": tk.BooleanVar(value=True),
    "PacketLoss": tk.BooleanVar(value=True),
    "Success": tk.BooleanVar(value=True),
    "Status": tk.BooleanVar(value=True),
    "Uptime": tk.BooleanVar(value=True),
    "AvgPing": tk.BooleanVar(value=True),
    "TotalPings": tk.BooleanVar(value=True),
    "FailCount": tk.BooleanVar(value=True),
    "TotalResponseTime": tk.BooleanVar(value=True),
}

# --- Layout ---
mainframe = tk.Frame(root, bg=BG_COLOR)
mainframe.pack(fill="both", expand=True, padx=10, pady=10)
mainframe.columnconfigure(0, weight=1)
mainframe.rowconfigure(3, weight=1)

# --- Controls ---
controls_frame = tk.Frame(mainframe, bg=BG_COLOR)
controls_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 5))
controls_frame.columnconfigure(9, weight=1)

tk.Label(controls_frame, text="Management", font=("Segoe UI", 14, "bold"), bg=BG_COLOR, fg=FG_COLOR)\
    .grid(row=0, column=0, columnspan=10, sticky="w", pady=(0, 6))

tk.Label(controls_frame, text="IP:", bg=BG_COLOR, fg=FG_COLOR).grid(row=1, column=0)
ip_entry = Entry(controls_frame, width=18)
ip_entry.insert(0, "8.8.8.8")
ip_entry.grid(row=1, column=1)

tk.Label(controls_frame, text="Port:", bg=BG_COLOR, fg=FG_COLOR).grid(row=1, column=2, padx=(10, 0))
port_entry = Entry(controls_frame, width=6)
port_entry.insert(0, "2302")
port_entry.grid(row=1, column=3)

tk.Label(controls_frame, text="Interval:", bg=BG_COLOR, fg=FG_COLOR).grid(row=1, column=4, padx=(10, 0))
interval_spinbox = Spinbox(controls_frame, from_=1, to=60, width=5)
interval_spinbox.set("2")
interval_spinbox.grid(row=1, column=5)

Button(controls_frame, text="Start", command=start_monitor, bootstyle="success-outline", width=10).grid(row=1, column=6, padx=(10, 0))
Button(controls_frame, text="Pause", command=pause_monitor, bootstyle="warning-outline", width=10).grid(row=1, column=7)
Button(controls_frame, text="Stop", command=stop_monitor, bootstyle="danger-outline", width=10).grid(row=1, column=8)

status_indicator = tk.Label(controls_frame, text="Stopped", fg="red", bg=BG_COLOR, font=("Segoe UI", 10, "bold"))
status_indicator.grid(row=1, column=9, sticky="e", padx=10)

# --- Middle ---
middle_frame = tk.Frame(mainframe, bg=BG_COLOR)
middle_frame.grid(row=1, column=0, columnspan=2, sticky="nsew", pady=10)
middle_frame.columnconfigure(0, weight=1)
middle_frame.columnconfigure(1, weight=0)

# Приборка
left_frame = tk.Frame(middle_frame, bg=BG_COLOR)
left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 20))
tk.Label(left_frame, text="📟 Info", font=("Segoe UI", 14, "bold"), bg=BG_COLOR, fg=FG_COLOR).pack(anchor="w", pady=(0, 6))
meter_frame = tk.Frame(left_frame, bg=BG_COLOR)
meter_frame.pack(anchor="w", fill="x")

# Show/Hide
right_frame = tk.Frame(middle_frame, bg=BG_COLOR)
right_frame.grid(row=0, column=1, sticky="n")
tk.Label(right_frame, text="🧩 Show/Hide", font=("Segoe UI", 14, "bold"), bg=BG_COLOR, fg=FG_COLOR).pack(anchor="center", pady=(0, 6))

checkbox_frame = tk.Frame(right_frame, bg=BG_COLOR)
checkbox_frame.pack()
for i, key in enumerate(show_vars):
    col = i % 2
    row = i // 2
    cb = Checkbutton(checkbox_frame, text=key, variable=show_vars[key], command=on_check_change,
                     bootstyle="info-round-toggle", width=14)
    cb.grid(row=row, column=col, sticky="w", padx=4, pady=2)

# --- Log ---
tk.Label(mainframe, text="📜 Log", font=("Segoe UI", 14, "bold"), bg=BG_COLOR, fg=FG_COLOR)\
    .grid(row=2, column=0, columnspan=2, sticky="w", pady=(10, 0))

log_container = tk.Frame(mainframe, bg=BG_COLOR)
log_container.grid(row=3, column=0, columnspan=2, sticky="nsew")
log_container.columnconfigure(0, weight=1)
log_container.rowconfigure(0, weight=1)

log_text = tk.Text(log_container, height=15, wrap="word", font=("Consolas", 10),
                   bg="#1e1e1e", fg="#00ff00", insertbackground="#00ff00")
log_text.grid(row=0, column=0, sticky="nsew")

scrollbar = tk.Scrollbar(log_container, command=log_text.yview)
scrollbar.grid(row=0, column=1, sticky='ns')
log_text.config(yscrollcommand=scrollbar.set)

on_check_change()
root.mainloop()
