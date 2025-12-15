# OpenPYME ERP/CRM

Sistema de gestión empresarial (ERP/CRM) para pequeñas y medianas empresas, desarrollado con Python y una interfaz web moderna.

## 🚀 Características

- **Gestión de Inventario**: Control completo de productos, stock, proveedores y materias primas
- **Bill of Materials (BOM)**: Gestión de listas de materiales y cálculo de producción
- **Planificación de Producción (MRP)**: Cálculo automático de productos fabricables según inventario
- **Gestión Financiera**: Registro de ingresos, costos y categorización de gastos
- **Ventas**: Historial completo de ventas con seguimiento en tiempo real
- **Business Intelligence**: Dashboard con KPIs, métricas financieras y análisis de productos
- **Exportación a Excel**: Generación de reportes y exportación de datos completos
- **Integración con Google Sheets**: Sincronización opcional con Google Sheets

## 📋 Requisitos

- Python 3.8 o superior
- Sistema operativo: Windows, macOS o Linux

## 🛠️ Instalación

### Instalación desde código fuente

1. Clona el repositorio:
```bash
git clone https://github.com/Silverx1242/OpenERP.git
cd OpenERP
```

2. Crea un entorno virtual (recomendado):
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

3. Instala las dependencias:
```bash
pip install -r requirements.txt
```

4. Ejecuta la aplicación:
```bash
python main.py
```

## 📦 Descarga de ejecutables

Puedes descargar ejecutables pre-construidos desde la sección [Releases](https://github.com/Silverx1242/OpenERP/releases).

### macOS
- Descarga el archivo `.dmg` o `.app.zip` desde los releases
- Para `.dmg`: Abre el archivo y arrastra la aplicación a la carpeta Aplicaciones
- Para `.app.zip`: Descomprime y arrastra `OpenPYME_ERP.app` a la carpeta Aplicaciones

## 🔧 Configuración

### Base de Datos

La aplicación utiliza SQLite como base de datos local. El archivo `erp_data.db` se crea automáticamente en el directorio de ejecución la primera vez que se inicia la aplicación.

### Integración con Google Sheets (Opcional)

Para habilitar la sincronización con Google Sheets:

1. Ve a [Google Cloud Console](https://console.cloud.google.com/)
2. Crea un nuevo proyecto
3. Habilita las APIs de Google Sheets y Google Drive
4. Crea una cuenta de servicio (Service Account)
5. Descarga el archivo JSON de credenciales
6. Guárdalo como `service_account.json` en la raíz del proyecto
7. Comparte tu Google Sheet con el email de la cuenta de servicio

## 📖 Uso

### Gestión de Inventario

- **Añadir Productos**: Navega a "Inventario" y completa el formulario con los datos del producto
- **Tipos de Producto**:
  - `final`: Productos terminados para venta
  - `hijo`: Materias primas/insumos
  - `padre`: Sub-ensamblajes
  - `otro`: Otros gastos o categorías

### Bill of Materials (BOM)

- Define las listas de materiales para productos compuestos
- El sistema calcula automáticamente el costo total basado en los componentes
- Utiliza el cálculo de producción (MRP) para saber cuántos productos puedes fabricar

### Finanzas

- Registra ingresos y costos
- Categoriza los costos para mejor análisis
- Visualiza resúmenes financieros en el dashboard

### Exportación de Datos

- Utiliza el botón "Exportar a Excel" para generar un archivo completo con todas las secciones
- Los archivos se guardan en:
  - Windows/Linux: Directorio actual
  - macOS (desde .app): `~/Documents/OpenPYME_ERP/`

## 🏗️ Construcción desde código fuente

### macOS

Para construir un ejecutable `.app` en macOS:

```bash
# Instalar dependencias de construcción
pip install pyinstaller

# Convertir icono a formato .icns (si es necesario)
# Opción 1: Usar iconutil (requiere .iconset)
# Opción 2: Usar convert (ImageMagick)

# Construir la aplicación
pyinstaller --name="OpenPYME_ERP" \
  --windowed \
  --onedir \
  --icon=assets/icono.icns \
  --add-data="app/ui:app/ui" \
  --add-data="assets:assets" \
  --osx-bundle-identifier="com.openpyme.erp" \
  main.py
```

### GitHub Actions

El repositorio incluye un workflow de GitHub Actions que construye automáticamente la aplicación para macOS cuando se crea un tag de release:

```bash
git tag v1.0.0
git push origin v1.0.0
```

El workflow se ejecutará automáticamente y generará los artefactos en la sección de Actions.

## 📁 Estructura del Proyecto

```
openpyme-erp/
├── app/
│   ├── __init__.py
│   ├── database.py          # Gestión de base de datos SQLite
│   ├── excel_export.py      # Exportación a Excel
│   ├── g_sheets.py          # Integración con Google Sheets
│   └── ui/
│       └── index.html       # Interfaz web
├── assets/
│   ├── icono.ico           # Icono de la aplicación (Windows)
│   └── icono.icns          # Icono de la aplicación (macOS)
├── .github/
│   └── workflows/
│       └── build-macos.yml  # Workflow para construir .app de macOS
├── main.py                 # Punto de entrada principal
├── requirements.txt        # Dependencias del proyecto
├── .gitignore             # Archivos ignorados por Git
└── README.md              # Este archivo
```

## 🤝 Contribuir

Las contribuciones son bienvenidas. Por favor:

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📝 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo LICENSE para más detalles.

## 🙏 Agradecimientos

- [pywebview](https://github.com/r0x0r/pywebview) - Framework para interfaces web nativas
- [openpyxl](https://openpyxl.readthedocs.io/) - Manipulación de archivos Excel
- [Tailwind CSS](https://tailwindcss.com/) - Framework CSS utilitario
- [Chart.js](https://www.chartjs.org/) - Gráficos interactivos

## 📧 Contacto

Para preguntas o sugerencias, abre un issue en el repositorio.

---

Desarrollado con ❤️ para PyMEs

