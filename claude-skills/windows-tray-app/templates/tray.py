"""FanTray: minimal Windows tray app in Python (pystray + tkinter).

pip install pystray==0.19.5 Pillow==10.4.0 pyinstaller==6.10.0
Run:   pythonw tray.py
Build: pyinstaller --noconsole --onefile --name FanTray --icon app.ico --hidden-import pystray._win32 tray.py
"""
import ctypes, json, os, queue, sys, threading, tkinter as tk, winreg
from pathlib import Path
import pystray
from PIL import Image, ImageDraw

APP, MUTEX = "FanTray", "FanTray-7f3c2a"
SETTINGS = Path(os.environ["APPDATA"]) / APP / "settings.json"
DEFAULTS = {"port": "COM3", "default_percent": 40, "start_with_windows": False}
RUN_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"

def load():
    try: return {**DEFAULTS, **json.loads(SETTINGS.read_text(encoding="utf-8"))}
    except (OSError, ValueError): return dict(DEFAULTS)

def save(s):
    SETTINGS.parent.mkdir(parents=True, exist_ok=True)
    tmp = SETTINGS.with_suffix(".tmp"); tmp.write_text(json.dumps(s, indent=2), encoding="utf-8"); os.replace(tmp, SETTINGS)
    frozen = getattr(sys, "frozen", False)   # True inside the PyInstaller exe
    cmd = f'"{sys.executable}"' if frozen else f'"{sys.executable.replace("python.exe", "pythonw.exe")}" "{Path(__file__).resolve()}"'
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY, 0, winreg.KEY_SET_VALUE) as key:
        if s["start_with_windows"]: winreg.SetValueEx(key, APP, 0, winreg.REG_SZ, cmd)
        else:
            try: winreg.DeleteValue(key, APP)
            except FileNotFoundError: pass

def icon_image():
    img = Image.new("RGBA", (64, 64), (0, 0, 0, 0))   # or Image.open("app.ico")
    ImageDraw.Draw(img).ellipse((4, 4, 60, 60), fill=(30, 110, 200, 255))
    return img

class App:
    def __init__(self):
        self.s, self.jobs, self.win = load(), queue.Queue(), None
        self.root = tk.Tk(); self.root.withdraw()          # hidden root; windows are Toplevels
        self.icon = pystray.Icon(APP, icon_image(), APP, pystray.Menu(
            pystray.MenuItem("Settings...", lambda: self.jobs.put(self.settings), default=True),
            pystray.MenuItem("Exit", lambda: self.jobs.put(self.quit))))
    def run(self):
        threading.Thread(target=self.icon.run, daemon=True).start()
        self.root.after(100, self.poll); self.root.mainloop()
    def poll(self):
        while not self.jobs.empty(): self.jobs.get()()
        self.root.after(100, self.poll)
    def settings(self):
        if self.win and self.win.winfo_exists(): self.win.deiconify(); self.win.lift(); return
        w = self.win = tk.Toplevel(self.root); w.title(f"{APP} settings"); w.resizable(False, False)
        port, pct = tk.StringVar(value=self.s["port"]), tk.IntVar(value=self.s["default_percent"])
        auto = tk.BooleanVar(value=self.s["start_with_windows"])
        tk.Label(w, text="Serial port").grid(row=0, column=0, sticky="w", padx=8, pady=4)
        tk.Entry(w, textvariable=port).grid(row=0, column=1, padx=8)
        tk.Label(w, text="Default fan %").grid(row=1, column=0, sticky="w", padx=8)
        tk.Spinbox(w, from_=0, to=100, textvariable=pct, width=5).grid(row=1, column=1, sticky="w", padx=8)
        tk.Checkbutton(w, text="Start with Windows", variable=auto).grid(row=2, columnspan=2, sticky="w", padx=8)
        def ok():
            self.s.update(port=port.get().strip(), default_percent=max(0, min(100, pct.get())), start_with_windows=auto.get())
            save(self.s); w.destroy()
        tk.Button(w, text="OK", width=10, command=ok).grid(row=3, column=0, pady=8)
        tk.Button(w, text="Cancel", width=10, command=w.destroy).grid(row=3, column=1, pady=8)
    def quit(self):
        self.icon.stop(); self.root.destroy()

if __name__ == "__main__":
    k32 = ctypes.WinDLL("kernel32", use_last_error=True)
    handle = k32.CreateMutexW(None, False, MUTEX)                 # keep the handle alive
    if ctypes.get_last_error() == 183: sys.exit(0)                # ERROR_ALREADY_EXISTS
    ctypes.windll.shcore.SetProcessDpiAwareness(1)                # sharp text on 125-200 % scaling
    App().run()
