; ============================================================
; latex2ocr Inno Setup 安装脚本
; 使用方法: 安装 Inno Setup 后，右键此文件 → Compile
;           或命令行: ISCC.exe setup.iss
; ============================================================

#define MyAppName "latex2ocr"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "shengshimeiyan"
#define MyAppURL "https://github.com/shengshimeiyan/latex2ocr"
#define MyAppExeName "latex2ocr.exe"

[Setup]
; 基本信息
AppId={{8F3C7A2B-1D5E-4A9B-B6C8-2E7F0D4A1C3D}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}

; 安装目录
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}

; 输出
OutputDir=installer_output
OutputBaseFilename=latex2ocr-setup-v{#MyAppVersion}
SetupIconFile=

; 压缩
Compression=lzma2/ultra64
SolidCompression=yes
LZMANumBlockThreads=4

; 权限：最低权限安装（不需要管理员）
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog

; 界面
WizardStyle=modern

; 许可证
LicenseFile=LICENSE

; 卸载
UninstallDisplayName={#MyAppName}
UninstallDisplayIcon={app}\{#MyAppExeName}

; 版本信息（右键 exe → 属性 → 详细信息 可见）
VersionInfoVersion={#MyAppVersion}
VersionInfoCompany={#MyAppPublisher}
VersionInfoDescription=latex2ocr - 轻量级公式 OCR 工具
VersionInfoCopyright=Copyright (c) 2025 {#MyAppPublisher}
VersionInfoProductName={#MyAppName}
VersionInfoProductVersion={#MyAppVersion}

; 其他
DisableProgramGroupPage=yes
DisableWelcomePage=no

[Languages]
Name: "chinese"; MessagesFile: "compiler:Default.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Messages]
; 覆盖英文界面中的关键文字为中文
chinese.WelcomeLabel2=这将安装 {#MyAppName} v{#MyAppVersion} 到您的计算机。%n%n{#MyAppName} 是一款轻量级公式 OCR 工具，支持 DeepSeek / Gemini / GPT / Qwen3-VL 等大模型，一键识别公式图片并转换为 LaTeX 格式。%n%n建议在继续之前关闭其他应用程序。
chinese.SelectDirLabel3=安装程序将把 {#MyAppName} 安装到以下文件夹。
chinese.SelectDirBrowseLabel=如需更改目录，请点击"浏览"。%n%n安装后请勿移动程序目录，否则配置文件会丢失。
chinese.ReadyLabel1=安装程序已准备好将 {#MyAppName} 安装到您的计算机。
chinese.ReadyLabel2a=点击"安装"开始，或点击"返回"修改设置。
chinese.FinishedHeadingLabel=安装完成
chinese.FinishedLabelNoIcons={#MyAppName} 已成功安装到您的计算机。
chinese.FinishedLabel={#MyAppName} 已成功安装到您的计算机。
chinese.ClickFinish=点击"完成"退出安装程序。
chinese.SetupWindowTitle=安装 - {#MyAppName}
chinese.WelcomeWindowTitle=安装 - {#MyAppName}
chinese.SelectDirLabel3=安装程序将把 {#MyAppName} 安装到以下文件夹。

[Tasks]
Name: "desktopicon"; Description: "创建桌面快捷方式(&D)"; GroupDescription: "附加图标:"; Flags: unchecked

[Files]
; 主程序
Source: "dist\latex2ocr.exe"; DestDir: "{app}"; Flags: ignoreversion
; 配置文件（仅当用户尚未修改时覆盖，保护已填写的 API Key）
Source: "dist\config.ini"; DestDir: "{app}"; Flags: onlyifdoesntexist uninsneveruninstall
; 许可证
Source: "LICENSE"; DestDir: "{app}"; Flags: ignoreversion
; README
Source: "README.md"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\卸载 {#MyAppName}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "启动 {#MyAppName}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
; 卸载时清理运行时生成的临时文件
Type: files; Name: "{app}\screenshot.png"
Type: files; Name: "{app}\temp_latex.png"
Type: files; Name: "{app}\temp.png"

[Code]
// 卸载时询问是否保留用户配置（含 API Key）
function InitializeUninstall(): Boolean;
begin
  Result := True;
end;

procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
var
  ConfigPath: string;
begin
  if CurUninstallStep = usPostUninstall then
  begin
    ConfigPath := ExpandConstant('{app}\config.ini');
    if FileExists(ConfigPath) then
    begin
      if MsgBox('是否删除配置文件（含 API Key 等个人信息）？', mbConfirmation, MB_YESNO) = IDYES then
      begin
        DeleteFile(ConfigPath);
      end;
    end;
    // 如果安装目录已空，删除它
    if DirExists(ExpandConstant('{app}')) then
    begin
      DelTree(ExpandConstant('{app}'), True, True, True);
    end;
  end;
end;
