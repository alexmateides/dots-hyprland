#!/bin/sh

# store to: /usr/lib/systemd/system-sleep/openrgb.sh
case "$1" in
  pre)
    /usr/bin/openrgb -c 000000
    ;;
  post)
    /usr/bin/openrgb -c FF00FF
    ;;
esac
