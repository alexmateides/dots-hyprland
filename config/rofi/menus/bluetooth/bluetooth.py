#!/usr/bin/env python3
import subprocess
import sys
import time

DIVIDER = "---------"
BACK     = "Back"
ROFI_OPTS = ["rofi", "-dmenu", "-i", "-p", "Bluetooth"]

def run_cmd(cmd, timeout=None):
    """Run a command, return (stdout, stderr)."""
    p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout or 10)
    return p.stdout.strip(), p.stderr.strip()

# --- Controller‐level helpers ---

def is_powered() -> bool:
    out, _ = run_cmd(["bluetoothctl", "show"])
    return "Powered: yes" in out

def toggle_power():
    if is_powered():
        run_cmd(["bluetoothctl", "power", "off"])
    else:
        # If soft‐blocked, unblock first
        out, _ = run_cmd(["rfkill", "list", "bluetooth"])
        if "blocked: yes" in out:
            run_cmd(["rfkill", "unblock", "bluetooth"])
            time.sleep(1)
        run_cmd(["bluetoothctl", "power", "on"])
    show_menu()

def is_scanning() -> bool:
    out, _ = run_cmd(["bluetoothctl", "show"])
    return "Discovering: yes" in out

def toggle_scan():
    if is_scanning():
        # Attempt to kill any lingering scan processes
        subprocess.run(["pkill", "-f", "bluetoothctl --timeout 5 scan on"])
        run_cmd(["bluetoothctl", "scan", "off"])
    else:
        run_cmd(["bluetoothctl", "--timeout", "5", "scan", "on"])
    show_menu()

def is_pairable():
    out, _ = run_cmd(["bluetoothctl", "show"])
    return "Pairable: yes" in out

def toggle_pairable():
    run_cmd(["bluetoothctl", "pairable", "off" if is_pairable() else "on"])
    show_menu()

def is_discoverable():
    out, _ = run_cmd(["bluetoothctl", "show"])
    return "Discoverable: yes" in out

def toggle_discoverable():
    run_cmd(["bluetoothctl", "discoverable", "off" if is_discoverable() else "on"])
    show_menu()

# --- Device‐level helpers ---

def info(mac):
    out, _ = run_cmd(["bluetoothctl", "info", mac])
    return out

def is_connected(mac):
    return "Connected: yes" in info(mac)

def is_paired(mac):
    return "Paired: yes" in info(mac)

def is_trusted(mac):
    return "Trusted: yes" in info(mac)

def toggle_connection(mac, name):
    run_cmd(["bluetoothctl", "disconnect" if is_connected(mac) else "connect", mac])
    device_menu(mac, name)

def toggle_paired(mac, name):
    run_cmd(["bluetoothctl", "remove" if is_paired(mac) else "pair", mac])
    device_menu(mac, name)

def toggle_trust(mac, name):
    run_cmd(["bluetoothctl", "untrust" if is_trusted(mac) else "trust", mac])
    device_menu(mac, name)

# --- UI helpers ---

def rofi(prompt, options):
    """
    Launch rofi -dmenu with given prompt and list of options.
    Returns the chosen line (or empty string).
    """
    menu = "\n".join(options)
    p = subprocess.run(ROFI_OPTS[:-1] + ["-p", prompt], input=menu,
                       text=True, capture_output=True)
    return p.stdout.strip()

def print_status():
    """Emulate --status mode for a status bar."""
    if not is_powered():
        print("")
        return

    sys.stdout.write("")
    # detect paired‐devices command name
    out, _ = run_cmd(["bluetoothctl", "version"])
    ver = float(out.split()[1])
    cmd = "paired-devices" if ver < 5.65 else "devices Paired"
    out, _ = run_cmd(["bluetoothctl"] + cmd.split())
    lines = [l for l in out.splitlines() if l.startswith("Device ")]
    first = True
    for l in lines:
        mac = l.split()[1]
        if is_connected(mac):
            alias = [m for m in info(mac).splitlines()
                     if m.startswith("Alias")][0].split(" ", 1)[1]
            if not first:
                sys.stdout.write(", " + alias)
            else:
                sys.stdout.write(" " + alias)
                first = False
    print()

def device_menu(mac, name):
    """
    Show the submenu for a single device (connect, pair, trust).
    """
    options = [
        f"Connected: {'yes' if is_connected(mac) else 'no'}",
        f"Paired: {'yes' if is_paired(mac) else 'no'}",
        f"Trusted: {'yes' if is_trusted(mac) else 'no'}",
        DIVIDER,
        BACK,
        "Exit"
    ]
    choice = rofi(name, options)
    if choice == options[0]:
        toggle_connection(mac, name)
    elif choice == options[1]:
        toggle_paired(mac, name)
    elif choice == options[2]:
        toggle_trust(mac, name)
    elif choice == BACK:
        show_menu()
    # Exit or divider just returns to shell

def show_menu():
    """
    Main menu: list devices + controller flags.
    """
    if is_powered():
        # list devices
        out, _ = run_cmd(["bluetoothctl", "devices"])
        # parse "Device XX:XX:XX:XX:XX Name" lines
        devs = [l.split(" ", 2)[2] for l in out.splitlines() if l.startswith("Device ")]
        options = devs + [
            DIVIDER,
            f"Power: on",
            f"Scan: {'on' if is_scanning() else 'off'}",
            f"Pairable: {'on' if is_pairable() else 'off'}",
            f"Discoverable: {'on' if is_discoverable() else 'off'}",
            "Exit"
        ]
        choice = rofi("Bluetooth", options)
        if choice == f"Power: on":
            toggle_power()
        elif choice == f"Scan: {'on' if is_scanning() else 'off'}":
            toggle_scan()
        elif choice == f"Pairable: {'on' if is_pairable() else 'off'}":
            toggle_pairable()
        elif choice == f"Discoverable: {'on' if is_discoverable() else 'off'}":
            toggle_discoverable()
        elif choice in devs:
            # look up mac
            out, _ = run_cmd(["bluetoothctl", "devices"])
            for l in out.splitlines():
                if choice in l:
                    mac = l.split()[1]
                    device_menu(mac, choice)
                    break
        # DIVIDER or Exit -> do nothing
    else:
        choice = rofi("Bluetooth", ["Power: off", "Exit"])
        if choice == "Power: off":
            toggle_power()

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--status":
        print_status()
    else:
        show_menu()
