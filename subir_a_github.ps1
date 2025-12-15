# Script para subir OpenPYME ERP a GitHub
Write-Host "========================================" -ForegroundColor Cyan
Write-Host " Subiendo OpenPYME ERP a GitHub" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar si Git está instalado
try {
    $gitVersion = git --version 2>$null
    Write-Host "[OK] Git está instalado: $gitVersion" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Git no está instalado." -ForegroundColor Red
    Write-Host ""
    Write-Host "Por favor instala Git desde: https://git-scm.com/download/win" -ForegroundColor Yellow
    Write-Host "O usa GitHub Desktop: https://desktop.github.com/" -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Presiona Enter para salir"
    exit 1
}

Write-Host ""

# Inicializar repositorio si no existe
if (-not (Test-Path ".git")) {
    Write-Host "[1/6] Inicializando repositorio Git..." -ForegroundColor Yellow
    git init
    Write-Host "[OK] Repositorio inicializado" -ForegroundColor Green
} else {
    Write-Host "[OK] Repositorio Git ya existe" -ForegroundColor Green
}
Write-Host ""

# Añadir archivos
Write-Host "[2/6] Añadiendo archivos al staging..." -ForegroundColor Yellow
git add .
Write-Host "[OK] Archivos añadidos" -ForegroundColor Green
Write-Host ""

# Verificar si hay cambios
$status = git status --porcelain
if ($status) {
    Write-Host "[3/6] Creando commit inicial..." -ForegroundColor Yellow
    git commit -m "Initial commit - Proyecto OpenPYME ERP listo para GitHub"
    Write-Host "[OK] Commit creado" -ForegroundColor Green
} else {
    Write-Host "[INFO] No hay cambios nuevos para commitear" -ForegroundColor Blue
}
Write-Host ""

# Configurar rama main
Write-Host "[4/6] Configurando rama main..." -ForegroundColor Yellow
git branch -M main
Write-Host "[OK] Rama configurada" -ForegroundColor Green
Write-Host ""

# Verificar si el remote existe
try {
    $remote = git remote get-url origin 2>$null
    Write-Host "[OK] Repositorio remoto ya configurado: $remote" -ForegroundColor Green
} catch {
    Write-Host "[5/6] Configurando repositorio remoto..." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "IMPORTANTE: Necesitas crear el repositorio en GitHub primero!" -ForegroundColor Yellow
    Write-Host "Ve a: https://github.com/new" -ForegroundColor Yellow
    Write-Host ""
    $repoUrl = Read-Host "Ingresa la URL de tu repositorio GitHub (ej: https://github.com/tu-usuario/openpyme-erp.git)"
    if ($repoUrl) {
        git remote add origin $repoUrl
        Write-Host "[OK] Repositorio remoto configurado" -ForegroundColor Green
    }
}
Write-Host ""

# Mostrar información
Write-Host "[6/6] Información del repositorio:" -ForegroundColor Yellow
git remote -v
Write-Host ""

# Preguntar si quiere hacer push
$push = Read-Host "¿Quieres subir el código ahora? (S/N)"
if ($push -eq "S" -or $push -eq "s") {
    Write-Host ""
    Write-Host "Subiendo código a GitHub..." -ForegroundColor Yellow
    git push -u origin main
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "========================================" -ForegroundColor Green
        Write-Host " ¡Código subido exitosamente!" -ForegroundColor Green
        Write-Host "========================================" -ForegroundColor Green
        Write-Host ""
        Write-Host "Siguiente paso: Crear un release en GitHub" -ForegroundColor Cyan
        Write-Host "para que GitHub Actions construya el .app" -ForegroundColor Cyan
        Write-Host ""
    } else {
        Write-Host ""
        Write-Host "[ERROR] Error al subir el código." -ForegroundColor Red
        Write-Host "Esto puede ser por:" -ForegroundColor Yellow
        Write-Host "- Credenciales incorrectas" -ForegroundColor Yellow
        Write-Host "- El repositorio no existe en GitHub" -ForegroundColor Yellow
        Write-Host "- Problemas de conexión" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "Ve a INSTRUCCIONES_GITHUB.md para más ayuda." -ForegroundColor Cyan
    }
} else {
    Write-Host ""
    Write-Host "No se subió el código. Puedes hacerlo más tarde con:" -ForegroundColor Blue
    Write-Host "  git push -u origin main" -ForegroundColor Gray
}

Write-Host ""
Read-Host "Presiona Enter para salir"

