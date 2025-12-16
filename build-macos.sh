#!/bin/bash
# Corrected build script for the actual project structure

echo "🔨 Building OpenERP for macOS (corrected structure)"
echo "============================================================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Verify we're in the correct folder
if [ ! -f "main.py" ]; then
    echo -e "${RED}❌ Error: main.py not found${NC}"
    echo "   Make sure you're in the project folder"
    exit 1
fi

# Verify structure
echo "📁 Verifying project structure..."
if [ ! -d "app" ]; then
    echo -e "${RED}❌ Error: app/ folder not found${NC}"
    exit 1
fi

if [ ! -f "app/ui/index.html" ]; then
    echo -e "${RED}❌ Error: app/ui/index.html not found${NC}"
    exit 1
fi

echo -e "${GREEN}✅${NC} Structure correct"
echo ""

# Verify Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Error: Python 3 is not installed${NC}"
    exit 1
fi

PYTHON_CMD="python3"
# Try to use Python 3.11 if available
if command -v python3.11 &> /dev/null; then
    PYTHON_CMD="python3.11"
    echo "🐍 Using Python 3.11"
elif command -v python3.10 &> /dev/null; then
    PYTHON_CMD="python3.10"
    echo "🐍 Using Python 3.10"
else
    echo "🐍 Using Python: $($PYTHON_CMD --version)"
fi
echo ""

# Install dependencies
echo "📦 Installing dependencies..."
$PYTHON_CMD -m pip install --quiet --upgrade pip
$PYTHON_CMD -m pip install --quiet -r requirements.txt
$PYTHON_CMD -m pip install --quiet pyinstaller

# Create .icns icon if it doesn't exist
if [ ! -f "assets/icono.icns" ] && [ -f "assets/icono.ico" ]; then
    echo "🎨 Creating .icns icon..."
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
        echo -e "${GREEN}✅${NC} Icon created"
    fi
    echo ""
fi

# Clean previous build
echo "🧹 Cleaning previous build..."
rm -rf build dist *.spec
echo ""

# Build with PyInstaller
echo "🔨 Building application..."
echo "   (This may take 2-5 minutes)"
echo ""

ICON_ARG=""
if [ -f "assets/icono.icns" ]; then
    ICON_ARG="--icon=assets/icono.icns"
fi

# Build with correct structure
# --add-data copies files to the Resources folder in the bundle
$PYTHON_CMD -m PyInstaller \
  --name="OpenERP" \
  --windowed \
  --noconsole \
  --onedir \
  --noconfirm \
  --clean \
  $ICON_ARG \
  --add-data="app:app" \
  --add-data="assets:assets" \
  --osx-bundle-identifier="com.openerp.erp" \
  --hidden-import=webview \
  --hidden-import=sqlite3 \
  --hidden-import=openpyxl \
  main.py

if [ $? -eq 0 ] && [ -d "dist/OpenERP.app" ]; then
    echo ""
    echo -e "${GREEN}============================================================="
    echo "  ✅ Build completed!"
    echo -e "=============================================================${NC}"
    echo ""
    
    # Verify bundle structure
    echo "🔍 Verifying bundle structure..."
    
    if [ -f "dist/OpenERP.app/Contents/MacOS/OpenERP" ]; then
        echo -e "${GREEN}✅${NC} Executable found"
    else
        echo -e "${RED}❌${NC} Executable NOT found"
    fi
    
    # Verify files in Resources
    if [ -f "dist/OpenERP.app/Contents/Resources/app/ui/index.html" ]; then
        echo -e "${GREEN}✅${NC} index.html found in Resources"
    elif [ -d "dist/OpenERP.app/Contents/Resources/app" ]; then
        echo -e "${YELLOW}⚠️${NC}  app folder found, but index.html in another location"
        find dist/OpenERP.app/Contents/Resources -name "index.html" 2>/dev/null | head -3
    else
        echo -e "${RED}❌${NC} app/ files NOT found in Resources"
        echo "   Searching in entire bundle..."
        find dist/OpenERP.app -name "index.html" 2>/dev/null
    fi
    
    echo ""
    echo "📦 Application created at:"
    echo "   $(pwd)/dist/OpenERP.app"
    echo ""
    echo "💡 Test the application:"
    echo "   open dist/OpenERP.app"
    echo ""
    
else
    echo ""
    echo -e "${RED}❌ Error during build${NC}"
    exit 1
fi
