#!/usr/bin/env python3
"""
YouTube下载器安装脚本
自动检查和安装依赖项
"""

import sys
import subprocess
import os
import platform
from pathlib import Path


def check_python_version():
    """检查Python版本"""
    print("检查Python版本...")
    if sys.version_info < (3, 7):
        print("❌ 错误: 需要Python 3.7或更高版本")
        print(f"当前版本: {sys.version}")
        return False
    print(f"✅ Python版本: {sys.version}")
    return True


def check_pip():
    """检查pip是否可用"""
    print("检查pip...")
    try:
        import pip
        print("✅ pip可用")
        return True
    except ImportError:
        print("❌ pip不可用，请先安装pip")
        return False


def install_package(package_name, import_name=None):
    """安装Python包"""
    if import_name is None:
        import_name = package_name
        
    try:
        __import__(import_name)
        print(f"✅ {package_name} 已安装")
        return True
    except ImportError:
        print(f"📦 正在安装 {package_name}...")
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", package_name
            ])
            print(f"✅ {package_name} 安装成功")
            return True
        except subprocess.CalledProcessError:
            print(f"❌ {package_name} 安装失败")
            return False


def check_yt_dlp():
    """检查yt-dlp是否可用"""
    print("检查yt-dlp...")
    try:
        result = subprocess.run(
            ["yt-dlp", "--version"], 
            capture_output=True, 
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            version = result.stdout.strip()
            print(f"✅ yt-dlp版本: {version}")
            return True
        else:
            print("❌ yt-dlp不可用")
            return False
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print("❌ yt-dlp未安装或不在PATH中")
        return False


def create_desktop_shortcut():
    """创建桌面快捷方式（Windows）"""
    if platform.system() != "Windows":
        return
        
    try:
        import winshell
        from win32com.client import Dispatch
        
        desktop = winshell.desktop()
        path = os.path.join(desktop, "YouTube下载器.lnk")
        target = os.path.join(os.getcwd(), "main.py")
        wDir = os.getcwd()
        icon = os.path.join(os.getcwd(), "icon.ico")
        
        shell = Dispatch('WScript.Shell')
        shortcut = shell.CreateShortCut(path)
        shortcut.Targetpath = sys.executable
        shortcut.Arguments = f'"{target}"'
        shortcut.WorkingDirectory = wDir
        if os.path.exists(icon):
            shortcut.IconLocation = icon
        shortcut.save()
        
        print("✅ 桌面快捷方式创建成功")
    except ImportError:
        print("⚠️ 无法创建桌面快捷方式（缺少winshell或pywin32）")
    except Exception as e:
        print(f"⚠️ 创建桌面快捷方式失败: {e}")


def create_batch_file():
    """创建批处理文件（Windows）"""
    if platform.system() != "Windows":
        return
        
    try:
        # 经典版启动脚本
        classic_bat = """@echo off
cd /d "%~dp0"
python main.py
pause
"""
        with open("启动YouTube下载器.bat", "w", encoding="utf-8") as f:
            f.write(classic_bat)
            
        # 改进版启动脚本
        improved_bat = """@echo off
cd /d "%~dp0"
python main.py --improved
pause
"""
        with open("启动YouTube下载器(改进版).bat", "w", encoding="utf-8") as f:
            f.write(improved_bat)
            
        print("✅ 启动脚本创建成功")
    except Exception as e:
        print(f"⚠️ 创建启动脚本失败: {e}")


def create_shell_script():
    """创建Shell脚本（Linux/macOS）"""
    if platform.system() == "Windows":
        return
        
    try:
        # 经典版启动脚本
        classic_sh = """#!/bin/bash
cd "$(dirname "$0")"
python3 main.py
"""
        with open("start_youtube_downloader.sh", "w") as f:
            f.write(classic_sh)
        os.chmod("start_youtube_downloader.sh", 0o755)
        
        # 改进版启动脚本
        improved_sh = """#!/bin/bash
cd "$(dirname "$0")"
python3 main.py --improved
"""
        with open("start_youtube_downloader_improved.sh", "w") as f:
            f.write(improved_sh)
        os.chmod("start_youtube_downloader_improved.sh", 0o755)
        
        print("✅ 启动脚本创建成功")
    except Exception as e:
        print(f"⚠️ 创建启动脚本失败: {e}")


def create_download_directory():
    """创建下载目录"""
    download_dir = Path("download")
    if not download_dir.exists():
        download_dir.mkdir()
        print("✅ 下载目录创建成功")
    else:
        print("✅ 下载目录已存在")


def main():
    """主安装流程"""
    print("=" * 50)
    print("YouTube下载器安装程序")
    print("=" * 50)
    
    # 检查Python版本
    if not check_python_version():
        return False
        
    # 检查pip
    if not check_pip():
        return False
    
    # 安装依赖包
    required_packages = [
        ("PyQt5", "PyQt5"),
        ("yt-dlp", "yt_dlp"),
    ]
    
    print("\n检查和安装依赖包...")
    for package_name, import_name in required_packages:
        if not install_package(package_name, import_name):
            print(f"❌ 安装失败: {package_name}")
            return False
    
    # 检查yt-dlp命令行工具
    if not check_yt_dlp():
        print("⚠️ yt-dlp命令行工具不可用，但Python模块已安装")
    
    # 创建下载目录
    create_download_directory()
    
    # 创建启动脚本
    if platform.system() == "Windows":
        create_batch_file()
        # 可选：创建桌面快捷方式
        try:
            create_desktop_shortcut()
        except:
            pass
    else:
        create_shell_script()
    
    print("\n" + "=" * 50)
    print("✅ 安装完成！")
    print("=" * 50)
    
    print("\n使用方法:")
    if platform.system() == "Windows":
        print("1. 双击 '启动YouTube下载器.bat' 运行经典版")
        print("2. 双击 '启动YouTube下载器(改进版).bat' 运行改进版")
        print("3. 或在命令行中运行:")
    else:
        print("1. 运行 './start_youtube_downloader.sh' 启动经典版")
        print("2. 运行 './start_youtube_downloader_improved.sh' 启动改进版")
        print("3. 或在命令行中运行:")
    
    print("   python main.py                # 经典版")
    print("   python main.py --improved     # 改进版（推荐）")
    
    print("\n📖 详细使用说明请查看 USER_GUIDE.md")
    print("🔧 重构详情请查看 REFACTOR_SUMMARY.md")
    
    return True


if __name__ == "__main__":
    try:
        success = main()
        if not success:
            print("\n❌ 安装失败，请检查错误信息")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n⚠️ 安装被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 安装过程中出现错误: {e}")
        sys.exit(1)
