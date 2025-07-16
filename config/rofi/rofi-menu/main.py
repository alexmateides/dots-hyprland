from .models3 import *
import os

menu = Menu(
    items=[
        Item(text="A"),
        Item(text="B"),
        ExitItem()
    ],
)


def run_menu(menu: Menu) -> None:
    rofi_retv = os.environ.get("ROFI_RETV", "0")
    rofi_info = os.environ.get("ROFI_INFO", "")
    rofi_data = os.environ.get("ROFI_DATA", None)

    menu.set_item_data()

    if rofi_retv == "0":
        menu.render_menu()
    if rofi_retv == "1":
        menu.apply_select(item_id=rofi_info)


if __name__ == "__main__":
    run_menu(menu)
