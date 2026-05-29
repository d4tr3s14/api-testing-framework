# Ejecuta la suite completa y abre el dashboard de Allure (Windows / PowerShell).
$ErrorActionPreference = "Stop"
Set-Location (Join-Path $PSScriptRoot "..")

Write-Host "`n[1/2] Ejecutando suite de pruebas de API..." -ForegroundColor Cyan
python -m pytest --alluredir=allure-results

Write-Host "`n[2/2] Abriendo dashboard de Allure..." -ForegroundColor Cyan
$allureCmd = $null
foreach ($c in @(
    "$env:APPDATA\npm\allure.cmd",
    "$env:ProgramData\chocolatey\bin\allure.cmd",
    "$env:USERPROFILE\scoop\shims\allure.cmd"
)) {
    if (Test-Path $c) { $allureCmd = $c; break }
}

if ($allureCmd) {
    # Invocar vía cmd.exe: evita problemas del perfil de PowerShell con el
    # operador & sobre archivos .cmd, y maneja rutas con espacios.
    & cmd.exe /d /s /c """$allureCmd"" serve allure-results"
} else {
    Write-Host "`nAllure CLI no se encontro. Instalalo con:" -ForegroundColor Yellow
    Write-Host "  npm install -g allure-commandline" -ForegroundColor White
}
