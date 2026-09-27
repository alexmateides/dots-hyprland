#!/usr/bin/env python3
from typing import List
from html import escape
import glob
import json
import os
import subprocess
import sys
import time

sys.path.append("/home/truepeak/.config/rofi")
import rofi_menu

# Keep in sync with ~/.config/hypr/hosts/truepad.lua
INTERNAL = {"output": "eDP-1", "mode": "1920x1200@60", "position": "0x0", "scale": 1.333333}
EXTERNAL_SCALE = 1
EXTEND_SCALE = 1.25

RUNTIME_DIR = os.environ.get("XDG_RUNTIME_DIR", "/tmp")
# Hyprland skips the auto popup for a few seconds after we apply a mode (see truepad.lua)
STAMP_PATH = f"{RUNTIME_DIR}/display-menu.stamp"
WATCHER_PID_PATH = f"{RUNTIME_DIR}/display-menu-watcher.pid"


def connected_externals() -> List[str]:
    """Connected non-internal outputs, read from DRM so disabled outputs are listed too"""
    names = []
    for status_path in sorted(glob.glob("/sys/class/drm/card*-*/status")):
        name = status_path.split("/")[-2].split("-", 1)[1]
        if name == INTERNAL["output"] or name.startswith(("eDP", "LVDS", "Writeback")):
            continue
        with open(status_path) as f:
            if f.read().strip() == "connected":
                names.append(name)
    return names


def monitor_rule(output: str, mode: str = "preferred", position: str = "auto", scale: float = EXTERNAL_SCALE,
                 disabled: bool = False, mirror: str = "") -> str:
    # disabled / mirror are always passed: hyprland keeps the previous value when a field is omitted
    return (f"hl.monitor({{ output = '{output}', mode = '{mode}', position = '{position}', scale = {scale}, "
            f"disabled = {str(disabled).lower()}, mirror = '{mirror}' }})")


def internal_rule(disabled: bool = False) -> str:
    return monitor_rule(INTERNAL["output"], INTERNAL["mode"], INTERNAL["position"], INTERNAL["scale"], disabled)


def get_monitors() -> dict:
    out, _ = rofi_menu.run_cmd(["hyprctl", "monitors", "all", "-j"])
    try:
        return {m["name"]: m for m in json.loads(out)}
    except json.JSONDecodeError:
        return {}


def mirror_mode(output: str) -> str:
    """
    Largest mode with the internal panel's aspect ratio (16:10), e.g. 1680x1050 / 1280x800.
    Mirroring onto a different aspect ratio letterboxes, and hyprland leaves the bars undamaged (flicker)
    """
    width, height = map(int, INTERNAL["mode"].split("@")[0].split("x"))
    best = None
    for mode in get_monitors().get(output, {}).get("availableModes", []):
        res, rate = mode.removesuffix("Hz").split("@")
        w, h = map(int, res.split("x"))
        if abs(w / h - width / height) > 0.01 or w > width:
            continue
        key = (w * h, float(rate))
        if best is None or key > best[0]:
            best = (key, f"{res}@{rate}")
    return best[1] if best else "preferred"


def current_mode(externals: List[str]) -> str | None:
    monitors = get_monitors()
    if not monitors:
        return None
    ext = [monitors[n] for n in externals if n in monitors]
    if not ext or all(m["disabled"] for m in ext):
        return "laptop"
    if monitors.get(INTERNAL["output"], {}).get("disabled"):
        return "external"
    if all(m.get("mirrorOf", "none") != "none" for m in ext):
        return "mirror"
    return "extend"


def stop_watcher():
    try:
        with open(WATCHER_PID_PATH) as f:
            os.kill(int(f.read()), 15)
    except (OSError, ValueError):
        pass
    try:
        os.remove(WATCHER_PID_PATH)
    except OSError:
        pass


def start_watcher(externals: List[str]):
    """A disabled output fires no hyprland events, so wait for the unplug here and reset its rule"""
    reset = "; ".join(monitor_rule(n, scale=INTERNAL["scale"]) for n in externals)
    checks = " || ".join(f'grep -qx connected /sys/class/drm/card*-{n}/status' for n in externals)
    script = f'while {checks}; do sleep 2; done; hyprctl eval "{reset}"; rm -f {WATCHER_PID_PATH}'
    p = subprocess.Popen(["sh", "-c", script], start_new_session=True,
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    with open(WATCHER_PID_PATH, "w") as f:
        f.write(str(p.pid))


class ModeItem(rofi_menu.Item):
    def __init__(self, mode: str, icon: str, label: str, externals: List[str], active: bool = False, **kwargs):
        super().__init__(**kwargs)
        self.mode = mode
        self.externals = externals
        self.active = active
        self.text = f"{icon}  {label}"

    def render_item(self):
        if not self.externals:
            # blocked: dimmed and not selectable
            return f"<span alpha='40%'>{escape(self.text)}</span>\0nonselectable\x1ftrue\x1finfo\x1f{self.item_id}"
        return f"{escape(self.text)}\0info\x1f{self.item_id}"

    def rules(self) -> List[str]:
        internal = INTERNAL["output"]
        match self.mode:
            case "mirror":
                return [internal_rule()] + [monitor_rule(n, mode=mirror_mode(n), mirror=internal) for n in self.externals]
            case "extend":
                return [internal_rule()] + [monitor_rule(n, position="auto-right", scale=EXTEND_SCALE) for n in self.externals]
            case "external":
                # enable the externals first so there is never zero active outputs
                return [monitor_rule(n, position="auto-right") for n in self.externals] + [internal_rule(disabled=True)]
            case "laptop":
                return [internal_rule()] + [monitor_rule(n, disabled=True) for n in self.externals]
        return []

    def on_select(self, **kwargs):
        if not self.externals:
            return rofi_menu.SelectOutcome.EXIT
        with open(STAMP_PATH, "w") as f:
            f.write(str(int(time.time())))
        stop_watcher()
        rofi_menu.run_cmd(["hyprctl", "eval", "; ".join(self.rules())])
        if self.mode == "laptop":
            start_watcher(self.externals)
        return rofi_menu.SelectOutcome.EXIT


if __name__ == "__main__":
    externals = connected_externals()
    active = current_mode(externals) if externals else None

    modes = [
        ("mirror",   "󰍺", "Mirror"),
        ("extend",   "󰍹", "Extend"),
        ("external", "󰐯", "External only"),
        ("laptop",   "󰌢", "Laptop only"),
    ]
    items: List[rofi_menu.Item] = [
        rofi_menu.ExitItem(),
    ]
    items.extend(ModeItem(mode, icon, label, externals, active=(mode == active)) for mode, icon, label in modes)

    if externals:
        message = f"󰍹  DISPLAYS · {', '.join(externals)}"
    else:
        message = "󰍹  DISPLAYS · no external display connected"
    main_menu = rofi_menu.Menu(items=items, message=message)

    # pango markup for the dimmed rows, highlight the current mode
    if os.environ.get("ROFI_RETV", "0") == "0":
        sys.stdout.write("\0markup-rows\x1ftrue\n")
        if active:
            sys.stdout.write(f"\0active\x1f{[m for m, _, _ in modes].index(active) + 1}\n")
    rofi_menu.run_menu(main_menu)
