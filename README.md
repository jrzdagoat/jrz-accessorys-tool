# jrz's Accessory's Tool

A small desktop app that generates client-side **FiveM** visual files:

- **Weather**: clear, rain, thunder, fog, snow, blizzard, light snow, Christmas, with rain intensity, wind speed, time of day and a weather lock.
- **Ped lighting**: white, black or custom colour, with intensity and shine sliders.

## Requirements
- Python 3.9+ (tkinter is included with the standard installer)

## Usage
```bash
python src/jrz_accessorys_tool.py
```
1. Choose your settings and press **Generate Files**.
2. Copy the generated `jrz_accessory` folder from `Documents/jrz Accessory's Tool/Output` into your FiveM `resources` folder.
3. Add `ensure jrz_accessory` to your `server.cfg` (or your client resources setup).

## Download the .exe
Every push builds the exe automatically with GitHub Actions:
1. Open the **Actions** tab, click the latest **Build EXE** run.
2. Download `jrz-Accessory-Tool` from **Artifacts** (unzip it to get the .exe).

For a permanent download, create a release tag (e.g. `v1.0`). The exe is then attached to the **Releases** page.

You can also build locally on Windows by running `build_exe.bat`.

## Output
```
jrz_accessory/
├── fxmanifest.lua
├── client.lua          # weather + time (FiveM natives)
└── visualsettings.dat  # ped light colour / intensity
```

## Notes
- The weather part uses standard FiveM natives.
- The `visualsettings.dat` key names for ped lighting may differ between game builds. If the effect doesn't show, adjust the keys for your build.
- Changes are client-side visuals only. Many servers prohibit lighting tweaks that make players easier to see, so check server rules before use.
- Not affiliated with any other tool or brand.

## License
MIT
