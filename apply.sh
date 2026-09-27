#!/bin/bash
cp -r config/. ~/.config
cp -r local/. ~/.local
sudo cp -r etc/. /etc
sudo systemctl daemon-reload
systemctl --user enable --now ssh-agent.socket
# OpenRGB startup / shutdown / sleep hooks (desktop only)
if [[ $(</etc/hostname) == truepeak-pc ]]; then
    sudo systemctl enable truepeak_shutdown --now
    sudo systemctl enable truepeak_startup
    sudo cp config/scripts/openrgb_sleep.sh /usr/lib/systemd/system-sleep/openrgb.sh
else
    sudo systemctl disable --now truepeak_shutdown truepeak_startup 2>/dev/null
    sudo rm -f /usr/lib/systemd/system-sleep/openrgb.sh
fi
./scripts/electron-wayland.sh
# Use greetd as the display manager (--force replaces the existing display-manager.service link, e.g. plasmalogin)
sudo systemctl disable plasmalogin 2>/dev/null
sudo systemctl enable --force greetd
# Dolphin as default file manager (archlinux-xdg-menu + XDG_MENU_PREFIX=arch- lets KDE apps see the mime database outside Plasma)
xdg-mime default org.kde.dolphin.desktop inode/directory
# nano as default text editor (nano.desktop ships in local/share/applications)
xdg-mime default nano.desktop text/plain text/x-log text/markdown text/x-shellscript application/x-shellscript application/json application/xml application/toml application/x-yaml
command -v kbuildsycoca6 >/dev/null && XDG_MENU_PREFIX=arch- kbuildsycoca6 --noincremental >/dev/null 2>&1
