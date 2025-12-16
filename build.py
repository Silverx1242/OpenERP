"""
Script to build the OpenERP executable
Uses PyInstaller to create an executable for Windows, macOS or Linux
"""
import PyInstaller.__main__
import os
import sys

# Configuration
APP_NAME = "OpenERP"
MAIN_SCRIPT = "main.py"

# Detect operating system
IS_MACOS = sys.platform == 'darwin'
IS_WINDOWS = sys.platform == 'win32'
IS_LINUX = sys.platform.startswith('linux')

# Select icon according to operating system (from assets/)
if IS_MACOS:
    ICON_FILE = "assets/icono.icns"  # macOS uses .icns format
    EXECUTABLE_EXT = ".app"
elif IS_WINDOWS:
    ICON_FILE = "assets/icono.ico"  # Windows uses .ico format
    EXECUTABLE_EXT = ".exe"
else:
    ICON_FILE = "assets/icono.ico"  # Linux can also use .ico
    EXECUTABLE_EXT = ""

# Files and folders to include
ADD_DATA = [
    ("app/ui", "app/ui"),  # Include complete UI folder
    ("assets", "assets"),  # Include assets (in case there are additional resources)
]

# PyInstaller options
OPTIONS = [
    f"--name={APP_NAME}",
    "--onefile",  # Create a single executable file
    "--clean",  # Clean cache before building
    "--noupx",  # Don't use UPX (can cause problems with antivirus)
]

# Configure options according to operating system
if IS_MACOS:
    OPTIONS.append("--windowed")  # macOS uses --windowed
    OPTIONS.append("--onedir")  # For macOS, it's better to use onedir for .app bundle
    OPTIONS.append(f"--osx-bundle-identifier=com.openerp.erp")
    USE_SPEC_FILE = False
elif IS_WINDOWS:
    OPTIONS.append("--noconsole")  # Windows uses --noconsole
    USE_SPEC_FILE = False
else:
    OPTIONS.append("--noconsole")  # Linux also uses --noconsole
    USE_SPEC_FILE = False

# Add data files
for src, dst in ADD_DATA:
    # macOS uses : as separator, Windows uses ;
    separator = ":" if IS_MACOS else os.pathsep
    OPTIONS.append(f"--add-data={src}{separator}{dst}")

# If there's an icon, add it
if ICON_FILE and os.path.exists(ICON_FILE):
    OPTIONS.append(f"--icon={ICON_FILE}")
    print(f"✓ Icon found: {ICON_FILE}")
else:
    # Try with alternative icon if main one doesn't exist
    if IS_MACOS and not os.path.exists(ICON_FILE):
        alt_icon = "assets/icono.ico"
        if os.path.exists(alt_icon):
            print("⚠ assets/icono.icns not found, but assets/icono.ico exists")
            print("  💡 For macOS, you need to convert the icon to .icns")
            print("  💡 You can use: iconutil -c icns icono.iconset")
    elif not IS_MACOS and not os.path.exists(ICON_FILE):
        print(f"⚠ Icon not found: {ICON_FILE} (continuing without icon)")

# Execute PyInstaller
print(f"\n{'='*60}")
print(f"Building executable for: {sys.platform}")
print(f"{'='*60}\n")

print("Starting executable build...")
print(f"Options: {' '.join(OPTIONS)}\n")
PyInstaller.__main__.run([
    MAIN_SCRIPT,
    *OPTIONS
])

if IS_MACOS:
    output_path = f"dist/{APP_NAME}{EXECUTABLE_EXT}"
else:
    output_path = f"dist/{APP_NAME}{EXECUTABLE_EXT}"

print(f"\n{'='*60}")
print("Build completed!")
print(f"{'='*60}")
print(f"Executable is located at: {output_path}")
if IS_MACOS:
    print("\n💡 Note for macOS:")
    print("   - The executable is a .app bundle")
    print("   - You can move it to /Applications to install")
    print("   - If macOS shows a security warning:")
    print("     System > Security & Privacy > Allow")

