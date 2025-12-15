#!/bin/bash
# Script para verificar la estructura del bundle .app

echo "🔍 Verificando estructura del bundle .app"
echo "========================================="
echo ""

APP_PATH="dist/OpenPYME_ERP.app"

if [ ! -d "$APP_PATH" ]; then
    echo "❌ Error: No se encuentra $APP_PATH"
    echo "   Asegúrate de haber compilado primero"
    exit 1
fi

echo "📁 Estructura del bundle:"
echo ""
tree -L 3 "$APP_PATH" 2>/dev/null || find "$APP_PATH" -maxdepth 3 | head -30

echo ""
echo "========================================="
echo "🔍 Verificaciones importantes:"
echo ""

# Verificar ejecutable
if [ -f "$APP_PATH/Contents/MacOS/OpenPYME_ERP" ]; then
    echo "✅ Ejecutable encontrado: Contents/MacOS/OpenPYME_ERP"
    ARCH=$(file "$APP_PATH/Contents/MacOS/OpenPYME_ERP" | grep -o "x86_64\|arm64")
    echo "   Arquitectura: $ARCH"
else
    echo "❌ Ejecutable NO encontrado en Contents/MacOS/"
fi

# Verificar index.html
if [ -f "$APP_PATH/Contents/Resources/app/ui/index.html" ]; then
    echo "✅ index.html encontrado en Resources/app/ui/"
else
    echo "❌ index.html NO encontrado en Resources/app/ui/"
    echo ""
    echo "   Buscando en otros lugares..."
    find "$APP_PATH" -name "index.html" 2>/dev/null | head -5
fi

# Verificar Info.plist
if [ -f "$APP_PATH/Contents/Info.plist" ]; then
    echo "✅ Info.plist encontrado"
    echo ""
    echo "   Contenido del Info.plist:"
    cat "$APP_PATH/Contents/Info.plist" | grep -A 2 "CFBundleExecutable\|CFBundleIdentifier" | head -6
else
    echo "❌ Info.plist NO encontrado"
fi

echo ""
echo "========================================="
echo "💡 Próximos pasos:"
echo ""
echo "Si index.html NO está en Resources/app/ui/, entonces:"
echo "  1. Los archivos no se están copiando correctamente"
echo "  2. Necesitas revisar el comando --add-data en PyInstaller"
echo ""
echo "Si TODO está correcto pero el .app no funciona:"
echo "  1. Prueba ejecutar el binario directamente:"
echo "     $APP_PATH/Contents/MacOS/OpenPYME_ERP"
echo "  2. Si el binario funciona, el problema es el bundle"
echo "  3. Usa la Solución 5 del documento SOLUCION_APP_BUNDLE.md"

