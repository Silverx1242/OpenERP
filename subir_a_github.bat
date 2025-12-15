@echo off
echo ========================================
echo  Subiendo OpenPYME ERP a GitHub
echo ========================================
echo.

REM Verificar si Git está instalado
git --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Git no esta instalado.
    echo.
    echo Por favor instala Git desde: https://git-scm.com/download/win
    echo O usa GitHub Desktop: https://desktop.github.com/
    echo.
    pause
    exit /b 1
)

echo [OK] Git esta instalado
echo.

REM Inicializar repositorio si no existe
if not exist ".git" (
    echo [1/6] Inicializando repositorio Git...
    git init
    echo [OK] Repositorio inicializado
) else (
    echo [OK] Repositorio Git ya existe
)
echo.

REM Añadir archivos
echo [2/6] Añadiendo archivos al staging...
git add .
echo [OK] Archivos añadidos
echo.

REM Verificar si hay cambios
git diff --cached --quiet
if errorlevel 1 (
    echo [3/6] Creando commit inicial...
    git commit -m "Initial commit - Proyecto OpenPYME ERP listo para GitHub"
    echo [OK] Commit creado
) else (
    echo [INFO] No hay cambios nuevos para commitear
)
echo.

REM Configurar rama main
echo [4/6] Configurando rama main...
git branch -M main
echo [OK] Rama configurada
echo.

REM Verificar si el remote existe
git remote get-url origin >nul 2>&1
if errorlevel 1 (
    echo [5/6] Configurando repositorio remoto...
    echo.
    echo IMPORTANTE: Necesitas crear el repositorio en GitHub primero!
    echo.
    set /p REPO_URL="Ingresa la URL de tu repositorio GitHub (ej: https://github.com/tu-usuario/openpyme-erp.git): "
    git remote add origin %REPO_URL%
    echo [OK] Repositorio remoto configurado
) else (
    echo [OK] Repositorio remoto ya configurado
)
echo.

REM Mostrar información
echo [6/6] Informacion del repositorio:
git remote -v
echo.

REM Preguntar si quiere hacer push
set /p PUSH="¿Quieres subir el código ahora? (S/N): "
if /i "%PUSH%"=="S" (
    echo.
    echo Subiendo código a GitHub...
    git push -u origin main
    if errorlevel 1 (
        echo.
        echo [ERROR] Error al subir el código.
        echo Esto puede ser por:
        echo - Credenciales incorrectas
        echo - El repositorio no existe en GitHub
        echo - Problemas de conexion
        echo.
        echo Ve a INSTRUCCIONES_GITHUB.md para mas ayuda.
    ) else (
        echo.
        echo ========================================
        echo  ¡Codigo subido exitosamente!
        echo ========================================
        echo.
        echo Siguiente paso: Crear un release en GitHub
        echo para que GitHub Actions construya el .app
        echo.
    )
) else (
    echo.
    echo No se subio el codigo. Puedes hacerlo mas tarde con:
    echo   git push -u origin main
)

echo.
pause

