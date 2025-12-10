#!/bin/bash
cp -r config/. ~/.config
sudo cp -r etc/. /etc
sudo systemctl daemon-reload
sudo systemctl enable truepeak_shutdown --now
sudo systemctl enable truepeak_startup
sudo cp config/scripts/openrgb_sleep.sh /usr/lib/systemd/system-sleep/openrgb.sh