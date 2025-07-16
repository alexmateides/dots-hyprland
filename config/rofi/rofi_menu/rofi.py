"""Rofi specific commands"""
def rofi_keep_selection():
    """Keeps selector button in the previous position after menu refresh"""
    return "\0keep-selection\x1ftrue"

def rofi_force_selection(i: int):
    """Forces selector button to position 0"""
    return f"\0new-selection\x1f{i}"

def rofi_persist_data(data: str):
    """Persists data between script calls in ROFI_DATA env variable"""
    return f"\0data\x1f{data}"

def rofi_message(message: str):
    """Prints message at top"""
    return f"\0message\x1f{message}"