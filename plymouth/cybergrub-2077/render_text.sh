#!/bin/bash
# Re-renders the text images of the plymouth theme (plymouth has no fonts in the initramfs, so all static text is a png).
# Needs pango-view + the Rajdhani ttf (same font the CyberGRUB-2077 .pf2 files are built from); the pngs are committed.
# Sizes are for a 1080p screen, the script scales them. Usage: plymouth/cybergrub-2077/render_text.sh
set -euo pipefail
cd "$(dirname "$(readlink -f "$0")")"

tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
curl -sfLo "$tmp/Rajdhani-Regular.ttf" https://github.com/google/fonts/raw/main/ofl/rajdhani/Rajdhani-Regular.ttf
cat > "$tmp/fonts.conf" <<EOF
<?xml version="1.0"?><!DOCTYPE fontconfig SYSTEM "fonts.dtd">
<fontconfig><dir>$tmp</dir><include ignore_missing="yes">/etc/fonts/fonts.conf</include><cachedir>$tmp/cache</cachedir></fontconfig>
EOF
export FONTCONFIG_FILE=$tmp/fonts.conf

DIM='#842624' RED='#f75d54' CYAN='#74d6cf'
# name size color text
render() {
    pango-view -q --dpi=72 --margin=0 --antialias=gray --hinting=none --font="Rajdhani $2" \
        --foreground="$3" --background=transparent --output="$1.png" --text="$4"
}

render title     32 "$DIM"  "LINUX UNIFIED KEY SETUP // CRYPTLVM"
render display   24 "$RED"  "[DISPLAY 1]"
render select    16 "$DIM"  "[ OK ] SELECT OPERATING SYSTEM"
render initramfs 16 "$DIM"  "[ OK ] LOAD INITRAMFS"
render decrypt   16 "$RED"  "[ >> ] DECRYPT VOLUME"
render decrypted 16 "$DIM"  "[ OK ] DECRYPT VOLUME"
render load      16 "$RED"  "[ >> ] LOAD OPERATING SYSTEM"
render loaded    16 "$DIM"  "[ OK ] LOAD OPERATING SYSTEM"
render desktop   16 "$RED"  "[ >> ] START DESKTOP"
render shutdown  16 "$RED"  "[ >> ] SHUTTING DOWN"
render reboot    16 "$RED"  "[ >> ] REBOOTING"
render prompt    24 "$CYAN" "ENTER DECRYPTION KEY"
render denied    24 "$RED"  "ACCESS DENIED  //  RETRY"
render confirm   24 "$DIM"  "<-' - CONFIRM"
render log       24 "$DIM"  "ESC - BOOT LOG"

# password bullet: slanted cyan block
cat > "$tmp/bullet.svg" <<EOF
<svg xmlns="http://www.w3.org/2000/svg" width="14" height="24"><polygon points="5,0 14,0 9,24 0,24" fill="$CYAN"/></svg>
EOF
rsvg-convert "$tmp/bullet.svg" -o bullet.png
# 1px swatch, stretched into the progress bar frame
cat > "$tmp/px.svg" <<EOF
<svg xmlns="http://www.w3.org/2000/svg" width="1" height="1"><rect width="1" height="1" fill="$RED"/></svg>
EOF
rsvg-convert "$tmp/px.svg" -o px_red.png
