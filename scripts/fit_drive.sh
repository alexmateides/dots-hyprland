#!/bin/bash
# !!! DONT RUN WITH ROOT

# 1) Create the mountpoint and make sure YOU own /media/$USER
sudo mkdir -p /media/$USER/drive.in.fit.cvut.cz
sudo chown -R "$USER:$USER" /media/$USER

# 2) Mount and force files to be owned by your user
sudo mount.cifs //drive.in.fit.cvut.cz/home/mateial1 \
  /media/$USER/drive.in.fit.cvut.cz \
  -o "sec=ntlmv2i,uid=$(id -u $USER),gid=$(id -g $USER),file_mode=0600,dir_mode=0700,username=mateial1"
# You'll be prompted for the CVUT password for user 'mateial1'
