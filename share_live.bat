@echo off
title CloudDedup - Live Public Tunnel
echo ========================================================
echo        Sharing CloudDedup on the Public Internet
echo ========================================================
echo.
echo Make sure your app is running first (via run_app.bat).
echo Generating live public link...
echo.
cloudflared tunnel --url http://127.0.0.1:5000
pause
