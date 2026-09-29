@echo off
rem Starts OmniRoute, Headroom proxy and claude-mem worker, each in its own window.
rem Double-click to run. Close a window (or press Ctrl+C in it) to stop that tool.
title Claude tools launcher

echo Starting OmniRoute  (port 20128)...
start "OmniRoute" cmd /k omniroute serve --no-open

echo Starting Headroom   (port 8787)...
start "Headroom" cmd /k headroom proxy

echo Starting claude-mem (port 37777)...
start "claude-mem" cmd /k npx --yes claude-mem start

echo.
echo Waiting for the three tools to come up (up to 2 minutes)...
echo.
call :wait "OmniRoute " http://localhost:20128/
call :wait "Headroom  " http://127.0.0.1:8787/health
call :wait "claude-mem" http://127.0.0.1:37777/

echo.
echo Done. Keep the three tool windows open while you use Claude Code.
echo You can close this window.
pause
exit /b

:wait
set /a tries=0
:wait_loop
curl -s -o nul --max-time 3 %2 >nul 2>&1
if not errorlevel 1 (
  echo   [ OK ] %~1 is running
  exit /b
)
set /a tries+=1
if %tries% geq 24 (
  echo   [FAIL] %~1 did not respond - check its window for a red error
  exit /b
)
timeout /t 5 /nobreak >nul
goto wait_loop
