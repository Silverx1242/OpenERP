#!/bin/bash
# Script de compilación corregido para la estructura real del proyecto

echo "🔨 Compilando OpenPYME ERP para macOS (estructura corregida)"
echo "============================================================="
echo ""

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Verificar que estamos en la carpeta correcta
if [ ! -f "main.py" ]; then
    echo -e "${RED}❌ Error: No se encuentra main.py${NC}"
    echo "   Asegúrate de estar en la carpeta del proyecto"
    exit 1
fi

# Verificar estructura
echo "📁 Verificando estructura del proyecto..."
if [ ! -d "app" ]; then
    echo -e "${RED}❌ Error: No se encuentra la carpeta app/${NC}"
    exit 1
fi

if [ ! -f "app/ui/index.html" ]; then
    echo -e "${RED}❌ Error: No se encuentra app/ui/index.html${NC}"
    exit 1
fi

echo -e "${GREEN}✅${NC} Estructura correcta"
echo ""

# Verificar Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Error: Python 3 no está instalado${NC}"
    exit 1
fi

PYTHON_CMD="python3"
# Intentar usar Python 3.11 si está disponible
if command -v python3.11 &> /dev/null; then
    PYTHON_CMD="python3.11"
    echo "🐍 Usando Python 3.11"
elif command -v python3.10 &> /dev/null; then
    PYTHON_CMD="python3.10"
    echo "🐍 Usando Python 3.10"
else
    echo "🐍 Usando Python: $($PYTHON_CMD --version)"
fi
echo ""

# Instalar dependencias
echo "📦 Instalando dependencias..."
$PYTHON_CMD -m pip install --quiet --upgrade pip
$PYTHON_CMD -m pip install --quiet -r requirements.txt
$PYTHON_CMD -m pip install --quiet pyinstaller

# Crear icono .icns si no existe
if [ ! -f "assets/icono.icns" ] && [ -f "assets/icono.ico" ]; then
    echo "🎨 Creando icono .icns..."
    ICONSET_DIR="assets/icono.iconset"
    mkdir -p "$ICONSET_DIR"
    sips -s format png assets/icono.ico --out temp_icon.png > /dev/null 2>&1
    if [ -f "temp_icon.png" ]; then
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
        rm temp_icon.png
        iconutil -c icns "$ICONSET_DIR" -o assets/icono.icns > /dev/null 2>&1
        rm -rf "$ICONSET_DIR"
        echo -e "${GREEN}✅${NC} Icono creado"
    fi
    echo ""
fi

# Limpiar compilación anterior
echo "🧹 Limpiando compilación anterior..."
rm -rf build dist *.spec
echo ""

# Compilar con PyInstaller
echo "🔨 Compilando aplicación..."
echo "   (Esto puede tardar 2-5 minutos)"
echo ""

ICON_ARG=""
if [ -f "assets/icono.icns" ]; then
    ICON_ARG="--icon=assets/icono.icns"
fi

# Compilar con la estructura correcta
# --add-data copia los archivos a la carpeta Resources en el bundle
$PYTHON_CMD -m PyInstaller \
  --name="OpenPYME_ERP" \
  --windowed \
  --noconsole \
  --onedir \
  --noconfirm \
  --clean \
  $ICON_ARG \
  --add-data="app:app" \
  --add-data="assets:assets" \
  --osx-bundle-identifier="com.openpyme.erp" \
  --hidden-import=webview \
  --hidden-import=sqlite3 \
  --hidden-import=openpyxl \
  main.py

if [ $? -eq 0 ] && [ -d "dist/OpenPYME_ERP.app" ]; then
    echo ""
    echo -e "${GREEN}============================================================="
    echo "  ✅ Compilación completada!"
    echo -e "=============================================================${NC}"
    echo ""
    
    # Verificar estructura del bundle
    echo "🔍 Verificando estructura del bundle..."
    
    if [ -f "dist/OpenPYME_ERP.app/Contents/MacOS/OpenPYME_ERP" ]; then
        echo -e "${GREEN}✅${NC} Ejecutable encontrado"
    else
        echo -e "${RED}❌${NC} Ejecutable NO encontrado"
    fi
    
    # Verificar archivos en Resources
    if [ -f "dist/OpenPYME_ERP.app/Contents/Resources/app/ui/index.html" ]; then
        echo -e "${GREEN}✅${NC} index.html encontrado en Resources"
    elif [ -d "dist/OpenPYME_ERP.app/Contents/Resources/app" ]; then
        echo -e "${YELLOW}⚠️${NC}  Carpeta app encontrada, pero index.html en otra ubicación"
        find dist/OpenPYME_ERP.app/Contents/Resources -name "index.html" 2>/dev/null | head -3
    else
        echo -e "${RED}❌${NC} Archivos app/ NO encontrados en Resources"
        echo "   Buscando en todo el bundle..."
        find dist/OpenPYME_ERP.app -name "index.html" 2>/dev/null
    fi
    
    echo ""
    echo "📦 Aplicación creada en:"
    echo "   $(pwd)/dist/OpenPYME_ERP.app"
    echo ""
    echo "💡 Prueba la aplicación:"
    echo "   open dist/OpenPYME_ERP.app"
    echo ""
    
else
    echo ""
    echo -e "${RED}❌ Error durante la compilación${NC}"
    exit 1
fi

