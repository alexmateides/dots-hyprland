#!/usr/bin/env python3
import sys
import subprocess
import re
from typing import Dict, Any, List, Tuple

sys.path.append("/home/truepeak/PycharmProjects")
import rofi_menu

OFFSET = 18

BATTERY_MAP = {
    None: "",
    0: "󰥇 (0%)",
    10: "󰤾 (10%)",
    20: "󰤿 (20%)",
    30: "󰥀 (30%)",
    40: "󰥁 (40%)",
    50: "󰥂 (50%)",
    60: "󰥃 (60%)",
    70: "󰥄 (70%)",
    80: "󰥅 (80%)",
    90: "󰥆 (90%)",
    100: "󰥈 (100%)"
}


def get_bluetoothctl_status() -> Dict[str, Any]:
    status_string, _ = rofi_menu.run_cmd("bluetoothctl show")
    result = {}
    result['powered'] = True if re.search(r'Powered: (.*)$', status_string, re.MULTILINE).group(1) == "yes" else False
    result['discoverable'] = True if re.search(r'Discoverable: (.*)$', status_string, re.MULTILINE).group(
        1) == "yes" else False
    result['pairable'] = True if re.search(r'Pairable: (.*)$', status_string, re.MULTILINE).group(1) == "yes" else False
    result['scanning'] = True if re.search(r'Discovering: (.*)$', status_string, re.MULTILINE).group(
        1) == "yes" else False

    return result


class BluetoothToggleItem(rofi_menu.Item):
    def __init__(self, status: bool, **kwargs):
        super().__init__(**kwargs)
        self.status = status
        self.set_text()

    def on_select(self, **kwargs):
        action = "off" if self.status else "on"
        out, _ = rofi_menu.run_cmd(f"bluetoothctl power {action}")
        self.status = get_bluetoothctl_status()['powered']
        self.set_text()
        self._main_menu.reload()
        return rofi_menu.SelectOutcome.REFRESH

    def set_text(self):
        if self.status:
            self.text = f"{'󰂯  Bluetooth':<{OFFSET}}[ON]"
        else:
            self.text = f"{'󰂲  Bluetooth':<{OFFSET}}[OFF]"


class DiscoverableToggleItem(rofi_menu.Item):
    def __init__(self, status: bool, **kwargs):
        super().__init__(**kwargs)
        self.status = status
        self.set_text()

    def on_select(self, **kwargs):
        action = "off" if self.status else "on"
        out, _ = rofi_menu.run_cmd(f"bluetoothctl discoverable {action}")
        self.status = get_bluetoothctl_status()['discoverable']
        self.set_text()
        return rofi_menu.SelectOutcome.REFRESH

    def set_text(self):
        if self.status:
            self.text = f"{'󱜠  Discoverable':<{OFFSET}}[ON]"
        else:
            self.text = f"{'󱜡  Discoverable':<{OFFSET}}[OFF]"


class PairableToggleItem(rofi_menu.Item):
    def __init__(self, status: bool, **kwargs):
        super().__init__(**kwargs)
        self.status = status
        self.set_text()

    def on_select(self, **kwargs):
        action = "off" if self.status else "on"
        out, _ = rofi_menu.run_cmd(f"bluetoothctl pairable {action}")
        self.status = get_bluetoothctl_status()['pairable']
        self.set_text()
        return rofi_menu.SelectOutcome.REFRESH

    def set_text(self):
        if self.status:
            self.text = f"{'󰌹  Pairable':<{OFFSET}}[ON]"
        else:
            self.text = f"{'󰌺  Pairable':<{OFFSET}}[OFF]"


class DeviceConnectToggleItem(rofi_menu.SubMenuItem):
    def __init__(self, status: bool, **kwargs):
        kwargs['wait_menu'] = True
        super().__init__(**kwargs)
        self.status = status
        self.mac = kwargs.get("mac")
        self.wait = 0
        self.set_text()
        self._items = [rofi_menu.WaitItem(text="Connecting: ")]

    def on_select(self, **kwargs):
        super().on_select(**kwargs)
        if self._items[0].cooldown == 0:
            pid, _ = rofi_menu.run_cmd(['sh', '-c', 'sleep 0.5 && wtype -k Return'], background=True)

    def set_text(self):
        if self.status:
            self.text = f"{'Disconnect':<{OFFSET}}"
        else:
            self.text = f"{'Connect':<{OFFSET}}"


class DeviceMenuItem(rofi_menu.SubMenuItem):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = kwargs.get("name")
        self.mac = kwargs.get("mac")
        self.device_info = self.get_device_info()
        battery = self.device_info["battery"]
        if battery:
            battery = int(battery) - int(battery) % 10
        icon = '󰋋' if self.device_info["connected"] else "󰟎"
        self.text = f"{icon + '  ' + self.name:<{OFFSET}}{BATTERY_MAP[battery]}"
        self._items = [
            rofi_menu.ReturnItem(),
            DeviceConnectToggleItem(status=self.device_info["connected"], mac=self.mac)
        ]

    def get_device_info(self) -> Dict[str, Any]:
        info_string, _ = rofi_menu.run_cmd(f"bluetoothctl info {self.mac}")

        result = {
            'connected': True if re.search(r'Connected: (.*)$', info_string, re.MULTILINE).group(1) == 'yes' else False,
            'paired': True if re.search(r'Connected: (.*)$', info_string, re.MULTILINE).group(1) == 'yes' else False,
            'trusted': True if re.search(r'Connected: (.*)$', info_string, re.MULTILINE).group(1) == 'yes' else False,
        }
        result['battery'] = re.search(r'Battery Percentage:.*\((.*)\)$', info_string, re.MULTILINE).group(1) if result[
            'connected'] else None

        return result


class DevicesMenuItem(rofi_menu.SubMenuItem):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._items: List[rofi_menu.Item] = [
            rofi_menu.ReturnItem(),
        ]
        self._items.extend([
            DeviceMenuItem(mac=mac, name=name)
            for mac, name in self.get_devices()
        ])
        num_devices = f"[{len(self._items) - 1}]"
        self.text = f"{self.text:<{OFFSET}}{num_devices}"

        self._items.extend(
            [rofi_menu.Item(text=("󰐷 Scan"))]
        )

    @staticmethod
    def get_devices() -> List[Tuple]:
        """
        Returns [(mac, name) ...]
        """
        info_string, _ = rofi_menu.run_cmd("bluetoothctl devices Paired")
        devices = [tuple(l.split(" ", maxsplit=2)[1:]) for l in info_string.splitlines() if l.startswith("Device")]

        return devices


class BluetoothMenu(rofi_menu.Menu):
    def __init__(self, **kwargs):
        self.status = get_bluetoothctl_status()
        
        super().__init__(**kwargs)
        
        if self.status['powered']:
            self._items = [
                rofi_menu.ExitItem(),
                BluetoothToggleItem(self.status['powered']),
                DevicesMenuItem(text="󰋋  Devices"),
                DiscoverableToggleItem(status=self.status['discoverable']),
                PairableToggleItem(status=self.status['pairable']),
                rofi_menu.WaitItem(text="Lol")
            ]
        else:
            self._items = [
                rofi_menu.ExitItem(),
                BluetoothToggleItem(self.status['powered']),
            ]


menu = BluetoothMenu()

rofi_menu.run_menu(menu)
