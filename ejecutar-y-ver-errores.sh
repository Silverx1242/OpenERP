#!/bin/bash
# Script para ejecutar la app y ver errores en Terminal

echo "🔍 Ejecutando aplicación y mostrando errores..."
echo "================================================"
echo ""

APP_EXEC="dist/OpenPYME_ERP.app/Contents/MacOS/OpenPYME_ERP"

if [ ! -f "$APP_EXEC" ]; then
    echo "❌ Error: No se encuentra el ejecutable"
    echo "   Buscando en: $APP_EXEC"
    echo ""
    echo "💡 Asegúrate de haber compilado primero con:"
    echo "   ./build-macos-correcto.sh"
    exit 1
fi

echo "📱 Ejecutando: $APP_EXEC"
echo ""
echo "⚠️  Cualquier error aparecerá aquí abajo:"
echo "================================================"
echo ""

# Ejecutar y capturar tanto stdout como stderr
"$APP_EXEC" 2>&1

EXIT_CODE=$?

echo ""
echo "================================================"
if [ $EXIT_CODE -eq 0 ]; then
    echo "✅ La aplicación terminó normalmente"
else
    echo "❌ La aplicación terminó con código de error: $EXIT_CODE"
    echo ""
    echo "💡 Revisa los mensajes de error arriba para más detalles"
fi

