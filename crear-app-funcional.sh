#!/bin/bash
# Script para crear un .app funcional desde el ejecutable que ya funciona

echo "🔧 Creando .app funcional desde el ejecutable"
echo "=============================================="
echo ""

BUNDLE_PATH="dist/OpenPYME_ERP.app"
EXECUTABLE_PATH="$BUNDLE_PATH/Contents/MacOS/OpenPYME_ERP"

if [ ! -f "$EXECUTABLE_PATH" ]; then
    echo "❌ Error: No se encuentra el ejecutable en $EXECUTABLE_PATH"
    echo "   Asegúrate de haber compilado primero"
    exit 1
fi

echo "✅ Ejecutable encontrado"
echo ""

# Crear estructura de bundle si no existe
mkdir -p "$BUNDLE_PATH/Contents/MacOS"
mkdir -p "$BUNDLE_PATH/Contents/Resources"
mkdir -p "$BUNDLE_PATH/Contents/Resources/app/ui"

# Copiar archivos UI si no están
if [ ! -f "$BUNDLE_PATH/Contents/Resources/app/ui/index.html" ]; then
    echo "📦 Copiando archivos UI..."
    if [ -d "app/ui" ]; then
        cp -R app/ui/* "$BUNDLE_PATH/Contents/Resources/app/ui/"
        echo "✅ Archivos UI copiados"
    else
        echo "⚠️  No se encontró app/ui/, busca manualmente dónde está"
    fi
fi

# Crear Info.plist
echo "📝 Creando Info.plist..."
cat > "$BUNDLE_PATH/Contents/Info.plist" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleDevelopmentRegion</key>
    <string>en</string>
    <key>CFBundleExecutable</key>
    <string>OpenPYME_ERP</string>
    <key>CFBundleIconFile</key>
    <string>icon</string>
    <key>CFBundleIdentifier</key>
    <string>com.openpyme.erp</string>
    <key>CFBundleInfoDictionaryVersion</key>
    <string>6.0</string>
    <key>CFBundleName</key>
    <string>OpenPYME ERP</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0</string>
    <key>CFBundleVersion</key>
    <string>1</string>
    <key>LSMinimumSystemVersion</key>
    <string>10.13</string>
    <key>NSHighResolutionCapable</key>
    <true/>
    <key>NSRequiresAquaSystemAppearance</key>
    <false/>
</dict>
</plist>
EOF

echo "✅ Info.plist creado"
echo ""

# Copiar icono si existe
if [ -f "assets/icono.icns" ]; then
    cp assets/icono.icns "$BUNDLE_PATH/Contents/Resources/icon.icns"
    echo "✅ Icono copiado"
fi

# Asegurar que el ejecutable tiene permisos
chmod +x "$EXECUTABLE_PATH"

echo ""
echo "=============================================="
echo "✅ .app creado/corregido"
echo ""
echo "📦 Ubicación: $BUNDLE_PATH"
echo ""
echo "💡 Próximos pasos:"
echo "   1. Prueba abrir: open $BUNDLE_PATH"
echo "   2. Si funciona, puedes arrastrarlo a Aplicaciones"
echo ""
echo "🔍 Si aún no funciona, ejecuta:"
echo "   $EXECUTABLE_PATH"
echo "   (Esto mostrará los errores en Terminal)"

