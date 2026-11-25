@echo off
title EVENTFLOW - Smart Event Management System
cd /d "%~dp0"
echo ================================================================
echo   Starting EVENTFLOW - Smart Event Management System
echo   Powered by AVL Interval Trees & SQLite
echo ================================================================
echo.
echo Opening in your default browser at http://localhost:8501 ...
echo.
python -m streamlit run app.py
pause
