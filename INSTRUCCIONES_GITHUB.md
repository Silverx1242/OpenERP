# 📤 Instrucciones para Subir el Código a GitHub

## Paso 1: Instalar Git (si no lo tienes)

### Opción A: Instalar Git para Windows
1. Descarga Git desde: https://git-scm.com/download/win
2. Ejecuta el instalador y sigue las instrucciones
3. **Importante**: Durante la instalación, selecciona "Git from the command line and also from 3rd-party software"
4. Reinicia tu terminal después de la instalación

### Opción B: Usar GitHub Desktop (más fácil)
1. Descarga GitHub Desktop: https://desktop.github.com/
2. Instálalo y configúralo con tu cuenta de GitHub
3. Puedes usar la interfaz gráfica en lugar de la terminal

## Paso 2: Crear un Repositorio en GitHub

1. Ve a https://github.com e inicia sesión (o crea una cuenta)
2. Haz clic en el botón **"+"** (arriba a la derecha) → **"New repository"**
3. Configura el repositorio:
   - **Repository name**: `openpyme-erp` (o el nombre que prefieras)
   - **Description**: "Sistema ERP/CRM para pequeñas y medianas empresas"
   - **Visibility**: Público o Privado (tu elección)
   - **NO marques** "Initialize this repository with a README" (ya tenemos uno)
   - **NO selecciones** ningún .gitignore o license (ya los tenemos)
4. Haz clic en **"Create repository"**
5. **Copia la URL** del repositorio (algo como: `https://github.com/tu-usuario/openpyme-erp.git`)

## Paso 3: Subir el Código (Usando Git en Terminal)

Abre PowerShell o CMD en la carpeta del proyecto y ejecuta estos comandos:

### 3.1 Inicializar el repositorio Git
```bash
git init
```

### 3.2 Añadir todos los archivos
```bash
git add .
```

### 3.3 Hacer el primer commit
```bash
git commit -m "Initial commit - Proyecto OpenPYME ERP listo para GitHub"
```

### 3.4 Renombrar la rama principal (si es necesario)
```bash
git branch -M main
```

### 3.5 Añadir el repositorio remoto de GitHub
```bash
git remote add origin https://github.com/TU-USUARIO/openpyme-erp.git
```
**⚠️ IMPORTANTE**: Reemplaza `TU-USUARIO` y `openpyme-erp` con tu usuario y nombre de repositorio reales.

### 3.6 Subir el código
```bash
git push -u origin main
```

Si te pide credenciales:
- **Usuario**: Tu nombre de usuario de GitHub
- **Contraseña**: Necesitas un **Personal Access Token** (no tu contraseña normal)
  - Ve a: https://github.com/settings/tokens
  - Genera un nuevo token con permisos `repo`
  - Úsalo como contraseña

## Paso 4: Usar GitHub Desktop (Alternativa más Fácil)

Si instalaste GitHub Desktop:

1. Abre GitHub Desktop
2. File → Add Local Repository
3. Selecciona la carpeta `C:\Users\Silverx\Desktop\Consultoria`
4. Haz clic en "Publish repository"
5. Selecciona tu cuenta de GitHub y el nombre del repositorio
6. Haz clic en "Publish repository"

## Paso 5: Verificar que Todo Funciona

1. Ve a tu repositorio en GitHub: `https://github.com/tu-usuario/openpyme-erp`
2. Deberías ver todos los archivos subidos
3. El workflow de GitHub Actions estará disponible en la pestaña "Actions"

## Paso 6: Crear un Release con el .app de macOS

Para que GitHub Actions construya automáticamente el ejecutable .app:

### Opción A: Desde GitHub
1. Ve a tu repositorio en GitHub
2. Haz clic en "Releases" → "Create a new release"
3. Tag version: `v1.0.0`
4. Release title: `v1.0.0 - Primera versión`
5. Describe los cambios
6. Publica el release

### Opción B: Desde Terminal
```bash
git tag v1.0.0
git push origin v1.0.0
```

Luego ve a la pestaña "Actions" en GitHub y verás el workflow ejecutándose. Cuando termine, los artefactos estarán disponibles en la sección de Releases.

## 🆘 Solución de Problemas

### Error: "git no se reconoce"
- Git no está instalado. Ve al Paso 1.

### Error: "fatal: not a git repository"
- Ejecuta `git init` primero

### Error: "authentication failed"
- Usa un Personal Access Token en lugar de tu contraseña
- O configura SSH keys (más avanzado)

### Error: "refusing to merge unrelated histories"
- Si el repositorio de GitHub tiene archivos iniciales:
  ```bash
  git pull origin main --allow-unrelated-histories
  git push -u origin main
  ```

## 📝 Notas Importantes

- El `.gitignore` ya está configurado para ignorar archivos innecesarios
- La carpeta `Consultoria - EXE/` no se subirá (está en .gitignore)
- Los archivos `.db` (base de datos) tampoco se subirán
- El workflow de GitHub Actions solo funciona en macOS runners (gratis)

¡Listo! Tu código debería estar en GitHub ahora. 🎉

