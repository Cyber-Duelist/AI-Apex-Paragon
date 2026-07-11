@echo off
title Envoy Omni-Modal Launcher

echo ===================================================
echo   Starting ENVOY & ENTROPY AI
echo ===================================================
echo.

echo [1/2] Starting backend AI server (main.py)...
start "Entropy Backend" cmd /c "python main.py"

echo Waiting for backend to initialize...
timeout /t 3 /nobreak >nul

echo.
echo [2/2] Starting UI Dashboard (envoy.py)...
python envoy.py

echo.
echo ENVOY closed. Shutting down backend...
taskkill /FI "WINDOWTITLE eq Entropy Backend" /F /T >nul 2>&1

echo Done!
