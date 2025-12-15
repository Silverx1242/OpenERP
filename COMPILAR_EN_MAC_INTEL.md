# Guía Paso a Paso: Compilar en Mac Intel

Esta guía te ayudará a compilar OpenPYME ERP directamente en tu Mac Intel.

## Paso 1: Preparar el entorno

### 1.1 Abrir Terminal
- Presiona `Cmd + Espacio` para abrir Spotlight
- Escribe "Terminal" y presiona Enter

### 1.2 Verificar Python
Ejecuta en Terminal:
```bash
python3 --version
```

Si no tienes Python 3.11 o superior:
```bash
# Opción A: Usar Homebrew (recomendado)
brew install python@3.11

# Opción B: Descargar desde python.org
# Ve a: https://www.python.org/downloads/
```

### 1.3 Instalar Homebrew (si no lo tienes)
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

## Paso 2: Obtener el código fuente

### Opción A: Clonar desde GitHub
```bash
cd ~/Desktop
git clone https://github.com/Silverx1242/OpenERP.git
cd OpenERP
```

### Opción B: Descargar ZIP del release
1. Ve a: https://github.com/Silverx1242/OpenERP/releases
2. Descarga `OpenPYME_ERP-Source-v1.0.2.zip` (o la versión más reciente)
3. Extrae el ZIP en el Escritorio
4. Abre Terminal y ejecuta:
```bash
cd ~/Desktop/OpenERP
```

## Paso 3: Instalar dependencias

```bash
# Actualizar pip
python3 -m pip install --upgrade pip

# Instalar dependencias del proyecto
pip3 install -r requirements.txt

# Instalar PyInstaller
pip3 install pyinstaller
```

## Paso 4: Crear el icono (si es necesario)

```bash
# Dar permisos de ejecución al script (si lo descargaste)
chmod +x build-macos-intel.sh

# O crear el icono manualmente
cd assets
mkdir icono.iconset
sips -s format png icono.ico --out temp_icon.png
sips -z 16 16 temp_icon.png --out icono.iconset/icon_16x16.png
sips -z 32 32 temp_icon.png --out icono.iconset/icon_16x16@2x.png
sips -z 32 32 temp_icon.png --out icono.iconset/icon_32x32.png
sips -z 64 64 temp_icon.png --out icono.iconset/icon_32x32@2x.png
sips -z 128 128 temp_icon.png --out icono.iconset/icon_128x128.png
sips -z 256 256 temp_icon.png --out icono.iconset/icon_128x128@2x.png
sips -z 256 256 temp_icon.png --out icono.iconset/icon_256x256.png
sips -z 512 512 temp_icon.png --out icono.iconset/icon_256x256@2x.png
sips -z 512 512 temp_icon.png --out icono.iconset/icon_512x512.png
sips -z 1024 1024 temp_icon.png --out icono.iconset/icon_512x512@2x.png
rm temp_icon.png
iconutil -c icns icono.iconset -o icono.icns
rm -rf icono.iconset
cd ..
```

## Paso 5: Compilar la aplicación

### Método 1: Usar el script automático
```bash
./build-macos-intel.sh
```

### Método 2: Compilar manualmente
```bash
pyinstaller --name="OpenPYME_ERP" \
  --windowed \
  --noconfirm \
  --onedir \
  --icon=assets/icono.icns \
  --add-data="app/ui:app/ui" \
  --add-data="assets:assets" \
  --osx-bundle-identifier="com.openpyme.erp" \
  --clean \
  main.py
```

## Paso 6: Verificar la compilación

```bash
# La aplicación debería estar en:
ls -la dist/OpenPYME_ERP.app

# Verificar la arquitectura (debe ser x86_64 para Intel)
file dist/OpenPYME_ERP.app/Contents/MacOS/OpenPYME_ERP
```

Debería mostrar algo como: `x86_64` o `Mach-O 64-bit executable x86_64`

## Paso 7: Probar la aplicación

```bash
# Abrir la aplicación
open dist/OpenPYME_ERP.app
```

O simplemente haz doble clic en `dist/OpenPYME_ERP.app` desde el Finder.

## Paso 8: Crear DMG (Opcional)

```bash
cd dist
hdiutil create -volname "OpenPYME ERP" \
  -srcfolder "OpenPYME_ERP.app" \
  -ov -format UDZO \
  "OpenPYME_ERP-Intel.dmg"
cd ..
```

El DMG estará en `dist/OpenPYME_ERP-Intel.dmg`

## Solución de problemas

### Error: "Python no encontrado"
```bash
# Verificar que Python está instalado
which python3

# Si no está, instalarlo
brew install python@3.11
```

### Error: "pip no encontrado"
```bash
python3 -m ensurepip --upgrade
```

### Error: "PyInstaller falla"
```bash
# Reinstalar PyInstaller
pip3 uninstall pyinstaller
pip3 install pyinstaller
```

### Error: "No se puede abrir la aplicación"
```bash
# Dar permisos de ejecución
chmod +x dist/OpenPYME_ERP.app/Contents/MacOS/OpenPYME_ERP

# Si macOS bloquea la app:
xattr -cr dist/OpenPYME_ERP.app
```

## Verificar que funciona en Intel

Para asegurarte de que está compilada para Intel:

```bash
file dist/OpenPYME_ERP.app/Contents/MacOS/OpenPYME_ERP
```

Debería decir `x86_64`, no `arm64`.

## Archivos generados

Después de compilar encontrarás en `dist/`:
- `OpenPYME_ERP.app` - La aplicación
- `OpenPYME_ERP-Intel.dmg` - Instalador (si creaste el DMG)

¡Listo! Tu aplicación estará compilada específicamente para Mac Intel.

