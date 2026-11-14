@echo off
rem Atorapp, modo exploracion (Fase 3F). Doble clic para abrir la app.
rem Estimacion experimental, no verificada con NVDA. Fuera del estudio.
setlocal
cd /d "%~dp0"
title Atorapp - modo exploracion

if not exist ".venv\Scripts\python.exe" (
    echo Primera vez: creando el entorno de Python 3.12 en .venv ...
    py -3.12 -m venv .venv
    if errorlevel 1 goto :error_python
)

rem Instala dependencias solo si requirements.txt cambio desde la ultima vez.
fc /b requirements.txt ".venv\requisitos-instalados.txt" >nul 2>&1
if errorlevel 1 (
    echo Instalando dependencias ...
    ".venv\Scripts\python.exe" -m pip install --disable-pip-version-check -q -r requirements.txt
    if errorlevel 1 goto :error_pip
    ".venv\Scripts\python.exe" -m playwright install chromium
    if errorlevel 1 goto :error_pip
    copy /y requirements.txt ".venv\requisitos-instalados.txt" >nul
)

echo Abriendo Atorapp ...
".venv\Scripts\python.exe" -m app %*
if errorlevel 1 goto :error_app
exit /b 0

:error_python
echo.
echo No se pudo crear el entorno. Instala Python 3.12 (con el lanzador "py") y vuelve a intentar.
pause
exit /b 1

:error_pip
echo.
echo No se pudieron instalar las dependencias. Revisa tu conexion a internet y vuelve a intentar.
pause
exit /b 1

:error_app
echo.
echo Atorapp se cerro con un error. El detalle esta arriba.
pause
exit /b 1
