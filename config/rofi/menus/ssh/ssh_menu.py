#!/usr/bin/env python3
from typing import List
import tomllib
import os
import sys

sys.path.append("/home/truepeak/.config/rofi")
import rofi_menu

USER_HOME = f"/home/{os.getlogin()}"
SSH_CONFIG_PATH = f"{USER_HOME}/.ssh/rofi_menu.toml"


class SSHEntry(rofi_menu.Item):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        entry_config = kwargs.get("entry_config")
        self.identifier: str = entry_config["identifier"]
        self.username: str = entry_config["username"]
        self.hostname: str = entry_config["hostname"]
        self.port: int = entry_config["port"]
        self.sshkey: str = entry_config["ssh_key"]
        self.sshkey.replace("~", USER_HOME)

        self.text = f"󰢹  {self.identifier}"

    def on_select(self, **kwargs):
        ssh_command = f"TERM=xterm-256color ssh {self.username}@{self.hostname} -p {self.port} -i {self.sshkey}"
        rofi_menu.run_cmd(['kitty', '--title', self.identifier, '--hold', 'sh', '-c', ssh_command], background=True)
        return rofi_menu.SelectOutcome.EXIT


def parse_config() -> List[SSHEntry]:
    with open(SSH_CONFIG_PATH, "rb") as f:
        config = tomllib.load(f)
    entries = config.get("ssh")
    entries = [SSHEntry(entry_config=e) for e in entries]
    return entries


if __name__ == "__main__":
    items: List[rofi_menu.Item] = [
        rofi_menu.ExitItem(),
    ]
    items.extend(parse_config())
    main_menu = rofi_menu.Menu(items=items, message="󰌘  SSH MANAGER")
    rofi_menu.run_menu(main_menu)
