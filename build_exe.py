#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ADB电视工具打包脚本
使用PyInstaller打包成独立EXE文件
"""

import os
import sys
import shutil
from pathlib import Path

def setup_packaging():
    """设置打包环境"""
    print("=" * 60)
    print("ADB电视工具 - EXE打包程序")
    print("=" * 60)
    
    # 检查PyInstaller是否安装
    try:
        import PyInstaller
        print("✅ PyInstaller 已安装")
    except ImportError:
        print("❌ PyInstaller 未安装，正在安装...")
        os.system("pip install pyinstaller")
    
    # 创建打包目录
    build_dir = Path("build_exe")
    dist_dir = Path("dist")
    
    # 清理旧的打包文件
    if build_dir.exists():
        shutil.rmtree(build_dir)
        print("✅ 已清理旧构建文件")
    
    return build_dir, dist_dir

def create_spec_file():
    """创建PyInstaller spec文件"""
    spec_content = f'''# -*- mode: python ; coding: utf-8 -*-

import sys
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

block_cipher = None

a = Analysis(
    ['adb_tv_tool/simplified_main.py'],
    pathex=[str(project_root)],
    binaries=[],
    datas=[
        # 包含ADB工具文件
        ('.comate/adb_temp/*', '.comate/adb_temp/'),
        # 包含必要的配置文件
        ('requirements.txt', '.'),
    ],
    hiddenimports=[
        'PyQt6',
        'PyQt6.QtWidgets',
        'PyQt6.QtCore',
        'PyQt6.QtGui',
        'logging',
        'subprocess',
        'tempfile',
        'shutil',
        'pathlib',
    ],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# 添加PyQt6相关文件
pyqt6_paths = []
for path in sys.path:
    if 'PyQt6' in path:
        pyqt6_paths.append(path)

for pyqt_path in pyqt6_paths:
    pyqt_path = Path(pyqt_path)
    if pyqt_path.exists():
        # 添加Qt插件
        plugins_path = pyqt_path / 'Qt6' / 'plugins'
        if plugins_path.exists():
            a.datas += collect_data_files(str(plugins_path), 'qt6_plugins')

# 排除不必要的模块以减少体积
excludes = [
    'tkinter',
    'matplotlib',
    'pandas',
    'numpy',
    'scipy',
    'sqlite3',
    'test',
    'unittest',
    'email',
    'http',
    'urllib',
    'xml',
    'html',
    'ssl',
]

for exclude in excludes:
    if exclude in a.dependencies:
        a.dependencies.remove(exclude)

# 设置图标和元数据
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='ADB_TV_Tool',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,  # 启用UPX压缩
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # 不显示控制台窗口
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(project_root / 'adb_tv_tool' / 'ui' / 'icon.ico') if Path('adb_tv_tool/ui/icon.ico').exists() else None,
)

# 如果有图标文件，添加到资源
if Path('adb_tv_tool/ui/icon.ico').exists():
    exe.datas.append(('adb_tv_tool/ui/icon.ico', 'icon.ico'))
'''
    
    with open('adb_tv_tool.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    print("✅ 已创建spec文件")

def package_application():
    """打包应用程序"""
    print("\\n🚀 开始打包ADB电视工具...")
    
    # 使用PyInstaller打包
    result = os.system('pyinstaller --clean --noconfirm adb_tv_tool.spec')
    
    if result == 0:
        print("✅ 打包成功!")
        
        # 检查生成的文件
        dist_path = Path("dist")
        if dist_path.exists():
            exe_files = list(dist_path.glob("*.exe"))
            if exe_files:
                print(f"📦 生成的EXE文件: {exe_files[0].name}")
                print(f"📁 文件位置: {exe_files[0].absolute()}")
                
                # 显示文件大小
                size_mb = exe_files[0].stat().st_size / (1024 * 1024)
                print(f"📊 文件大小: {size_mb:.1f} MB")
                
        return True
    else:
        print("❌ 打包失败!")
        return False

def copy_additional_files():
    """复制额外的文件到dist目录"""
    dist_path = Path("dist")
    if not dist_path.exists():
        return
    
    # 复制README文件
    files_to_copy = [
        "README.md",
        "简化版使用指南.md",
        "截图功能优化说明.md"
    ]
    
    for file in files_to_copy:
        if Path(file).exists():
            shutil.copy2(file, dist_path / file)
            print(f"✅ 已复制: {file}")

def main():
    """主函数"""
    try:
        # 设置打包环境
        build_dir, dist_dir = setup_packaging()
        
        # 创建spec文件
        create_spec_file()
        
        # 打包应用程序
        if package_application():
            # 复制额外文件
            copy_additional_files()
            
            print("\\n" + "=" * 60)
            print("🎉 ADB电视工具打包完成!")
            print("=" * 60)
            print("📋 打包内容:")
            print("  • ADB_TV_Tool.exe - 主程序")
            print("  • README.md - 使用说明")
            print("  • 简化版使用指南.md - 详细指南")
            print("  • 截图功能优化说明.md - 技术文档")
            print("\\n🚀 使用方法:")
            print("  直接运行 dist/ADB_TV_Tool.exe 即可启动程序")
            print("=" * 60)
        else:
            print("❌ 打包过程中出现错误")
            
    except Exception as e:
        print(f"❌ 打包失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()