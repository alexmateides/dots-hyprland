#!/bin/bash
# One-time laptop setup for suspend-then-hibernate:
# btrfs swapfile in its own @swap subvolume, resume hook, resume= / resume_offset= in the UKI cmdline.
# Safe to re-run. Usage: sudo scripts/setup_hibernate.sh [swap size, default 32g]
set -euo pipefail

[[ $EUID -eq 0 ]] || { echo "run with sudo"; exit 1; }

SIZE=${1:-32g}
ROOT_UUID=$(findmnt -no UUID /)
ROOT_DEV=$(findmnt -no SOURCE / | sed 's/\[.*//')
DOTS=$(dirname "$(readlink -f "$0")")/..

# 1. @swap subvolume next to @, @home, ... (kept out of snapper snapshots of @)
if ! grep -q 'subvol=/@swap' /etc/fstab; then
    top=$(mktemp -d)
    mount -o subvolid=5 "$ROOT_DEV" "$top"
    [[ -d $top/@swap ]] || btrfs subvolume create "$top/@swap"
    umount "$top" && rmdir "$top"
    mkdir -p /swap
    cat >> /etc/fstab <<EOF

# /dev/mapper/ArchinstallVg-root (hibernation swapfile)
UUID=$ROOT_UUID	/swap     	btrfs     	rw,relatime,ssd,space_cache=v2,subvol=/@swap	0 0
/swap/swapfile	none      	swap      	defaults,pri=10	0 0
EOF
    systemctl daemon-reload
fi
mountpoint -q /swap || mount /swap

# 2. swapfile (nocow, uncompressed; zram stays preferred at pri=100)
[[ -f /swap/swapfile ]] || btrfs filesystem mkswapfile --size "$SIZE" --uuid clear /swap/swapfile
swapon --show=NAME --noheadings | grep -q '^/swap/swapfile$' || swapon /swap/swapfile

# 3. resume hook after encrypt/lvm2, before filesystems
grep -qE '^HOOKS=.*\bresume\b' /etc/mkinitcpio.conf || sed -i '/^HOOKS=/s/ filesystems/ resume filesystems/' /etc/mkinitcpio.conf

# 4. resume= / resume_offset= in the UKI cmdline
OFFSET=$(btrfs inspect-internal map-swapfile -r /swap/swapfile)
sed -i -E 's/ ?resume(_offset)?=[^ ]*//g; s/$/ resume=UUID='"$ROOT_UUID"' resume_offset='"$OFFSET"'/' /etc/kernel/cmdline

# 5. sleep delay + lid behaviour, then rebuild the UKI
cp -r "$DOTS/etc/systemd/sleep.conf.d" "$DOTS/etc/systemd/logind.conf.d" /etc/systemd/
systemctl kill -s HUP systemd-logind
mkinitcpio -P

echo
grep '^HOOKS=' /etc/mkinitcpio.conf
cat /etc/kernel/cmdline
swapon --show
echo "Reboot, then test with: systemctl hibernate"
