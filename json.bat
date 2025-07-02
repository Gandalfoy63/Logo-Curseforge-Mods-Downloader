@echo off
setlocal enabledelayedexpansion

set "OUTPUT=icons.json"
set "FOLDER=mod_logos"
set "TEMPFILE=icons_temp.txt"

REM Clear temp file
> "%TEMPFILE%" echo.

REM Step 1: Find image files and save to temp file
echo 🔍 Scanning %FOLDER% for image files...
for %%F in (%FOLDER%\*.png %FOLDER%\*.jpg %FOLDER%\*.jpeg %FOLDER%\*.gif %FOLDER%\*.webp) do (
    set "filename=%%~nxF"
    echo Found: !filename!
    echo "!filename!" >> "%TEMPFILE%"
)

REM Count valid lines
set /a COUNT=0
for /f %%L in ('type "%TEMPFILE%"') do set /a COUNT+=1

REM Step 2: Write JSON file
> "%OUTPUT%" echo [

set /a LINE=0
for /f "delims=" %%L in (%TEMPFILE%) do (
    set /a LINE+=1
    if !LINE! lss %COUNT% (
        >> "%OUTPUT%" echo     %%L,
    ) else (
        >> "%OUTPUT%" echo     %%L
    )
)

>> "%OUTPUT%" echo ]

REM Cleanup
del "%TEMPFILE%"

echo.
echo ✅ Done: %OUTPUT% created with !COUNT! entries.
echo.
pause
