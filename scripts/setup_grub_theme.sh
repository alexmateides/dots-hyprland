#!/bin/bash
# Installs the CyberGRUB-2077 grub theme from grub/ (same steps as the upstream install.fish, see grub/README.md)
# and trims the menu to the UKI entries of etc/grub.d/15_uki.
# Safe to re-run. Usage: sudo scripts/setup_grub_theme.sh
set -euo pipefail

[[ $EUID -eq 0 ]] || { echo "run with sudo"; exit 1; }

DOTS=$(dirname "$(readlink -f "$0")")/..
THEMES=/boot/grub/themes
CFG=/etc/default/grub

mkdir -p "$THEMES"
rm -rf "$THEMES/CyberGRUB-2077"
cp -r "$DOTS/grub/CyberGRUB-2077" "$THEMES/"

# set KEY=value in /etc/default/grub, uncommenting or appending it
set_opt() {
    if grep -qE "^#?$1=" "$CFG"; then
        sed -i -E "s|^#?$1=.*|$1=$2|" "$CFG"
    else
        echo "$1=$2" >> "$CFG"
    fi
}
set_opt GRUB_THEME "\"$THEMES/CyberGRUB-2077/theme.txt\""
set_opt GRUB_GFXMODE auto
set_opt GRUB_GFXPAYLOAD_LINUX keep
sed -i 's/^GRUB_TERMINAL_OUTPUT=/#GRUB_TERMINAL_OUTPUT=/' "$CFG"
# no "(EFI BootNext)" entries for every firmware boot option (grub 2.16's 31_efi_bootnext)
set_opt GRUB_DISABLE_BOOTNEXT true
# UKI machines: only 15_uki's entries (etc/pacman.d/hooks/grub-uki-only.hook redoes this after grub upgrades)
ls /boot/EFI/Linux/*.efi >/dev/null 2>&1 && chmod -x /etc/grub.d/10_linux /etc/grub.d/20_linux_xen

grub-mkconfig -o /boot/grub/grub.cfg
