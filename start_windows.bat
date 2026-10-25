@echo off
cd /d "%~dp0"
py -3 run_demo.py
if errorlevel 1 (
  echo Si no tienes el lanzador py, instala Python 3.10 o superior y usa: python run_demo.py
  pause
)