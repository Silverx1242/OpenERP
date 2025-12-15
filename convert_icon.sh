#!/bin/bash
# Script para convertir icono.ico a icono.icns para macOS

echo "🔄 Convirtiendo icono.ico a formato .icns para macOS..."

# Verificar que existe el icono
if [ ! -f "assets/icono.ico" ]; then
    echo "❌ Error: No se encuentra assets/icono.ico"
    exit 1
fi

# Crear directorio temporal para el iconset
ICONSET_DIR="assets/icono.iconset"
rm -rf "$ICONSET_DIR"
mkdir -p "$ICONSET_DIR"

# Convertir ICO a PNG temporal
echo "📸 Convirtiendo ICO a PNG..."
if command -v convert &> /dev/null; then
    # Usar ImageMagick si está disponible
    convert assets/icono.ico -resize 1024x1024 temp_icon.png
else
    # Usar sips (nativo de macOS)
    sips -s format png assets/icono.ico --out temp_icon.png
fi

# Crear todas las resoluciones necesarias
echo "📐 Generando tamaños de icono..."
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

# Limpiar archivo temporal
rm temp_icon.png

# Crear el archivo .icns
echo "🎨 Creando archivo .icns..."
iconutil -c icns "$ICONSET_DIR" -o assets/icono.icns

# Limpiar el directorio temporal
rm -rf "$ICONSET_DIR"

echo "✅ ¡Conversión completada! assets/icono.icns creado."
echo "💡 Ahora puedes usar build.py para crear el ejecutable."

