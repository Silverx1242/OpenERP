# Guía de Contribución

¡Gracias por tu interés en contribuir a OpenPYME ERP!

## Cómo Contribuir

### Reportar Bugs

Si encuentras un bug, por favor:

1. Verifica que no haya un issue abierto ya reportando el mismo problema
2. Crea un nuevo issue con:
   - Descripción clara del problema
   - Pasos para reproducir
   - Comportamiento esperado vs comportamiento actual
   - Información del sistema (OS, versión de Python, etc.)

### Sugerir Mejoras

Las sugerencias de nuevas características son bienvenidas:

1. Abre un issue con la etiqueta "feature request"
2. Describe claramente la funcionalidad propuesta
3. Explica por qué sería útil para los usuarios

### Contribuir Código

1. **Fork el repositorio**
2. **Crea una rama** para tu feature o fix:
   ```bash
   git checkout -b feature/mi-nueva-feature
   ```
3. **Haz tus cambios** siguiendo las convenciones del proyecto
4. **Prueba tus cambios** localmente
5. **Commit** con mensajes descriptivos:
   ```bash
   git commit -m "Añade: descripción de los cambios"
   ```
6. **Push** a tu fork:
   ```bash
   git push origin feature/mi-nueva-feature
   ```
7. **Abre un Pull Request** con una descripción clara de los cambios

### Convenciones de Código

- Usa nombres descriptivos para variables y funciones
- Añade comentarios cuando el código no sea obvio
- Sigue el estilo de código existente (PEP 8 para Python)
- Asegúrate de que el código funcione en Windows, macOS y Linux

### Estructura del Proyecto

- `app/` - Módulos principales de la aplicación
  - `database.py` - Gestión de base de datos
  - `excel_export.py` - Exportación a Excel
  - `ui/` - Interfaz web (HTML/CSS/JS)
- `assets/` - Recursos estáticos (iconos, etc.)
- `main.py` - Punto de entrada principal

## Preguntas

Si tienes preguntas, abre un issue o contacta a los maintainers.

¡Gracias por ayudar a mejorar OpenPYME ERP!

