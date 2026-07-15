@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ========================================
echo   latex2ocr 一键打包脚本
echo ========================================
echo.

REM 检查 Python：优先使用绝对路径，回退到 PATH 中的 python
set PYTHON=C:\Users\12608\AppData\Local\Programs\Python\Python312\python.exe
if not exist "%PYTHON%" (
    where python >nul 2>&1
    if %errorlevel% neq 0 (
        echo [错误] 未找到 Python，请安装或修改脚本中的 PYTHON 路径
        pause
        exit /b 1
    )
    set PYTHON=python
)

REM 第1步：PyInstaller 打包（使用 spec 文件，保留 excludes/datas 配置）
echo [1/2] PyInstaller 打包中...
"%PYTHON%" -m PyInstaller latex2ocr.spec --noconfirm
if errorlevel 1 (
    echo [错误] PyInstaller 打包失败！
    pause
    exit /b 1
)
echo [1/2] PyInstaller 打包完成。

REM 复制配置文件到 dist
copy /Y config.ini dist\ >nul

REM 第2步：Inno Setup 打包
echo.
echo [2/2] Inno Setup 生成安装包...
where iscc >nul 2>&1
if %errorlevel% neq 0 (
    echo [跳过] Inno Setup (ISCC) 未安装。
    echo        仅生成裸 exe: dist\latex2ocr.exe
    echo.
    echo        如需生成安装包，请安装 Inno Setup:
    echo        https://jrsoftware.org/isdl.php
    echo        安装后重新运行此脚本即可。
    goto :done
)

iscc setup.iss
if errorlevel 1 (
    echo [错误] Inno Setup 打包失败！
    pause
    exit /b 1
)
echo [2/2] Inno Setup 安装包生成完成。

:done
echo.
echo ========================================
echo   打包完成！
echo.
if exist "installer_output\latex2ocr-setup-v1.1.0.exe" (
    echo   安装包: installer_output\latex2ocr-setup-v1.1.0.exe
    echo.
    echo   将此文件发送给用户即可，双击安装，
    echo   不会触发 Windows SmartScreen 拦截。
) else (
    echo   裸 exe: dist\latex2ocr.exe
    echo   配置文件: dist\config.ini
    echo.
    echo   将这两个文件放在同一目录即可使用。
)
echo ========================================
pause
