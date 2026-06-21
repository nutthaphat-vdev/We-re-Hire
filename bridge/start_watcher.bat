@echo off
REM start_watcher.bat - launch the Cowork -> Claude Code bridge watcher
REM Run from anywhere; it cd's to the repo root (parent of bridge\).

setlocal
cd /d "%~dp0.."

echo ============================================================
echo  WeHire bridge watcher
echo  repo: %CD%
echo  Drop a filled task packet into bridge\inbox\ to fire a run.
echo  Press Ctrl+C to stop.
echo ============================================================

where py >nul 2>nul
if %errorlevel%==0 (
  py bridge\bridge_runner.py
) else (
  python bridge\bridge_runner.py
)

echo.
echo Watcher exited.
pause
endlocal
