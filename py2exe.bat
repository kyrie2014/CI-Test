::echo off
pyinstaller -F Processor.py --hidden-import=pandas._libs.tslibs.timedeltas
pause