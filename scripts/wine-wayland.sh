#!/bin/bash
# Make Wine use its native Wayland driver instead of XWayland.
# Wine's default is "x11,wayland", so X11 wins whenever DISPLAY is set (always, under Hyprland),
# and XWayland windows get blurry/wrongly sized on the fractionally scaled eDP-1.
# winewayland picks up the compositor scale itself, so no LogPixels tweak is needed.
#
# Usage: scripts/wine-wayland.sh [prefix ...]   (default: $WINEPREFIX or ~/.wine)
# Re-run for each new prefix; undo with: wine reg delete 'HKCU\Software\Wine\Drivers' /v Graphics /f

if ! command -v wine >/dev/null; then
    echo "wine-wayland: skipping (wine not installed)"
    exit 0
fi

prefixes=("$@")
[ ${#prefixes[@]} -eq 0 ] && prefixes=("${WINEPREFIX:-$HOME/.wine}")

for prefix in "${prefixes[@]}"; do
    WINEPREFIX="$prefix" wine reg add 'HKCU\Software\Wine\Drivers' /v Graphics /d wayland /f >/dev/null \
        && echo "wine-wayland: $prefix -> wayland"
done
