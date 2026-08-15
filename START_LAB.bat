@echo off
rem ── Fark VFX Lab launcher ─────────────────────────────────────────
rem Double-click me. A black window opens (that's the little server the
rem lab needs) and the lab opens in your browser a moment later.
rem KEEP THIS WINDOW OPEN while you use the lab.
rem CLOSE THIS WINDOW when you're done - that stops the server too.
cd /d "%~dp0"
echo Starting the Fark VFX Lab... the browser opens in a moment.
echo Keep this window open while you work. Close it when you're done.
start "" cmd /c "timeout /t 2 /nobreak >nul & start http://localhost:8085/fark_lab.html"
where python >nul 2>nul && (python -m http.server 8085) || (py -m http.server 8085)
