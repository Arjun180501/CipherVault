import PyInstaller.__main__
import os
from PyInstaller.building.datastruct import Tree


# Paths to your CLI & GUI entry points
CLI_ENTRY = os.path.join("src", "ciphervault", "cli", "cli.py")
GUI_ENTRY = os.path.join("src", "ciphervault", "gui", "main.py")

ICON_PATH = os.path.join("assets", "icons", "ciphervault_logo.ico")


print("[*] Building CLI executable...")
PyInstaller.__main__.run([
    CLI_ENTRY,
    "--name", "cvault",
    "--onefile",
    "--console",
    "--add-data", "vaults;vaults",
    "--hidden-import", "numpy",
    "--hidden-import", "numpy.core.multiarray",
    "--clean"
])

print("[*] Building GUI executable...")
PyInstaller.__main__.run([
    GUI_ENTRY,
    "--name", "cvault-gui",
    "--onefile",
    "--noconsole",
    "--icon", ICON_PATH,
    "--add-data", "assets/images;assets/images",
    "--add-data", "assets/icons;assets/icons",
    "--add-data", "vaults;vaults",
    "--clean"
])

print("\n[+] Build complete! Check the dist/ folder.\n")
