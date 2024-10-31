@echo off
setlocal enabledelayedexpansion

:: 날짜 형식 설정 (YYYY-MM-DD)
set "today=%date:~0,4%-%date:~5,2%-%date:~8,2%"

:: 로그 파일 이름 설정
set "logfile=D:\log\%today%.log"

:: Python 스크립트 실행 및 로그 저장
C:\Users\logger\AppData\Local\Microsoft\WindowsApps\pythonw.exe C:\Users\logger\Codes\LoudnessLogging\main.py > "!logfile!" 2>&1