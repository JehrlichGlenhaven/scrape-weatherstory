@echo off
echo Starting GSC Weather Channel...

REM Start a tiny web server in the background so the radar and weather API work correctly
start /min "" python -m http.server 8080 --bind 127.0.0.1

REM Wait a moment for the server to start
timeout /t 2 /nobreak >nul

REM Open Chrome in full-screen kiosk mode
start chrome --kiosk http://127.0.0.1:8080/index.html

REM Optional: to open in a normal full-screen window instead of kiosk mode, use this line instead:
REM start chrome --start-fullscreen http://127.0.0.1:8080/index.html
