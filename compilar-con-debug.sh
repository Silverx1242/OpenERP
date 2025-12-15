#!/bin/bash
# Compilar con modo debug habilitado para ver errores

echo "🔨 Compilando con modo DEBUG habilitado"
echo "========================================="
echo ""

# Primero hacer backup del main.py original
cp main.py main.py.backup

# Modificar temporalmente main.py para habilitar debug
sed -i.bak 's/webview.start(debug=False)/webview.start(debug=True)/g' main.py

echo "✅ Modo debug habilitado temporalmente"
echo ""

# Ejecutar el build
./build-macos-correcto.sh

# Restaurar el original
mv main.py.backup main.py
rm -f main.py.bak

echo ""
echo "💡 La app compilada tiene debug=True"
echo "   Esto abrirá las herramientas de desarrollador para ver errores"

