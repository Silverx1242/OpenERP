# Instalación en Mac Intel

Si tienes un Mac Intel (como iMac 2017) y la aplicación ARM64 no funciona, sigue estos pasos:

## Opción 1: Forzar ejecución con Rosetta 2

1. Abre Terminal
2. Navega a la carpeta donde está la aplicación:
   ```bash
   cd ~/Descargas/OpenPYME_ERP-macOS-arm64
   ```
3. Ejecuta con Rosetta 2:
   ```bash
   arch -x86_64 ./OpenPYME_ERP.app/Contents/MacOS/OpenPYME_ERP
   ```

## Opción 2: Compilar localmente para Intel

Si la Opción 1 no funciona, puedes compilar la aplicación localmente en tu Mac Intel:

### Requisitos previos:

1. Instala Python 3.11:
   ```bash
   brew install python@3.11
   ```

2. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   pip install pyinstaller
   ```

3. Compila para Intel:
   ```bash
   python3.11 -m PyInstaller --name="OpenPYME_ERP" \
     --windowed \
     --onedir \
     --icon=assets/icono.icns \
     --add-data="app/ui:app/ui" \
     --add-data="assets:assets" \
     --osx-bundle-identifier="com.openpyme.erp" \
     main.py
   ```

4. La aplicación estará en `dist/OpenPYME_ERP.app`

## Opción 3: Ejecutar desde código fuente

La forma más simple es ejecutar directamente desde el código fuente:

1. Clona o descarga el código fuente del release
2. Instala dependencias:
   ```bash
   pip install -r requirements.txt
   ```
3. Ejecuta:
   ```bash
   python main.py
   ```

## Verificar arquitectura de la aplicación

Para ver qué arquitectura tiene la aplicación:

```bash
file OpenPYME_ERP.app/Contents/MacOS/OpenPYME_ERP
```

Esto mostrará si es `arm64` o `x86_64`.

