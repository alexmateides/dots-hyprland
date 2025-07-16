import json
import time
import sys, os

from .definitions import *
from .rofi import *
from .utils import run_cmd, get_process_elapsed_time

from typing import List, Dict, Any


class Store:
    """
    Stores session state data between script calls
    Data are stored in JSON format in /tmp
    """

    def __init__(self, path: str):
        self.path = path
        self.data = {}

    def load(self):
        """Loads data from JSON file"""
        with open(self.path) as f:
            self.data = json.load(f)

    def save(self):
        """Saves data to JSON file"""
        with open(self.path, 'w') as f:
            json.dump(self.data, f)


class Menu:
    """Main menu class"""

    def __init__(self, **kwargs):
        self.id = "main"
        self._items: List[Item] = kwargs.get('items', [])

        # --- Flags ---
        self.flag_keep_selection = kwargs.get('keep_selection', True)
        self.flag_force_selection = kwargs.get('force_selection', None)
        self.flag_message = kwargs.get('message', None)

        # --- Store init ---
        self.store_path = kwargs.get('store_path', "/tmp/rofi_menu_session.json")
        self.store = Store(self.store_path)

    def set_item_data(self) -> None:
        """Sets child item data from the session store"""
        for i, item in enumerate(self._items):
            item.item_id = f"{self.id}-{i}"
            item._parent_menu = self
            item._main_menu = self
            if self.store.data.get(item.item_id):
                for key, val in self.store.data.get(item.item_id).items():
                    setattr(item, key, val)
            item.set_item_data()

    def reload(self) -> None:
        """Reloads all objects from the session store"""
        self.__init__()
        self.set_item_data()

    def save_item_data(self) -> None:
        """Saves child item data to the session store"""
        for item in self._items:
            item.save_data()

    def get_rofi_metadata(self) -> List[str]:
        """Returns list of rofi control strings set in flags"""
        headings = []
        self.flag_message and headings.append(rofi_message(self.flag_message))
        self.flag_keep_selection and headings.append(rofi_keep_selection())
        self.flag_force_selection is not None and headings.append(rofi_force_selection(self.flag_force_selection))

        # append session store path
        headings.append(rofi_persist_data(self.store_path))

        return headings

    def render_menu(self, **kwargs) -> None:
        """Renders the menu from child items"""
        result = self.get_rofi_metadata()
        for i, item in enumerate(self._items):
            result.append(item.render_item())

        sys.stdout.write("\n".join(result))

    def apply_select(self, **kwargs) -> SelectOutcome | None:
        """Selects coresponding item from the menu"""
        item_id = kwargs.get("item_id", None)
        if not item_id:
            raise ValueError("No item id when calling main menu apply_select")

        # item_id = XX-YY-ZZ... ==> {menu_idx}-{idx_in_current_(sub)menu}-{idx_in_next_submenu}...
        id_list = item_id.split('-')
        idx = int(id_list[1])
        action = self._items[idx].on_select(id_list=id_list[1:])

        match action:
            case SelectOutcome.REFRESH:  # render current menu
                self.save_item_data()
                self.render_menu()
            case SelectOutcome.EXIT:  # exit the script
                exit(0)
            case SelectOutcome.SUBMENU:  # let the submenu handle rendering
                return


# === |--- ITEMS ---| ===

class Item:
    """Basic menu item"""

    def __init__(self, **kwargs):
        self.text = kwargs.get('text', '<undefined>')
        self.id = None
        self._parent_menu: Menu = None
        self._main_menu: Menu = None

    def on_select(self, **kwargs):
        """Here goes the item code"""
        self.text = "<pressed>"  # sample driver code
        return SelectOutcome.REFRESH

    def render_item(self):
        """Returns rofi string"""
        return f"{self.text}\0info\x1f{self.item_id}"

    def save_data(self):
        """
        Saves itself to main menu store for persistence between script calls
        (private attributes -> '_main_menu' etc. get ignored)
        """
        self._main_menu.store.data[self.id] = {
            key: val for key, val in vars(self).items() if not key.startswith("_")
        }

    def set_item_data(self):
        """Implemented in submenus"""
        pass


class ExitItem(Item):
    """Exits the script"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.text = "󰈆  Exit"

    def on_select(self, **kwargs):
        return SelectOutcome.EXIT


class ReturnItem(Item):
    """Returns from submenu to parent menu"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.text = "󰈆  Return"

    def on_select(self, **kwargs):
        return SelectOutcome.RETURN


class ToggleItem(Item):
    """
    Binary toggle item
    Executes on_select_true/false according to 'status' flag
    """

    def __init__(self, status: bool = False, **kwargs):
        super().__init__(**kwargs)
        self.status = status
        self.text = "ON" if self.status else "OFF"

    def on_select(self, **kwargs):
        if self.status:
            return self.on_select_true()
        return self.on_select_false()

    def on_select_true(self):
        self.status = False
        self.text = "OFF"
        return SelectOutcome.REFRESH

    def on_select_false(self):
        self.status = True
        self.text = "ON"
        return SelectOutcome.REFRESH


class SubMenuItem(Item):
    """Used to create a (nested) submenu"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._items = kwargs.get("items", [])

        # --- Flags ---
        self.flag_keep_selection = kwargs.get("keep_selection", True)
        self.flag_force_selection = kwargs.get("default_selection", 0)
        self.flag_message = kwargs.get("message", None)

    def reload(self) -> None:
        """Reloads all child objets"""
        self.__init__()
        self.set_item_data()

    def get_rofi_metadata(self) -> List[str]:
        """Returns list of rofi control strings set in flags"""
        headings = []
        self.flag_message and headings.append(rofi_message(self.flag_message))
        self.flag_keep_selection and headings.append(rofi_keep_selection())
        self.flag_force_selection is not None and headings.append(rofi_force_selection(self.flag_force_selection))

        # append session store path
        headings.append(rofi_persist_data(self._main_menu.store_path))

        return headings

    def render_menu(self, wait: int = 0) -> None:
        """Renders the menu from items"""
        result = self.get_rofi_metadata()
        for i, item in enumerate(self._items):
            result.append(item.render_item())

        sys.stdout.write("\n".join(result))

    def on_select(self, **kwargs):
        # extract current position
        id_list = kwargs.get("id_list", [])

        if len(id_list) == 0:
            raise ValueError("No item id passed when calling submenu")

        # first entry
        if len(id_list) == 1:
            self.force_default_selection = 0
            self.render_menu()
            return SelectOutcome.SUBMENU

        idx = int(id_list[1])
        action = self._items[idx].on_select(id_list=id_list[1:])

        match action:
            case SelectOutcome.REFRESH:
                self.force_default_selection = idx
                self._main_menu.save_item_data()
                self.render_menu()
                return SelectOutcome.SUBMENU
            case SelectOutcome.EXIT:
                exit(0)
            case SelectOutcome.SUBMENU:
                return SelectOutcome.SUBMENU
            case SelectOutcome.RETURN:
                self.force_default_selection = 0
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
        self._main_menu.store.data[self.id] = {
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
        self.clicker_pid = None

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
            pid, _ = run_cmd(['sh', '-c', 'sleep 0.5 && wtype -k Return'], background=True)
            self.clicker_pid = pid
            return SelectOutcome.REFRESH

    def render_item(self):
        return f"{self.text} {'.' * (3 - int(self.cooldown) % 3)}\0info\x1f{self.item_id}"


