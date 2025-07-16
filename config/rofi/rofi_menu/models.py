import json
import time
import sys, os

from .definitions import *
from .rofi import *
from typing import List, Dict, Any


class Item:
    """Represents single row in menu"""

    def __init__(self, text: str = "<undefined>", **kwargs):
        self.text = text
        self.id = None

    def render(self):
        return self.text

    def select_outcome(self):
        return SelectOutcome.REFRESH

    def select_action(self):
        self.text = "B" if self.text == "A" else "A"

    def on_select(self, **kwargs):
        self.select_action()
        return self.select_outcome()

    def save(self) -> Dict[str, Any]:
        return {
            "text": self.text,
        }

    def load(self, data: Dict[str, Any]):
        self.text = data["text"]


class ExitItem(Item):
    """Represents an exit item in menu"""

    def __init__(self, text: str = "󰈆 Exit", **kwargs):
        super().__init__(text, **kwargs)

    def select_outcome(self):
        return SelectOutcome.EXIT

    def select_action(self):
        pass


class StatelessItem(Item):
    """Represents single state item in menu"""


class Menu:
    """Represents menu items"""

    def __init__(self, items: List[Item] = None, **kwargs):
        self.items = items
        self.id = kwargs.get("id", "main")
        self.keep_selection = kwargs.get("keep_selection", True)

    def set_item_ids(self):
        for i, item in enumerate(self.items):
            item.id = f"{self.id}-{i}"

    def get_headings(self) -> List[str]:
        """Returns rofi headings"""
        headings = []
        self.keep_selection and headings.append(rofi_keep_selection())
        headings.append(rofi_persist_data(self.get_json()))

        return headings

    def render(self, wait: int = 0) -> None:
        """Renders the menu from items"""
        result = self.get_headings()
        for i, item in enumerate(self.items):
            result.append(item.render() + f"\0info\x1f{i}")

        sys.stdout.write("\n".join(result))

    def get_json(self) -> str:
        json_data = {}
        for i, item in enumerate(self.items):
            json_data[str(i)] = item.save()

        return json.dumps(json_data)

    def load_json(self, json_data: str):
        json_data = json.loads(json_data)
        for i, item in enumerate(self.items):
            item.load(json_data[str(i)])

    def apply_select(self, item_id: str):
        """
        item_id: XX-YY-ZZ -> XX is position in current menu
        """
        # extract current position
        id_list = item_id.split("-")
        i = id_list[1]
        action = self.items[i].on_select(id_list=id_list[1:])

        match action:
            case SelectOutcome.REFRESH:
                self.render()
            case SelectOutcome.EXIT:
                exit(0)
            case SelectOutcome.SUBMENU:
                return


class SubMenu(Item):
    """Represents sub menu items"""

    def __init__(self, text: str = "<undefined>", items: List[Item] = None, **kwargs):
        super().__init__(text, **kwargs)
        self.items = items
        self.id = None
        self.keep_selection = kwargs.get("keep_selection", True)

    def on_select(self, **kwargs):
        id_list = kwargs["id_list"]
        i = id_list[1]
        action = self.items[i].on_select(id_list=id_list[1:])
        match action:
            case SelectOutcome.REFRESH:
                self.render()
                return SelectOutcome.SUBMENU
            case SelectOutcome.EXIT:
                exit(0)
            case SelectOutcome.SUBMENU:
                return SelectOutcome.SUBMENU

    def set_item_ids(self):
        for i, item in enumerate(self.items):
            item.id = f"{self.id}-{i}"

    def get_headings(self) -> List[str]:
        """Returns rofi headings"""
        headings = []
        self.keep_selection and headings.append(rofi_keep_selection())
        headings.append(rofi_persist_data(self.get_json()))

        return headings

    def render(self, wait: int = 0) -> None:
        """Renders the menu from items"""
        result = self.get_headings()
        for i, item in enumerate(self.items):
            result.append(item.render() + f"\0info\x1f{i}")

        sys.stdout.write("\n".join(result))

    def get_json(self) -> str:
        json_data = {}
        for i, item in enumerate(self.items):
            json_data[str(i)] = item.save()

        return json.dumps(json_data)

    def load_json(self, json_data: str):
        json_data = json.loads(json_data)
        for i, item in enumerate(self.items):
            item.load(json_data[str(i)])
