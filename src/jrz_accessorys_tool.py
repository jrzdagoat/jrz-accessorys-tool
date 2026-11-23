"""
jrz's Accessory's Tool
Generates client-side FiveM visual files: weather, lightning, time lock and ped lighting.

Run:  python jrz_accessorys_tool.py      (Python 3.9+, tkinter is built in)
Output: <Documents>/jrz Accessory's Tool/Output/jrz_accessory
"""
import math
import os
import random
import subprocess
import sys
import tkinter as tk
from tkinter import colorchooser
from pathlib import Path

APP = "jrz's Accessory's Tool"
OUT = Path.home() / "Documents" / "jrz Accessory's Tool" / "Output"

# ---------- theme ----------
BG, SIDE, PANEL = "#050706", "#07090a", "#0b0e0d"
BORDER, FG, MUTED = "#1a1e1c", "#ececec", "#7d8481"
ACCENT, ACCENT_H, ACCENT_D = "#c8102e", "#e3173a", "#2e0a12"
FONT = "Segoe UI"

# ---------- content ----------
# (label, value, description)
TABS = {
    "Snow": [
        ("Blizzard", "BLIZZARD", "Heavy snowfall driven by strong wind."),
        ("Heavy Snow", "SNOW", "Steady snowfall across the whole map."),
        ("Light Snow", "SNOWLIGHT", "Gentle flurries and a light dusting."),
        ("Snow Ground Only", "XMAS", "Snowy ground with only a light flurry."),
        ("Remove Snow", None, "Leave snow out of the generated pack."),
    ],
    "Rain": [
        ("Thunderstorm", "THUNDER", "Heavy rain with storm clouds."),
        ("Heavy Rain", "RAIN", "Constant, heavy rain."),
        ("Light Rain", "CLEARING", "Light rain that looks like it is clearing."),
        ("Overcast", "OVERCAST", "Grey, flat skies with no rain."),
        ("Remove Rain", None, "Leave rain out of the generated pack."),
    ],
    "Lightning": [
        ("Storm Flashes", "THUNDER", "Storm weather plus random lightning flashes."),
        ("Flashes Only", "FLASH", "Keep your current weather, add lightning flashes."),
        ("Remove Lightning", None, "Leave lightning out of the generated pack."),
    ],
    "Time Lock": [
        ("Lock Time", "lock", "Pin the in-game clock to the time you choose."),
        ("Unlock Time", None, "Leave the clock alone."),
    ],
    "Ped Light": [
        ("White Peds", "white", "Peds are lit pure white."),
        ("Black Peds", "black", "Peds are lit pure black."),
        ("Custom Colour", "custom", "Peds are lit with the colour you pick on the right."),
        ("Normal Peds", None, "Leave ped lighting alone."),
    ],
}
WEATHER_TABS = ("Snow", "Rain", "Lightning")

# key, label, lo, hi, default, step, format
SLIDERS = {
    "Snow": [("wind", "WIND SPEED", 0, 12, 2.0, 0.5, "x{:.1f}"),
             ("dir", "WIND DIRECTION", 0, 360, 0, 5, "{:.0f}\u00b0")],
    "Rain": [("rain", "RAIN AMOUNT", 0, 1, 0.8, 0.05, "{:.2f}"),
             ("wind", "WIND SPEED", 0, 12, 1.0, 0.5, "x{:.1f}"),
             ("dir", "WIND DIRECTION", 0, 360, 0, 5, "{:.0f}\u00b0")],
    "Lightning": [("interval", "FLASH INTERVAL", 2, 60, 10, 1, "{:.0f}s")],
    "Time Lock": [("hour", "HOUR", 0, 23, 12, 1, "{:02.0f}"),
                  ("minute", "MINUTE", 0, 59, 0, 1, "{:02.0f}")],
    "Ped Light": [("intensity", "LIGHT INTENSITY", 0, 20, 4.0, 0.5, "{:.1f}"),
                  ("shine", "SHINE", 0, 5, 0.0, 0.1, "{:.1f}")],
}

# kind, key, label, default
SETTINGS = {
    "Snow": [("toggle", "ground", "Snow on the ground", True),
             ("toggle", "trails", "Vehicle & footprint trails", True)],
    "Rain": [("toggle", "storm", "Add thunder flashes", False)],
    "Lightning": [("toggle", "jitter", "Randomise flash timing", True)],
    "Time Lock": [("toggle", "freeze", "Freeze the clock", True)],
    "Ped Light": [("color", "colour", "Custom colour", "#ffffff")],
}


# ---------- small widgets ----------
class Toggle(tk.Canvas):
    def __init__(self, parent, var, bg=PANEL, command=None):
        super().__init__(parent, width=34, height=18, bg=bg,
                         highlightthickness=0, cursor="hand2")
        self.var, self.command = var, command
        self.bind("<Button-1>", self._click)
        var.trace_add("write", lambda *a: self.draw())
        self.draw()

    def _click(self, _):
        self.var.set(not self.var.get())
        if self.command:
            self.command()

    def draw(self):
        self.delete("all")
        on = self.var.get()
        col = ACCENT if on else "#2a2f2d"
        self.create_oval(1, 1, 17, 17, fill=col, outline=col)
        self.create_oval(17, 1, 33, 17, fill=col, outline=col)
        self.create_rectangle(9, 1, 25, 17, fill=col, outline=col)
        x = 25 if on else 9
        self.create_oval(x - 6, 3, x + 6, 15, fill="white", outline="white")


class Slider(tk.Frame):
    def __init__(self, parent, label, var, lo, hi, step, fmt, bg=SIDE):
        super().__init__(parent, bg=bg)
        self.var, self.lo, self.hi, self.step, self.fmt = var, lo, hi, step, fmt
        tk.Label(self, text=label, bg=bg, fg=MUTED,
                 font=(FONT, 7, "bold"), anchor="w").pack(fill="x")
        row = tk.Frame(self, bg=bg)
        row.pack(fill="x")
        self.cv = tk.Canvas(row, height=22, bg=bg, highlightthickness=0,
                            cursor="hand2")
        self.cv.pack(side="left", fill="x", expand=True)
        self.val = tk.Label(row, bg=bg, fg=FG, font=(FONT, 8, "bold"), width=6,
                            anchor="e")
        self.val.pack(side="right")
        self.cv.bind("<Configure>", lambda e: self.draw())
        self.cv.bind("<Button-1>", self._set)
        self.cv.bind("<B1-Motion>", self._set)
        var.trace_add("write", lambda *a: self.draw())

    def _set(self, e):
        w = max(1, self.cv.winfo_width() - 14)
        f = min(1, max(0, (e.x - 7) / w))
        v = self.lo + f * (self.hi - self.lo)
        v = round(v / self.step) * self.step
        self.var.set(round(min(self.hi, max(self.lo, v)), 4))

    def draw(self):
        c = self.cv
        c.delete("all")
        w = c.winfo_width()
        if w < 20:
            return
        f = (self.var.get() - self.lo) / (self.hi - self.lo)
        x = 7 + f * (w - 14)
        c.create_line(7, 11, w - 7, 11, fill="#262b29", width=4, capstyle="round")
        c.create_line(7, 11, x, 11, fill=ACCENT, width=4, capstyle="round")
        c.create_oval(x - 6, 5, x + 6, 17, fill=ACCENT, outline=ACCENT_H)
        self.val.config(text=self.fmt.format(self.var.get()))


class ColorField(tk.Frame):
    def __init__(self, parent, label, var, bg=PANEL):
        super().__init__(parent, bg=bg)
        self.var = var
        tk.Label(self, text=label, bg=bg, fg=MUTED, font=(FONT, 8)).pack(side="left")
        self.entry = tk.Entry(self, textvariable=var, width=9, bg="#101312", fg=FG,
                              insertbackground=FG, relief="flat",
                              highlightthickness=1, highlightbackground=BORDER,
                              highlightcolor=ACCENT, font=("Consolas", 9))
        self.entry.pack(side="right")
        self.sw = tk.Label(self, width=2, bg=var.get(), cursor="hand2")
        self.sw.pack(side="right", padx=8)
        self.sw.bind("<Button-1>", self._pick)
        var.trace_add("write", lambda *a: self._sync())

    def _pick(self, _):
        c = colorchooser.askcolor(color=self.var.get())[1]
        if c:
            self.var.set(c.upper())

    def _sync(self):
        v = self.var.get()
        if len(v) == 7 and v.startswith("#"):
            try:
                int(v[1:], 16)
                self.sw.config(bg=v)
            except ValueError:
                pass


def card(parent, title=None):
    f = tk.Frame(parent, bg=PANEL, highlightthickness=1, highlightbackground=BORDER)
    if title:
        tk.Label(f, text=title, bg=PANEL, fg=MUTED, font=(FONT, 7, "bold"),
                 anchor="w").pack(fill="x", padx=12, pady=(10, 4))
    return f


# ---------- app ----------
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP)
        self.geometry("1180x720")
        self.minsize(1000, 640)
        self.configure(bg=BG)

        self.tab = "Snow"
        self.sel = {t: len(m) - 1 for t, m in TABS.items()}  # everything "off"
        self.recent = []
        self.v = {t: {} for t in TABS}
        for t, sl in SLIDERS.items():
            for k, _l, lo, hi, d, *_ in sl:
                self.v[t][k] = tk.DoubleVar(value=d)
        for t, st in SETTINGS.items():
            for kind, k, _l, d in st:
                self.v[t][k] = (tk.BooleanVar(value=d) if kind == "toggle"
                                else tk.StringVar(value=d))
        self.lock = tk.BooleanVar(value=True)
        self.open_when = tk.BooleanVar(value=False)
        self.xmas = False
        self.bulbs = []

        self.build_top()
        self.build_body()
        self.build_status()
        self.show_tab("Snow")
        self.log("Ready. Pick a tab at the top and a mode on the left, then press Generate.")
        self.twinkle()

    # ----- top bar -----
    def build_top(self):
        top = tk.Frame(self, bg=SIDE)
        top.pack(fill="x")
        self.lights = tk.Canvas(top, height=20, bg=SIDE, highlightthickness=0)
        self.lights.pack(fill="x")
        self.lights.bind("<Configure>", lambda e: self.draw_lights())

        bar = tk.Frame(top, bg=SIDE)
        bar.pack(fill="x")
        tk.Label(bar, text="jrz", bg=SIDE, fg=ACCENT,
                 font=(FONT, 20, "bold italic")).pack(side="left", padx=(18, 24))
        self.tab_btns = {}
        for t in TABS:
            f = tk.Frame(bar, bg=SIDE, cursor="hand2")
            f.pack(side="left", padx=2)
            lab = tk.Label(f, text=t, bg=SIDE, fg=MUTED, font=(FONT, 10), padx=12,
                           pady=8)
            lab.pack()
            ul = tk.Frame(f, bg=SIDE, height=2)
            ul.pack(fill="x")
            for w in (f, lab):
                w.bind("<Button-1>", lambda e, t=t: self.show_tab(t))
            self.tab_btns[t] = (lab, ul)

        right = tk.Frame(bar, bg=SIDE)
        right.pack(side="right", padx=16)
        self.b_std = tk.Button(right, text="Standard", relief="flat", bd=0,
                               font=(FONT, 9), padx=12, pady=4, cursor="hand2",
                               command=lambda: self.set_theme(False))
        self.b_xmas = tk.Button(right, text="Christmas", relief="flat", bd=0,
                                font=(FONT, 9), padx=12, pady=4, cursor="hand2",
                                command=lambda: self.set_theme(True))
        self.b_std.pack(side="left", padx=2)
        self.b_xmas.pack(side="left", padx=2)
        tk.Button(right, text="Open Output Folder", bg=SIDE, fg=FG, bd=0,
                  font=(FONT, 9), padx=12, pady=4, cursor="hand2",
                  highlightthickness=1, highlightbackground=BORDER,
                  activebackground=PANEL, activeforeground=FG,
                  command=self.open_folder).pack(side="left", padx=(8, 0))
        tk.Frame(self, bg=BORDER, height=1).pack(fill="x")
        self.set_theme(False)

    def set_theme(self, xmas):
        self.xmas = xmas
        for b, on in ((self.b_std, not xmas), (self.b_xmas, xmas)):
            b.config(bg=ACCENT if on else SIDE, fg="white" if on else MUTED,
                     activebackground=ACCENT_H, activeforeground="white")
        self.draw_lights()

    def draw_lights(self):
        c = self.lights
        c.delete("all")
        self.bulbs = []
        if not self.xmas:
            return
        w = c.winfo_width()
        cols = ["#ff3b3b", "#35d36b", "#ffd23b", "#3b8bff"]
        step, x, i = 32, 0, 0
        while x < w:
            x2 = x + step
            pts = [x, 4, (x + x2) / 2, 12, x2, 4]
            c.create_line(*pts, smooth=True, fill="#1f2a24", width=2)
            bx = (x + x2) / 2
            col = cols[i % 4]
            b = c.create_oval(bx - 3, 12, bx + 3, 20, fill=col, outline="")
            self.bulbs.append((b, col))
            x, i = x2, i + 1

    def twinkle(self):
        for b, col in self.bulbs:
            dim = random.random() < 0.25
            self.lights.itemconfig(b, fill="#2a302d" if dim else col)
        self.after(700, self.twinkle)

    # ----- body -----
    def build_body(self):
        body = tk.Frame(self, bg=BG)
        body.pack(fill="both", expand=True)
        body.columnconfigure(1, weight=1)
        body.rowconfigure(0, weight=1)

        self.side = tk.Frame(body, bg=SIDE, width=220)
        self.side.grid(row=0, column=0, sticky="ns")
        self.side.grid_propagate(False)
        tk.Frame(body, bg=BORDER, width=1).grid(row=0, column=0, sticky="nse")

        mid = tk.Frame(body, bg=BG)
        mid.grid(row=0, column=1, sticky="nsew", padx=22, pady=14)
        self.crumb = tk.Frame(mid, bg=BG)
        self.crumb.pack(fill="x")
        self.c_tab = tk.Label(self.crumb, bg=BG, fg=ACCENT, font=(FONT, 7, "bold"))
        self.c_tab.pack(side="left")
        tk.Label(self.crumb, text=" /  MODE", bg=BG, fg=MUTED,
                 font=(FONT, 7, "bold")).pack(side="left")
        self.title_l = tk.Label(mid, bg=BG, fg=FG, font=(FONT, 16, "bold"),
                                anchor="w")
        self.title_l.pack(fill="x", pady=(4, 0))
        self.desc_l = tk.Label(mid, bg=BG, fg=MUTED, font=(FONT, 9), anchor="w")
        self.desc_l.pack(fill="x", pady=(2, 12))

        self.drop = tk.Canvas(mid, height=190, bg=BG, highlightthickness=0)
        self.drop.pack(fill="x")
        self.gen_btn = tk.Button(self.drop, text="Generate", bg=ACCENT, fg="white",
                                 bd=0, font=(FONT, 10, "bold"), padx=26, pady=6,
                                 cursor="hand2", activebackground=ACCENT_H,
                                 activeforeground="white", command=self.generate)
        self.drop.bind("<Configure>", lambda e: self.draw_drop())

        tk.Label(mid, text="ACTIVITY", bg=BG, fg=MUTED, font=(FONT, 7, "bold"),
                 anchor="w").pack(fill="x", pady=(16, 4))
        box = tk.Frame(mid, bg=PANEL, highlightthickness=1, highlightbackground=BORDER)
        box.pack(fill="both", expand=True)
        self.logbox = tk.Text(box, bg=PANEL, fg="#d8d8d8", bd=0, wrap="word",
                              font=("Consolas", 9), padx=12, pady=10,
                              state="disabled", insertbackground=FG)
        self.logbox.pack(fill="both", expand=True)

        rt = tk.Frame(body, bg=SIDE, width=310)
        rt.grid(row=0, column=2, sticky="ns")
        rt.grid_propagate(False)
        tk.Frame(body, bg=BORDER, width=1).grid(row=0, column=2, sticky="nsw")
        self.set_title = tk.Label(rt, bg=SIDE, fg=FG, font=(FONT, 13, "bold"),
                                  anchor="w")
        self.set_title.pack(fill="x", padx=18, pady=(16, 0))
        tk.Label(rt, text="Applied to the pack when you generate", bg=SIDE, fg=MUTED,
                 font=(FONT, 8), anchor="w").pack(fill="x", padx=18, pady=(0, 10))
        self.set_box = tk.Frame(rt, bg=SIDE)
        self.set_box.pack(fill="x", padx=18)

        after = card(rt, "AFTER GENERATING")
        after.pack(fill="x", padx=18, pady=10)
        for var, text in ((self.lock, "Lock against server changes"),
                          (self.open_when, "Open the saved folder when done")):
            r = tk.Frame(after, bg=PANEL)
            r.pack(fill="x", padx=12, pady=5)
            Toggle(r, var).pack(side="left")
            tk.Label(r, text=text, bg=PANEL, fg=FG, font=(FONT, 9)).pack(
                side="left", padx=10)
        tk.Frame(after, bg=PANEL, height=6).pack()

        how = card(rt, "HOW TO INSTALL")
        how.pack(fill="x", padx=18)
        steps = ("1   Copy 'jrz_accessory' into your FiveM resources folder",
                 "2   Add  ensure jrz_accessory  to your server.cfg",
                 "3   Stack effects: choose a mode on several tabs, then Generate")
        for s in steps:
            tk.Label(how, text=s, bg=PANEL, fg=MUTED, font=(FONT, 8), anchor="w",
                     justify="left", wraplength=250).pack(fill="x", padx=12, pady=2)
        tk.Frame(how, bg=PANEL, height=6).pack()

    def draw_drop(self):
        c = self.drop
        c.delete("all")
        w, h = c.winfo_width(), c.winfo_height()
        c.create_rectangle(2, 2, w - 2, h - 2, outline="#2e3432", dash=(5, 4))
        c.create_oval(w / 2 - 20, 28, w / 2 + 20, 68, fill="#1a0b10", outline="")
        c.create_text(w / 2, 48, text="\u2193", fill=ACCENT, font=(FONT, 18, "bold"))
        self.drop_t = c.create_text(w / 2, 90, fill=FG, font=(FONT, 11, "bold"),
                                    text=self.drop_text())
        c.create_text(w / 2, 112, fill=MUTED, font=(FONT, 8),
                      text="Files are saved to the Output folder - nothing in your game is touched.")
        c.create_window(w / 2, 150, window=self.gen_btn)

    def drop_text(self):
        n = len(self.active())
        return ("Pick a mode to get started" if n == 0
                else f"{n} effect{'s' if n != 1 else ''} ready to generate")

    # ----- status -----
    def build_status(self):
        tk.Frame(self, bg=BORDER, height=1).pack(fill="x")
        s = tk.Frame(self, bg=SIDE)
        s.pack(fill="x")
        tk.Label(s, text="\u25cf", bg=SIDE, fg="#2ecc71", font=(FONT, 8)).pack(
            side="left", padx=(12, 4), pady=5)
        self.status = tk.Label(s, text="Ready", bg=SIDE, fg=FG, font=(FONT, 8))
        self.status.pack(side="left")
        tk.Label(s, text=f"Saves to: {OUT}", bg=SIDE, fg=MUTED,
                 font=(FONT, 8)).pack(side="right", padx=12)

    # ----- tab / mode handling -----
    def show_tab(self, tab):
        self.tab = tab
        for t, (lab, ul) in self.tab_btns.items():
            on = t == tab
            lab.config(fg=FG if on else MUTED)
            ul.config(bg=ACCENT if on else SIDE)
        self.build_side()
        self.build_settings()
        self.refresh_header()

    def build_side(self):
        for w in self.side.winfo_children():
            w.destroy()
        tk.Label(self.side, text=f"{self.tab.upper()} MODES", bg=SIDE, fg=MUTED,
                 font=(FONT, 7, "bold"), anchor="w").pack(fill="x", padx=14,
                                                          pady=(16, 8))
        for i, (label, _v, _d) in enumerate(TABS[self.tab]):
            on = i == self.sel[self.tab]
            row = tk.Frame(self.side, bg=ACCENT_D if on else SIDE, cursor="hand2")
            row.pack(fill="x")
            tk.Frame(row, bg=ACCENT if on else SIDE, width=3).pack(side="left",
                                                                  fill="y")
            lab = tk.Label(row, text=label, bg=ACCENT_D if on else SIDE,
                           fg=FG if on else "#b9bfbc", font=(FONT, 9), anchor="w",
                           padx=12, pady=9)
            lab.pack(fill="x")
            for w in (row, lab):
                w.bind("<Button-1>", lambda e, i=i: self.pick_mode(i))
        tk.Frame(self.side, bg=SIDE, height=14).pack()
        for key, label, lo, hi, _d, step, fmt in SLIDERS[self.tab]:
            Slider(self.side, label, self.v[self.tab][key], lo, hi, step, fmt).pack(
                fill="x", padx=14, pady=(8, 0))

    def build_settings(self):
        self.set_title.config(text=f"{self.tab} settings")
        for w in self.set_box.winfo_children():
            w.destroy()
        c = card(self.set_box, self.tab.upper())
        c.pack(fill="x")
        for kind, key, label, _d in SETTINGS[self.tab]:
            r = tk.Frame(c, bg=PANEL)
            r.pack(fill="x", padx=12, pady=6)
            if kind == "toggle":
                Toggle(r, self.v[self.tab][key]).pack(side="left")
                tk.Label(r, text=label, bg=PANEL, fg=FG, font=(FONT, 9)).pack(
                    side="left", padx=10)
            else:
                ColorField(r, label, self.v[self.tab][key]).pack(fill="x")
        tk.Frame(c, bg=PANEL, height=6).pack()

    def pick_mode(self, i):
        self.sel[self.tab] = i
        if TABS[self.tab][i][1] is not None and self.tab in WEATHER_TABS:
            self.recent.append(self.tab)
        self.build_side()
        self.refresh_header()

    def refresh_header(self):
        label, _v, desc = TABS[self.tab][self.sel[self.tab]]
        self.c_tab.config(text=self.tab.upper())
        self.title_l.config(text=label)
        self.desc_l.config(text=desc)
        if hasattr(self, "drop_t"):
            self.drop.itemconfig(self.drop_t, text=self.drop_text())

    def active(self):
        return {t: TABS[t][i][1] for t, i in self.sel.items()
                if TABS[t][i][1] is not None}

    # ----- log / folders -----
    def log(self, msg):
        self.logbox.config(state="normal")
        self.logbox.insert("end", msg + "\n")
        self.logbox.see("end")
        self.logbox.config(state="disabled")

    def open_folder(self, path=None):
        p = Path(path) if path else OUT
        p.mkdir(parents=True, exist_ok=True)
        try:
            if os.name == "nt":
                os.startfile(p)
            elif sys.platform == "darwin":
                subprocess.Popen(["open", str(p)])
            else:
                subprocess.Popen(["xdg-open", str(p)])
        except Exception as e:
            self.log(f"Could not open folder: {e}")

    # ----- generation -----
    def ped_rgb(self, mode):
        if mode == "white":
            return 1.0, 1.0, 1.0
        if mode == "black":
            return 0.0, 0.0, 0.0
        h = self.v["Ped Light"]["colour"].get().lstrip("#")
        if len(h) != 6:
            raise ValueError("Custom colour must be a hex value like #FFFFFF")
        return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))

    def generate(self):
        act = self.active()
        if not act:
            self.log("Nothing to generate - pick a mode on at least one tab.")
            self.status.config(text="Nothing selected")
            return
        try:
            res = OUT / "jrz_accessory"
            res.mkdir(parents=True, exist_ok=True)
            g = lambda t, k: self.v[t][k].get()

            # which tab decides the weather type (last one chosen wins)
            owner = next((t for t in reversed(self.recent)
                          if t in act and act[t] != "FLASH"), None)
            weather = act[owner] if owner else None
            wind_tab = owner if owner in ("Snow", "Rain") else (
                "Snow" if "Snow" in act else "Rain" if "Rain" in act else None)

            lua_bool = lambda b: "true" if b else "false"
            flash = "Lightning" in act or (
                "Rain" in act and g("Rain", "storm"))
            interval = g("Lightning", "interval") if "Lightning" in act else 15
            jitter = g("Lightning", "jitter") if "Lightning" in act else True
            time_on = "Time Lock" in act

            cfg = {
                "weather": f"'{weather}'" if weather else "nil",
                "rain": f"{g('Rain', 'rain'):.2f}" if "Rain" in act else "nil",
                "wind": f"{g(wind_tab, 'wind'):.1f}" if wind_tab else "nil",
                "windDir": f"{math.radians(g(wind_tab, 'dir')):.3f}" if wind_tab else "nil",
                "ground": lua_bool(g("Snow", "ground")) if "Snow" in act else "nil",
                "trails": lua_bool(g("Snow", "trails")) if "Snow" in act else "nil",
                "flash": lua_bool(flash),
                "interval": f"{interval:.0f}",
                "jitter": lua_bool(jitter),
                "hour": f"{g('Time Lock', 'hour'):.0f}" if time_on else "nil",
                "minute": f"{g('Time Lock', 'minute'):.0f}" if time_on else "nil",
                "freeze": lua_bool(g("Time Lock", "freeze")) if time_on else "false",
                "lock": lua_bool(self.lock.get()),
            }
            body = ",\n".join(f"    {k} = {v}" for k, v in cfg.items())

            (res / "client.lua").write_text(f"""-- generated by {APP}
local CFG = {{
{body}
}}

local function applyWeather()
    if CFG.weather then
        SetWeatherTypePersist(CFG.weather)
        SetWeatherTypeNow(CFG.weather)
        SetWeatherTypeNowPersist(CFG.weather)
        SetOverrideWeather(CFG.weather)
    end
    if CFG.rain then SetRainLevel(CFG.rain) end
    if CFG.wind then SetWindSpeed(CFG.wind) end
    if CFG.windDir then SetWindDirection(CFG.windDir) end
    if CFG.ground ~= nil then ForceSnowPass(CFG.ground) end
    if CFG.trails ~= nil then
        SetForceVehicleTrails(CFG.trails)
        SetForcePedFootstepsTracks(CFG.trails)
    end
end

local function applyTime()
    if CFG.hour then NetworkOverrideClockTime(CFG.hour, CFG.minute, 0) end
end

CreateThread(function()
    local timeDone = false
    while true do
        applyWeather()
        if CFG.hour and (CFG.freeze or not timeDone) then
            applyTime()
            timeDone = true
        end
        Wait(CFG.lock and 1000 or 30000)
    end
end)

if CFG.flash then
    CreateThread(function()
        while true do
            local base = CFG.interval * 1000
            local wait = CFG.jitter and math.random(math.floor(base * 0.5), math.floor(base * 1.5)) or base
            Wait(wait)
            ForceLightningFlash()
        end
    end)
end
""", encoding="utf-8")
            files = ["client.lua"]
            manifest = ("fx_version 'cerulean'\ngame 'gta5'\nauthor 'jrz'\n"
                        f"description \"{APP} output\"\nclient_script 'client.lua'\n")

            if "Ped Light" in act:
                r, gg, b = self.ped_rgb(act["Ped Light"])
                (res / "visualsettings.dat").write_text(
                    f"# generated by {APP}\n"
                    f"pedLight.color.red {r:.3f}\n"
                    f"pedLight.color.green {gg:.3f}\n"
                    f"pedLight.color.blue {b:.3f}\n"
                    f"pedLight.intensity {g('Ped Light', 'intensity'):.2f}\n"
                    f"pedLight.specular {g('Ped Light', 'shine'):.2f}\n",
                    encoding="utf-8")
                manifest += ("file 'visualsettings.dat'\n"
                             "data_file 'VISUAL_SETTINGS' 'visualsettings.dat'\n")
                files.append("visualsettings.dat")
            (res / "fxmanifest.lua").write_text(manifest, encoding="utf-8")
            files.insert(0, "fxmanifest.lua")

            self.log("-" * 46)
            for t, v in act.items():
                self.log(f"  + {t}: {TABS[t][self.sel[t]][0]}")
            self.log(f"Wrote {', '.join(files)}")
            self.log(f"Saved to {res}")
            self.status.config(text="Generated")
            if self.open_when.get():
                self.open_folder(res)
        except Exception as e:
            self.log(f"Error: {e}")
            self.status.config(text="Error")


if __name__ == "__main__":
    App().mainloop()
