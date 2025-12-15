#!/bin/bash
# Script rápido para compilar en Mac Intel - Ejecutar desde la carpeta del proyecto

echo "🚀 Compilación rápida de OpenPYME ERP para Mac Intel"
echo "=================================================="
echo ""

# Colores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Verificar que estamos en la carpeta correcta
if [ ! -f "main.py" ]; then
    echo -e "${RED}❌ Error: No se encuentra main.py${NC}"
    echo "   Asegúrate de estar en la carpeta del proyecto"
    exit 1
fi

# Verificar Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Error: Python 3 no está instalado${NC}"
    echo "   Instálalo con: brew install python@3.11"
    exit 1
fi

echo -e "${GREEN}✓${NC} Python detectado: $(python3 --version)"
echo ""

# Instalar/actualizar dependencias
echo "📦 Instalando dependencias..."
python3 -m pip install --quiet --upgrade pip
pip3 install --quiet -r requirements.txt
pip3 install --quiet pyinstaller

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Error al instalar dependencias${NC}"
    exit 1
fi

echo -e "${GREEN}✓${NC} Dependencias instaladas"
echo ""

# Crear icono si no existe
if [ ! -f "assets/icono.icns" ] && [ -f "assets/icono.ico" ]; then
    echo "🎨 Creando icono .icns..."
    ICONSET_DIR="assets/icono.iconset"
    mkdir -p "$ICONSET_DIR"
    sips -s format png assets/icono.ico --out temp_icon.png > /dev/null 2>&1
    sips -z 16 16 temp_icon.png --out "$ICONSET_DIR/icon_16x16.png" > /dev/null 2>&1
    sips -z 32 32 temp_icon.png --out "$ICONSET_DIR/icon_16x16@2x.png" > /dev/null 2>&1
    sips -z 32 32 temp_icon.png --out "$ICONSET_DIR/icon_32x32.png" > /dev/null 2>&1
    sips -z 64 64 temp_icon.png --out "$ICONSET_DIR/icon_32x32@2x.png" > /dev/null 2>&1
    sips -z 128 128 temp_icon.png --out "$ICONSET_DIR/icon_128x128.png" > /dev/null 2>&1
    sips -z 256 256 temp_icon.png --out "$ICONSET_DIR/icon_128x128@2x.png" > /dev/null 2>&1
    sips -z 256 256 temp_icon.png --out "$ICONSET_DIR/icon_256x256.png" > /dev/null 2>&1
    sips -z 512 512 temp_icon.png --out "$ICONSET_DIR/icon_256x256@2x.png" > /dev/null 2>&1
    sips -z 512 512 temp_icon.png --out "$ICONSET_DIR/icon_512x512.png" > /dev/null 2>&1
    sips -z 1024 1024 temp_icon.png --out "$ICONSET_DIR/icon_512x512@2x.png" > /dev/null 2>&1
    rm -f temp_icon.png
    iconutil -c icns "$ICONSET_DIR" -o assets/icono.icns > /dev/null 2>&1
    rm -rf "$ICONSET_DIR"
    echo -e "${GREEN}✓${NC} Icono creado"
    echo ""
fi

# Compilar
echo "🔨 Compilando aplicación..."
echo "   (Esto puede tardar 2-5 minutos)"
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
  main.py > /dev/null 2>&1

if [ $? -eq 0 ] && [ -d "dist/OpenPYME_ERP.app" ]; then
    echo ""
    echo -e "${GREEN}=================================================="
    echo "  ✅ ¡Compilación exitosa!"
    echo -e "==================================================${NC}"
    echo ""
    echo "📦 Aplicación creada en:"
    echo "   $(pwd)/dist/OpenPYME_ERP.app"
    echo ""
    
    # Verificar arquitectura
    ARCH=$(file dist/OpenPYME_ERP.app/Contents/MacOS/OpenPYME_ERP 2>/dev/null | grep -o "x86_64\|arm64" | head -1)
    if [ "$ARCH" = "x86_64" ]; then
        echo -e "${GREEN}✓${NC} Arquitectura: Intel (x86_64) - Correcto para tu Mac"
    elif [ "$ARCH" = "arm64" ]; then
        echo -e "${YELLOW}⚠${NC}  Arquitectura: Apple Silicon (arm64)"
    else
        echo -e "${YELLOW}⚠${NC}  No se pudo verificar la arquitectura"
    fi
    echo ""
    echo "💡 Próximos pasos:"
    echo "   1. Prueba la aplicación: open dist/OpenPYME_ERP.app"
    echo "   2. Si funciona, arrástrala a la carpeta Aplicaciones"
    echo ""
else
    echo ""
    echo -e "${RED}❌ Error durante la compilación${NC}"
    echo "   Revisa los mensajes anteriores para más detalles"
    exit 1
fi

