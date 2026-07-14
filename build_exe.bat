@echo off
chcp 65001 >nul
echo ========================================
echo   latex2ocr 一键打包脚本
echo ========================================
echo.

REM 第1步：PyInstaller 打包
echo [1/3] PyInstaller 打包中...
python -m PyInstaller --name "latex2ocr" --onefile --windowed --add-data "config.ini;." main_v108.py --noconfirm
if errorlevel 1 (
    echo PyInstaller 打包失败！
    pause
    exit /b 1
)
echo PyInstaller 打包完成。

REM 复制 config.ini 到 dist
copy /Y config.ini dist\

REM 第2步：自签名（可选，不能消除 SmartScreen 但标注发布者）
echo.
echo [2/3] 代码签名...
where signtool >nul 2>&1
if %errorlevel%==0 (
    REM 检查是否已有自签名证书
    certutil -store My "latex2ocr-signing" >nul 2>&1
    if %errorlevel% neq 0 (
        echo 创建自签名证书...
        makecert -r -pe -n "CN=shengshimeiyan" -ss My "latex2ocr-signing.cer" >nul 2>&1
        if errorlevel 1 (
            echo makecert 不可用，跳过签名（需安装 Windows SDK）
            goto :skip_sign
        )
    )
    signtool sign /s My /n "shengshimeiyan" /t http://timestamp.digicert.com /fd sha256 "dist\latex2ocr.exe" >nul 2>&1
    if errorlevel 1 (
        echo 签名失败，跳过。
    ) else (
        echo 签名成功。
    )
) else (
    echo signtool 未安装，跳过签名。
)
:skip_sign

REM 第3步：Inno Setup 打包（如果已安装）
echo.
echo [3/3] Inno Setup 打包...
where iscc >nul 2>&1
if %errorlevel%==0 (
    iscc setup.iss
    if errorlevel 1 (
        echo Inno Setup 打包失败！
    ) else (
        echo 安装包已生成到 installer_output\ 目录。
    )
) else (
    echo Inno Setup 未安装，跳过安装包生成。
    echo 仅生成裸 exe: dist\latex2ocr.exe
)

echo.
echo ========================================
echo   打包完成！
echo   - 裸 exe: dist\latex2ocr.exe
echo   - 安装包: installer_output\ (如已安装 Inno Setup)
echo ========================================
pause
