import json
import time
import sys, os

from .definitions import *
from .rofi import *
from .utils import run_cmd

from typing import List, Dict, Any


class Store:
    """Persistent data storage"""

    def __init__(self):
        self.data = {}

    def data_to_string(self) -> str:
        return rofi_persist_data(json.dumps(self.data))

    def data_from_string(self, data: str) -> None:
        self.data = json.loads(data)


class Item:
    def __init__(self, **kwargs):
        self.text = kwargs.get("text", "<undefined>")
        self.item_id = None
        self._parent_menu = None
        self._main_menu = None

    def render(self):
        return f"{self.text}\0info\x1f{self.item_id}"

    def on_select(self, **kwargs):
        self.text = "B" if self.text == "A" else "A"
        return SelectOutcome.REFRESH

    def save_data(self):
        self._main_menu.store.data[self.item_id] = {
            key: val for key, val in vars(self).items() if not key.startswith("_")
        }

    def set_item_data(self):
        pass


class ExitItem(Item):
    """Represents an exit item in menu"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.text = "󰈆  Exit"

    def on_select(self, **kwargs):
        return SelectOutcome.EXIT


class ReturnItem(Item):
    """Represents an return item in menu"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.text = "󰈆  Return"

    def on_select(self, **kwargs):
        return SelectOutcome.RETURN


class SubMenuItem(Item):
    """Represents an sub menu item in menu"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._items = kwargs.get("items", [])
        self.keep_selection = kwargs.get("keep_selection", True)
        self.force_default_selection = kwargs.get("force_default_selection", 0)
        self.wait_menu = kwargs.get("wait_menu", False)

    def reload(self) -> None:
        self.__init__()
        self.set_item_data()

    def get_headings(self, **kwargs) -> List[str]:
        """Returns rofi headings"""
        headings = []
        self.keep_selection and headings.append(rofi_keep_selection())
        self.force_default_selection is not None and headings.append(
            rofi_force_selection(self.force_default_selection))

        if kwargs.get("wait"):
            if not self.keep_selection:
                headings.append(rofi_keep_selection())
            heading.append(rofi_force_selection(kwargs.get("wait")))
        headings.append(self._main_menu.store.data_to_string())

        return headings

    def render_menu(self, wait: int = 0) -> None:
        """Renders the menu from items"""
        result = self.get_headings()
        for i, item in enumerate(self._items):
            result.append(item.render())

        sys.stdout.write("\n".join(result))

    def on_select(self, **kwargs):
        # extract current position
        id_list = kwargs.get("id_list", [])

        # first entry
        if len(id_list) == 1:
            self.force_default_selection = 0
            self.render_menu()
            return SelectOutcome.SUBMENU

        i = int(id_list[1])
        action = self._items[i].on_select(id_list=id_list[1:])

        match action:
            case SelectOutcome.REFRESH:
                self.force_default_selection = i
                self._main_menu.save_item_data()
                self.render_menu()
                return SelectOutcome.SUBMENU
            case SelectOutcome.EXIT:
                exit(0)
            case SelectOutcome.SUBMENU:
                return SelectOutcome.SUBMENU
            case SelectOutcome.RETURN:
                self.force_default_selection = 0
                if self.wait_menu:
                    self.force_default_selection = self.item_id.split(" ")[-1]
                self._main_menu.save_item_data()
                self._parent_menu.render_menu()
                return SelectOutcome.SUBMENU

    def set_item_data(self):
        for i, item in enumerate(self._items):
            item.item_id = f"{self.item_id}-{i}"
            item._parent_menu = self
            item._main_menu = self._main_menu
            if self._main_menu.store.data.get(item.item_id):
                for key, val in self._main_menu.store.data.get(item.item_id).items():
                    setattr(item, key, val)
            item.set_item_data()

    def save_data(self):
        self._main_menu.store.data[self.item_id] = {
            key: val for key, val in vars(self).items() if not key.startswith("_")
        }

        for item in self._items:
            item.save_data()


class WaitItem(Item):
    """Represents an wait item in menu"""

    def __init__(self, cooldown: int = 10, **kwargs):
        super().__init__(**kwargs)
        self.text = kwargs.get("text", "<undefined>")
        self.stopped = False
        self.default_cooldown = cooldown
        self.cooldown = 0

    def on_select(self, **kwargs):
        # force stop
        if self.stopped:
            self.stopped = False
            self.cooldown = 0
            return SelectOutcome.RETURN
        # return
        if self.cooldown == 1:
            self.cooldown = 0
            return SelectOutcome.RETURN

        if self.cooldown == 0:
            self.cooldown = self.default_cooldown

        if self.cooldown > 1:
            self.cooldown -= 1
            run_cmd(['sh', '-c', 'sleep 0.5 && wtype -k Return'], background=True)
            return SelectOutcome.REFRESH

    def render(self):
        return f"{self.text} {'.' * (3 - int(self.cooldown) % 3)}\0info\x1f{self.item_id}"


class Menu:
    """Represents menu items"""

    def __init__(self, items: List[Item] = None, **kwargs):
        self.items = items
        self.menu_id = "main"
        self.keep_selection = kwargs.get("keep_selection", True)
        self.message = kwargs.get("message", None)
        self.store = Store()

    def reload(self) -> None:
        self.__init__()
        self.set_item_data()

    def set_item_data(self):
        for i, item in enumerate(self.items):
            item.item_id = f"{self.menu_id}-{i}"
            item._parent_menu = self
            item._main_menu = self
            if self.store.data.get(item.item_id):
                for key, val in self.store.data.get(item.item_id).items():
                    setattr(item, key, val)
            item.set_item_data()

    def save_item_data(self):
        for item in self.items:
            item.save_data()

    def get_headings(self, **kwargs) -> List[str]:
        """Returns rofi headings"""
        headings = []
        self.message and headings.append(rofi_message(self.message))
        self.keep_selection and headings.append(rofi_keep_selection())

        if kwargs.get("wait"):
            if not self.keep_selection:
                headings.append(rofi_keep_selection())
            heading.append(rofi_force_selection(kwargs.get("wait")))
        headings.append(self.store.data_to_string())

        return headings

    def render_menu(self, wait: int = 0, **kwargs) -> None:
        """Renders the menu from items"""
        result = self.get_headings()
        for i, item in enumerate(self.items):
            result.append(item.render())

        sys.stdout.write("\n".join(result))

    def apply_select(self, item_id: str):
        """
        item_id: XX-YY-ZZ -> XX is position in current menu
        """
        # extract current position
        id_list = item_id.split("-")
        i = int(id_list[1])
        action = self.items[i].on_select(id_list=id_list[1:])

        match action:
            case SelectOutcome.REFRESH:
                self.save_item_data()
                self.render_menu()
            case SelectOutcome.EXIT:
                exit(0)
            case SelectOutcome.SUBMENU:
                return
