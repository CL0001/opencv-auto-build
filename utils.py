import os
import shutil
import winreg

def move_contents(src, dst) -> None:
    for item in os.listdir(src):
        shutil.move(os.path.join(src, item), os.path.join(dst, item))

def add_to_system_path(paths) -> None:
    key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment", 0, winreg.KEY_READ | winreg.KEY_WRITE)
    
    try:
        existing_path, _ = winreg.QueryValueEx(key, "Path")
    except FileNotFoundError:
        existing_path = ""

    new_paths = [p for p in paths if p not in existing_path]
    
    if new_paths:
        new_path = existing_path + ";" + ";".join(new_paths)
        winreg.SetValueEx(key, "Path", 0, winreg.REG_EXPAND_SZ, new_path)
        print("Successfully updated system PATH. Restart required for changes to take effect.")

    winreg.CloseKey(key)