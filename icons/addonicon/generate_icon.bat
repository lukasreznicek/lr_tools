@echo off
setlocal

set "ASSET_DIR=%~dp0."
rem set "BLENDER_EXE=%~dp0..\..\..\..\..\blender.exe"
set "BLENDER_EXE=C:\Ext1\Blender\Stable\blender.exe"
if not exist "%BLENDER_EXE%" (
	echo Blender executable not found: "%BLENDER_EXE%"
	exit /b 1
)

"%BLENDER_EXE%" --background --factory-startup "%ASSET_DIR%\icon.blend" --python "%ASSET_DIR%\blender_icons_geom.py" -- --output-dir "%ASSET_DIR%"
exit /b %ERRORLEVEL%