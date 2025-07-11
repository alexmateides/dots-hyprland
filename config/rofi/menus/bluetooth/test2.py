#!/usr/bin/env python3
import os
import sys
import time
import subprocess

states = [".", "..", "...", "finished"]

def output_menu(idx):
    # Print the single entry and data, then flush!!
    sys.stdout.write(states[idx] + "\n")
    sys.stdout.write(f"\0data\x1f{idx}\n")
    sys.stdout.flush()

def schedule_return(delay=1):
    # After `delay` seconds, find the visible Rofi window and send Return
    cmd = (
        "sleep {d} && "
        # search for the most recent visible window with class "Rofi"
        "win=$(xdotool search --onlyvisible --class Rofi | tail -n1) && "
        # send an Enter, clearing any modifiers
        "xdotool key --window \"$win\" --clearmodifiers Return"
    ).format(d=delay)
    subprocess.Popen(
        ["bash", "-c", cmd],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        preexec_fn=os.setpgrp
    )

def main():
    retv  = int(os.environ.get("ROFI_RETV",  "0"))
    data  = os.environ.get("ROFI_DATA",  "0")
    idx   = int(data)

    if retv == 0:
        # initial draw
        output_menu(0)
    elif retv == 1:
        # user pressed Enter (or our xdotool did)
        if idx < len(states) - 1:
            next_idx = idx + 1
            output_menu(next_idx)
            # schedule a fake Enter in 1s to loop
            schedule_return(1)
        else:
            # done
            sys.exit(0)

if __name__ == "__main__":
    main()
