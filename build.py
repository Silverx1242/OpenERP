"""
Script para construir el ejecutable de OpenPYME ERP
Usa PyInstaller para crear un ejecutable para Windows, macOS o Linux
"""
import PyInstaller.__main__
import os
import sys

# Configuración
APP_NAME = "OpenPYME_ERP"
MAIN_SCRIPT = "main.py"

# Detectar el sistema operativo
IS_MACOS = sys.platform == 'darwin'
IS_WINDOWS = sys.platform == 'win32'
IS_LINUX = sys.platform.startswith('linux')

# Seleccionar el icono según el sistema operativo (desde assets/)
if IS_MACOS:
    ICON_FILE = "assets/icono.icns"  # macOS usa formato .icns
    EXECUTABLE_EXT = ".app"
elif IS_WINDOWS:
    ICON_FILE = "assets/icono.ico"  # Windows usa formato .ico
    EXECUTABLE_EXT = ".exe"
else:
    ICON_FILE = "assets/icono.ico"  # Linux también puede usar .ico
    EXECUTABLE_EXT = ""

# Archivos y carpetas a incluir
ADD_DATA = [
    ("app/ui", "app/ui"),  # Incluir la carpeta UI completa
    ("assets", "assets"),  # Incluir assets (por si hay recursos adicionales)
]

# Opciones de PyInstaller
OPTIONS = [
    f"--name={APP_NAME}",
    "--onefile",  # Crear un solo archivo ejecutable
    "--clean",  # Limpiar caché antes de construir
    "--noupx",  # No usar UPX (puede causar problemas con antivirus)
]

# Configurar opciones según el sistema operativo
if IS_MACOS:
    OPTIONS.append("--windowed")  # macOS usa --windowed
    OPTIONS.append("--onedir")  # Para macOS, es mejor usar onedir para .app bundle
    OPTIONS.append(f"--osx-bundle-identifier=com.openpyme.erp")
    USE_SPEC_FILE = False
elif IS_WINDOWS:
    OPTIONS.append("--noconsole")  # Windows usa --noconsole
    USE_SPEC_FILE = False
else:
    OPTIONS.append("--noconsole")  # Linux también usa --noconsole
    USE_SPEC_FILE = False

# Agregar archivos de datos
for src, dst in ADD_DATA:
    # macOS usa : como separador, Windows usa ;
    separator = ":" if IS_MACOS else os.pathsep
    OPTIONS.append(f"--add-data={src}{separator}{dst}")

# Si hay un icono, agregarlo
if ICON_FILE and os.path.exists(ICON_FILE):
    OPTIONS.append(f"--icon={ICON_FILE}")
    print(f"✓ Icono encontrado: {ICON_FILE}")
else:
    # Intentar con el icono alternativo si no existe el principal
    if IS_MACOS and not os.path.exists(ICON_FILE):
        alt_icon = "assets/icono.ico"
        if os.path.exists(alt_icon):
            print("⚠ No se encontró assets/icono.icns, pero existe assets/icono.ico")
            print("  💡 Para macOS, necesitas convertir el icono a .icns")
            print("  💡 Puedes usar: iconutil -c icns icono.iconset")
    elif not IS_MACOS and not os.path.exists(ICON_FILE):
        print(f"⚠ Icono no encontrado: {ICON_FILE} (continuando sin icono)")

# Ejecutar PyInstaller
print(f"\n{'='*60}")
print(f"Construyendo ejecutable para: {sys.platform}")
print(f"{'='*60}\n")

print("Iniciando construcción del ejecutable...")
print(f"Opciones: {' '.join(OPTIONS)}\n")
PyInstaller.__main__.run([
    MAIN_SCRIPT,
    *OPTIONS
])

if IS_MACOS:
    output_path = f"dist/{APP_NAME}{EXECUTABLE_EXT}"
else:
    output_path = f"dist/{APP_NAME}{EXECUTABLE_EXT}"

print(f"\n{'='*60}")
print("¡Construcción completada!")
print(f"{'='*60}")
print(f"El ejecutable se encuentra en: {output_path}")
if IS_MACOS:
    print("\n💡 Nota para macOS:")
    print("   - El ejecutable es un .app bundle")
    print("   - Puedes moverlo a /Applications para instalarlo")
    print("   - Si macOS muestra una advertencia de seguridad:")
    print("     Sistema > Seguridad y Privacidad > Permitir")

