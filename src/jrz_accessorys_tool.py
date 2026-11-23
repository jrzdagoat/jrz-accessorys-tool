"""
jrz's Accessory's Tool
Generates client-side FiveM visual files:
  * Weather (clear / rain / snow / fog / thunder ...)
  * Ped lighting (white / black / custom)

Run:  python jrz_accessorys_tool.py      (needs Python 3.9+, tkinter is built in)
Output goes to  <Documents>/jrz Accessory's Tool/Output
"""
import os
import tkinter as tk
from tkinter import ttk, colorchooser, messagebox
from pathlib import Path

APP = "jrz's Accessory's Tool"
OUT = Path.home() / "Documents" / "jrz Accessory's Tool" / "Output"

BG, PANEL, FG, ACCENT = "#0b0b0f", "#15151c", "#f2f2f2", "#e63946"

WEATHER = {
    "Clear": "CLEAR", "Extra Sunny": "EXTRASUNNY", "Clouds": "CLOUDS",
    "Overcast": "OVERCAST", "Rain": "RAIN", "Thunder": "THUNDER",
    "Fog": "FOGGY", "Smog": "SMOG", "Snow": "SNOW", "Blizzard": "BLIZZARD",
    "Light Snow": "SNOWLIGHT", "Christmas": "XMAS",
}


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP)
        self.geometry("620x560")
        self.configure(bg=BG)
        self.resizable(False, False)
        self._style()

        tk.Label(self, text=APP, font=("Segoe UI", 18, "bold"),
                 bg=BG, fg=FG).pack(pady=(14, 0))
        tk.Label(self, text="Weather & ped lighting generator for FiveM",
                 bg=BG, fg="#888").pack(pady=(0, 10))

        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True, padx=14)
        self.weather_tab(nb)
        self.light_tab(nb)

        self.status = tk.StringVar(value="Ready")
        tk.Label(self, textvariable=self.status, bg=BG, fg="#6c6",
                 anchor="w").pack(fill="x", padx=14, pady=6)
        tk.Button(self, text="GENERATE FILES", bg=ACCENT, fg="white",
                  bd=0, font=("Segoe UI", 11, "bold"),
                  command=self.generate).pack(fill="x", padx=14, pady=(0, 14),
                                              ipady=8)

    # ---------- styling ----------
    def _style(self):
        s = ttk.Style(self)
        s.theme_use("clam")
        s.configure("TNotebook", background=BG, borderwidth=0)
        s.configure("TNotebook.Tab", background=PANEL, foreground=FG,
                    padding=(18, 8))
        s.map("TNotebook.Tab", background=[("selected", ACCENT)])
        s.configure("TFrame", background=PANEL)

    def _label(self, parent, text):
        return tk.Label(parent, text=text, bg=PANEL, fg=FG, anchor="w")

    def _slider(self, parent, text, var, lo, hi, res):
        self._label(parent, text).pack(fill="x", padx=14, pady=(10, 0))
        tk.Scale(parent, variable=var, from_=lo, to=hi, resolution=res,
                 orient="horizontal", bg=PANEL, fg=FG, troughcolor=BG,
                 highlightthickness=0, activebackground=ACCENT
                 ).pack(fill="x", padx=14)

    # ---------- weather ----------
    def weather_tab(self, nb):
        f = ttk.Frame(nb)
        nb.add(f, text="  Weather  ")
        self.w_type = tk.StringVar(value="Clear")
        self._label(f, "Weather type").pack(fill="x", padx=14, pady=(14, 0))
        ttk.Combobox(f, textvariable=self.w_type, values=list(WEATHER),
                     state="readonly").pack(fill="x", padx=14)
        self.w_rain = tk.DoubleVar(value=0.0)
        self.w_wind = tk.DoubleVar(value=0.0)
        self.w_freeze = tk.BooleanVar(value=True)
        self.w_hour = tk.IntVar(value=12)
        self._slider(f, "Rain intensity (0 - 1)", self.w_rain, 0, 1, 0.05)
        self._slider(f, "Wind speed (0 - 12)", self.w_wind, 0, 12, 0.5)
        self._slider(f, "Time of day (hour)", self.w_hour, 0, 23, 1)
        tk.Checkbutton(f, text="Lock weather & time (stop server changes)",
                       variable=self.w_freeze, bg=PANEL, fg=FG,
                       selectcolor=BG, activebackground=PANEL,
                       activeforeground=FG).pack(anchor="w", padx=14, pady=10)

    # ---------- ped light ----------
    def light_tab(self, nb):
        f = ttk.Frame(nb)
        nb.add(f, text="  Ped Light  ")
        self.p_mode = tk.StringVar(value="white")
        self.p_color = "#ffffff"
        self._label(f, "Ped light colour").pack(fill="x", padx=14, pady=(14, 4))
        for txt, val in (("White", "white"), ("Black", "black"),
                         ("Custom", "custom")):
            tk.Radiobutton(f, text=txt, value=val, variable=self.p_mode,
                           bg=PANEL, fg=FG, selectcolor=BG,
                           activebackground=PANEL, activeforeground=FG
                           ).pack(anchor="w", padx=24)
        tk.Button(f, text="Pick custom colour", command=self.pick,
                  bg=BG, fg=FG, bd=0).pack(anchor="w", padx=24, pady=6)
        self.p_int = tk.DoubleVar(value=4.0)
        self.p_spec = tk.DoubleVar(value=0.0)
        self._slider(f, "Light intensity", self.p_int, 0, 20, 0.5)
        self._slider(f, "Specular (shine)", self.p_spec, 0, 5, 0.1)

    def pick(self):
        c = colorchooser.askcolor(color=self.p_color)[1]
        if c:
            self.p_color = c
            self.p_mode.set("custom")

    # ---------- generation ----------
    def ped_rgb(self):
        m = self.p_mode.get()
        if m == "white":
            return 1.0, 1.0, 1.0
        if m == "black":
            return 0.0, 0.0, 0.0
        h = self.p_color.lstrip("#")
        return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))

    def generate(self):
        try:
            res = OUT / "jrz_accessory"
            res.mkdir(parents=True, exist_ok=True)
            r, g, b = self.ped_rgb()
            inten, spec = self.p_int.get(), self.p_spec.get()
            weather = WEATHER[self.w_type.get()]

            (res / "fxmanifest.lua").write_text(
                "fx_version 'cerulean'\ngame 'gta5'\n"
                "author 'jrz'\ndescription \"jrz's Accessory's Tool output\"\n"
                "client_script 'client.lua'\n"
                "file 'visualsettings.dat'\n"
                "data_file 'VISUAL_SETTINGS' 'visualsettings.dat'\n")

            # Weather + time (runs on the client)
            lock = "true" if self.w_freeze.get() else "false"
            (res / "client.lua").write_text(f"""-- generated by {APP}
local WEATHER = '{weather}'
local RAIN    = {self.w_rain.get():.2f}
local WIND    = {self.w_wind.get():.1f}
local HOUR    = {self.w_hour.get()}
local LOCK    = {lock}

local function apply()
    SetWeatherTypePersist(WEATHER)
    SetWeatherTypeNow(WEATHER)
    SetWeatherTypeNowPersist(WEATHER)
    SetOverrideWeather(WEATHER)
    SetRainLevel(RAIN)
    SetWindSpeed(WIND)
    if WEATHER == 'XMAS' or WEATHER == 'SNOW' or WEATHER == 'BLIZZARD'
       or WEATHER == 'SNOWLIGHT' then
        SetForceVehicleTrails(true)
        SetForcePedFootstepsTracks(true)
    else
        SetForceVehicleTrails(false)
        SetForcePedFootstepsTracks(false)
    end
    NetworkOverrideClockTime(HOUR, 0, 0)
end

CreateThread(function()
    while true do
        apply()
        Wait(LOCK and 1000 or 60000)
    end
end)
""")

            # Ped lighting (visualsettings.dat override)
            (res / "visualsettings.dat").write_text(
                f"# generated by {APP}\n"
                f"pedLight.color.red {r:.3f}\n"
                f"pedLight.color.green {g:.3f}\n"
                f"pedLight.color.blue {b:.3f}\n"
                f"pedLight.intensity {inten:.2f}\n"
                f"pedLight.specular {spec:.2f}\n")

            self.status.set(f"Done  ->  {res}")
            if messagebox.askyesno(APP, f"Files saved to:\n{res}\n\nOpen folder?"):
                os.startfile(res) if os.name == "nt" else None
        except Exception as e:  # noqa
            messagebox.showerror(APP, str(e))
            self.status.set("Error")


if __name__ == "__main__":
    App().mainloop()
