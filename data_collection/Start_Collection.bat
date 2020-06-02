@ECHO off

:top

REM Run the code.
python run_once.py

REM Wait for 10 minutes.
TIMEOUT 600

REM Loop back to the top.

GOTO :top