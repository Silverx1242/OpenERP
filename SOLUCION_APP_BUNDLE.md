# Solución: El ejecutable funciona pero el .app no

## El problema

Si el ejecutable Unix funciona pero el .app no, el problema está en cómo PyInstaller estructura el bundle.

## Solución 1: Usar el ejecutable Unix directamente (Temporal)

El ejecutable Unix que funciona está en:
```
dist/OpenPYME_ERP.app/Contents/MacOS/OpenPYME_ERP
```

Puedes ejecutarlo directamente:
```bash
dist/OpenPYME_ERP.app/Contents/MacOS/OpenPYME_ERP
```

O crear un alias/script que lo ejecute.

## Solución 2: Compilar con --onedir (Recomendado)

El problema puede ser que está usando `--onedir` pero necesita una configuración diferente. Prueba compilar así:

```bash
# Limpiar compilación anterior
rm -rf build dist *.spec

# Compilar con configuración específica
pyinstaller --name="OpenPYME_ERP" \
  --windowed \
  --noconfirm \
  --onedir \
  --icon=assets/icono.icns \
  --add-data="app/ui:app/ui" \
  --add-data="assets:assets" \
  --osx-bundle-identifier="com.openpyme.erp" \
  --noconsole \
  --clean \
  main.py
```

## Solución 3: Verificar estructura del .app

Verifica que los archivos estén en el lugar correcto:

```bash
# Ver estructura
ls -la dist/OpenPYME_ERP.app/Contents/

# Deberías ver:
# - MacOS/ (con el ejecutable)
# - Resources/ (con app/ui/)

# Verificar que app/ui está en Resources
ls -la dist/OpenPYME_ERP.app/Contents/Resources/app/ui/index.html
```

Si los archivos NO están en Resources, ese es el problema.

## Solución 4: Compilar con --onefile y luego convertir a .app

Otra opción es compilar como un solo archivo y luego crear el bundle manualmente, pero esto es más complicado.

## Solución 5: Usar un script wrapper

Crea un script que ejecute el binario directamente y envuélvelo en un .app:

1. Crear un script `OpenPYME_ERP.sh`:
```bash
#!/bin/bash
cd "$(dirname "$0")"
exec ./OpenPYME_ERP.app/Contents/MacOS/OpenPYME_ERP
```

2. Dar permisos:
```bash
chmod +x OpenPYME_ERP.sh
```

3. Crear un .app que ejecute este script usando Automator o Platypus.

## Solución 6: Verificar Info.plist

El Info.plist del .app puede estar mal configurado. Verifica:

```bash
cat dist/OpenPYME_ERP.app/Contents/Info.plist
```

Debería tener:
- CFBundleExecutable: OpenPYME_ERP
- CFBundleIdentifier: com.openpyme.erp

## Solución rápida: Crear un alias del ejecutable

Mientras solucionas el .app, puedes crear un script que ejecute el binario:

```bash
# Crear script
cat > ~/Desktop/OpenPYME_ERP.sh << 'EOF'
#!/bin/bash
cd ~/Downloads/OpenERP-main/dist/OpenPYME_ERP.app/Contents/MacOS
./OpenPYME_ERP
EOF

chmod +x ~/Desktop/OpenPYME_ERP.sh
```

Luego puedes ejecutar ese script o arrastrarlo al Dock.

## Recomendación

Primero verifica la estructura (Solución 3). Si los archivos NO están en Resources, entonces el problema es cómo PyInstaller está empaquetando. En ese caso, necesitas asegurarte de que `--add-data` esté funcionando correctamente.

