#!/bin/bash
# Script para compilar OpenPYME ERP en Mac Intel localmente

echo "========================================="
echo "  Compilando OpenPYME ERP para Intel"
echo "========================================="
echo ""

# Verificar que estamos en macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo "❌ Error: Este script solo funciona en macOS"
    exit 1
fi

# Verificar arquitectura
ARCH=$(uname -m)
echo "📱 Arquitectura detectada: $ARCH"

if [[ "$ARCH" != "x86_64" ]]; then
    echo "⚠️  Advertencia: Este script está optimizado para Mac Intel (x86_64)"
    echo "   Si tienes Apple Silicon, usa el workflow de GitHub Actions"
fi

# Verificar Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 no está instalado"
    echo "   Instálalo con: brew install python@3.11"
    exit 1
fi

PYTHON_VERSION=$(python3 --version)
echo "🐍 Python detectado: $PYTHON_VERSION"
echo ""

# Instalar dependencias si es necesario
echo "📦 Instalando dependencias..."
python3 -m pip install --upgrade pip
pip3 install -r requirements.txt
pip3 install pyinstaller

# Crear icono .icns si no existe
if [ ! -f "assets/icono.icns" ]; then
    echo ""
    echo "🎨 Creando icono .icns..."
    ICONSET_DIR="assets/icono.iconset"
    mkdir -p "$ICONSET_DIR"
    
    if [ -f "assets/icono.ico" ]; then
        sips -s format png assets/icono.ico --out temp_icon.png
        sips -z 16 16 temp_icon.png --out "$ICONSET_DIR/icon_16x16.png"
        sips -z 32 32 temp_icon.png --out "$ICONSET_DIR/icon_16x16@2x.png"
        sips -z 32 32 temp_icon.png --out "$ICONSET_DIR/icon_32x32.png"
        sips -z 64 64 temp_icon.png --out "$ICONSET_DIR/icon_32x32@2x.png"
        sips -z 128 128 temp_icon.png --out "$ICONSET_DIR/icon_128x128.png"
        sips -z 256 256 temp_icon.png --out "$ICONSET_DIR/icon_128x128@2x.png"
        sips -z 256 256 temp_icon.png --out "$ICONSET_DIR/icon_256x256.png"
        sips -z 512 512 temp_icon.png --out "$ICONSET_DIR/icon_256x256@2x.png"
        sips -z 512 512 temp_icon.png --out "$ICONSET_DIR/icon_512x512.png"
        sips -z 1024 1024 temp_icon.png --out "$ICONSET_DIR/icon_512x512@2x.png"
        rm temp_icon.png
        iconutil -c icns "$ICONSET_DIR" -o assets/icono.icns
        rm -rf "$ICONSET_DIR"
        echo "✓ Icono creado"
    else
        echo "⚠️  No se encontró assets/icono.ico"
    fi
fi

echo ""
echo "🔨 Compilando aplicación con PyInstaller..."
echo ""

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

if [ $? -eq 0 ]; then
    echo ""
    echo "========================================="
    echo "  ✅ Compilación completada!"
    echo "========================================="
    echo ""
    echo "📦 La aplicación está en: dist/OpenPYME_ERP.app"
    echo ""
    echo "💡 Puedes:"
    echo "   1. Arrastrarla a la carpeta Aplicaciones"
    echo "   2. O ejecutarla desde ahí directamente"
    echo ""
    
    # Crear DMG opcional
    read -p "¿Crear archivo DMG? (s/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Ss]$ ]]; then
        if [ -d "dist/OpenPYME_ERP.app" ]; then
            hdiutil create -volname "OpenPYME ERP" -srcfolder "dist/OpenPYME_ERP.app" -ov -format UDZO "dist/OpenPYME_ERP-Intel.dmg"
            echo "✓ DMG creado: dist/OpenPYME_ERP-Intel.dmg"
        fi
    fi
else
    echo ""
    echo "❌ Error durante la compilación"
    exit 1
fi

