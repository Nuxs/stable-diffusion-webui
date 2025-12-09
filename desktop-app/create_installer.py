#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
创建安装程序脚本
使用 Inno Setup 创建 Windows 安装程序
"""

import os
import sys
from pathlib import Path


def create_iss_script():
    """创建 Inno Setup 脚本"""
    project_root = Path(__file__).parent
    dist_dir = project_root / "dist"
    exe_file = dist_dir / "StableDiffusionWebUI.exe"
    
    if not exe_file.exists():
        print("错误: 找不到可执行文件")
        print("请先运行 build.py 打包应用")
        sys.exit(1)
    
    iss_content = f"""; Inno Setup 安装脚本
; 用于创建 Stable Diffusion WebUI 安装程序

#define AppName "Stable Diffusion WebUI"
#define AppVersion "1.0.0"
#define AppPublisher "SD-WebUI"
#define AppURL "https://github.com/AUTOMATIC1111/stable-diffusion-webui"
#define AppExeName "StableDiffusionWebUI.exe"

[Setup]
AppId={{{{A1B2C3D4-E5F6-7890-ABCD-EF1234567890}}}}
AppName={{#AppName}}
AppVersion={{#AppVersion}}
AppPublisher={{#AppPublisher}}
AppPublisherURL={{#AppURL}}
AppSupportURL={{#AppURL}}
AppUpdatesURL={{#AppURL}}
DefaultDirName={{autopf}}\\{{#AppName}}
DefaultGroupName={{#AppName}}
AllowNoIcons=yes
LicenseFile=
OutputDir=installer
OutputBaseFilename=StableDiffusionWebUI-Setup
SetupIconFile=resources\\icon.ico
Compression=lzma
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin

[Languages]
Name: "chinesesimp"; MessagesFile: "compiler:Languages\\ChineseSimplified.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{{cm:CreateDesktopIcon}}"; GroupDescription: "{{cm:AdditionalIcons}}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{{cm:CreateQuickLaunchIcon}}"; GroupDescription: "{{cm:AdditionalIcons}}"; Flags: unchecked; OnlyBelowVersion: 6.1

[Files]
Source: "dist\\StableDiffusionWebUI.exe"; DestDir: "{{app}}"; Flags: ignoreversion
Source: "resources\\*"; DestDir: "{{app}}\\resources"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{{group}}\\{{#AppName}}"; Filename: "{{app}}\\{{#AppExeName}}"
Name: "{{group}}\\{{cm:UninstallProgram,{{#AppName}}}}"; Filename: "{{uninstallexe}}"
Name: "{{autodesktop}}\\{{#AppName}}"; Filename: "{{app}}\\{{#AppExeName}}"; Tasks: desktopicon
Name: "{{userappdata}}\\Microsoft\\Internet Explorer\\Quick Launch\\{{#AppName}}"; Filename: "{{app}}\\{{#AppExeName}}"; Tasks: quicklaunchicon

[Run]
Filename: "{{app}}\\{{#AppExeName}}"; Description: "{{cm:LaunchProgram,{{#StringChange({{#AppName}}, '&', '&&')}}}}}"; Flags: nowait postinstall skipifsilent
"""
    
    iss_file = project_root / "installer.iss"
    with open(iss_file, 'w', encoding='utf-8') as f:
        f.write(iss_content)
    
    print(f"Inno Setup 脚本已创建: {iss_file}")
    print("\n要创建安装程序，请:")
    print("1. 安装 Inno Setup: https://jrsoftware.org/isdl.php")
    print(f"2. 打开 {iss_file}")
    print("3. 在 Inno Setup Compiler 中点击 'Build' -> 'Compile'")


if __name__ == "__main__":
    create_iss_script()


