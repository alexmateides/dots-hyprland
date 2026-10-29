#!/bin/bash
# One-time setup of the plymouth boot splash / LUKS password prompt in the CyberGRUB-2077 look:
# theme from plymouth/cybergrub-2077 + the images of the grub theme in grub/, plymouth hook before encrypt, quiet splash.
# Safe to re-run. Usage: sudo scripts/setup_plymouth.sh
set -euo pipefail

[[ $EUID -eq 0 ]] || { echo "run with sudo"; exit 1; }

DOTS=$(dirname "$(readlink -f "$0")")/..
GRUB_THEME=$DOTS/grub/CyberGRUB-2077
THEME=/usr/share/plymouth/themes/cybergrub-2077

pacman -S --needed --noconfirm plymouth

# 1. theme: script + pre-rendered text, artwork from the grub theme. Fresh dir with 644 files (an earlier copy from
# the vfat /boot came out 0700), grub pngs reduced to IHDR/PLTE/tRNS/IDAT/IEND: their eXIf/iCCP/gAMA metadata is what
# plymouth's png loader may reject, and the pngs that failed to show were exactly those
rm -rf "$THEME"
install -d "$THEME"
install -m644 "$DOTS"/plymouth/cybergrub-2077/*.{plymouth,script,png} "$THEME/"
for png in "$GRUB_THEME"/{background,logo,label,progress_c}.png "$GRUB_THEME/item/highlight_c.png"; do
    python3 - "$png" "$THEME/${png##*/}" <<'EOF'
import struct, sys
src, dst = sys.argv[1:]
data = open(src, 'rb').read()
out, i = [data[:8]], 8
while i < len(data):
    length, kind = struct.unpack('>I4s', data[i:i + 8])
    if kind in (b'IHDR', b'PLTE', b'tRNS', b'IDAT', b'IEND'):
        out.append(data[i:i + 12 + length])
    i += 12 + length
open(dst, 'wb').write(b''.join(out))
EOF
    chmod 644 "$THEME/${png##*/}"
done

# 2. plymouth hook after kms, before encrypt so it draws the password prompt
grep -qE '^HOOKS=.*\bplymouth\b' /etc/mkinitcpio.conf || sed -i '/^HOOKS=/s/ encrypt/ plymouth encrypt/' /etc/mkinitcpio.conf

# 3. quiet splash on the kernel cmdline (UKI cmdline, and grub's in case it boots the plain kernel)
if [[ -f /etc/kernel/cmdline ]]; then
    for opt in quiet splash; do
        grep -qw "$opt" /etc/kernel/cmdline || sed -i "s/\$/ $opt/" /etc/kernel/cmdline
    done
fi
if [[ -f /etc/default/grub ]]; then
    for opt in quiet splash; do
        grep -qE "^GRUB_CMDLINE_LINUX_DEFAULT=.*\b$opt\b" /etc/default/grub ||
            sed -i -E "s/^(GRUB_CMDLINE_LINUX_DEFAULT=\"[^\"]*)\"/\1 $opt\"/" /etc/default/grub
    done
    grub-mkconfig -o /boot/grub/grub.cfg
fi

# 4. no Arch logo splash baked into the UKI (systemd-stub shows it before plymouth starts)
sed -i -E 's/^([a-z_]*options=".*)--splash [^ "]*/\1/; s/^([a-z_]*options=)" *"$/#\1""/' /etc/mkinitcpio.d/*.preset

# 5. select the theme and rebuild the initramfs / UKI
plymouth-set-default-theme cybergrub-2077
mkinitcpio -P

echo
grep '^HOOKS=' /etc/mkinitcpio.conf
[[ -f /etc/kernel/cmdline ]] && cat /etc/kernel/cmdline
grep '^GRUB_CMDLINE_LINUX_DEFAULT=' /etc/default/grub 2>/dev/null
echo "Preview without rebooting (from a TTY): sudo plymouthd; sudo plymouth show-splash; sudo plymouth ask-for-password; sudo plymouth quit"
