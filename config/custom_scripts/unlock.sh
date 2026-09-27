#!/bin/bash
# Applies when logging in
[[ $(</etc/hostname) == truepeak-pc ]] || exit 0
openrgb -c FF00FF