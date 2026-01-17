#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ADB管理工具
支持使用内置ADB工具，不依赖系统环境变量
"""

import os
import sys
import tempfile
import logging
import shutil
from pathlib import Path
import subprocess


class ADBManager:
    """ADB管理器 - 支持内置ADB工具"""
    
    def __init__(self):
        self.logger = logging.getLogger("utils.adb_manager")
        self.builtin_adb_path = None
        self.temp_dir = None
        self.setup_builtin_adb()
    
    def setup_builtin_adb(self):
        """设置内置ADB工具"""
        try:
            # 创建临时目录存放ADB工具
            self.temp_dir = tempfile.mkdtemp(prefix="adb_tv_tool_")
            self.logger.info(f"创建临时ADB目录: {self.temp_dir}")
            
            # 判断是否在EXE中运行
            if getattr(sys, 'frozen', False):
                # 在EXE中运行，从资源中提取ADB
                success = self._extract_adb_from_resources()
                if not success:
                    # 如果提取失败，尝试备份方案
                    self.logger.warning("内置ADB提取失败，尝试备用方案")
                    self._copy_adb_from_e_drive()
            else:
                # 在开发环境中运行，复制E盘的ADB工具
                self._copy_adb_from_e_drive()
            
            # 对于所有环境，都尝试EXE目录和PATH备份，如果主方法失败
            if not self.builtin_adb_path or not self.builtin_adb_path.exists():
                self.logger.warning("主方法失败，尝试备用方法")
                if not self._try_find_adb_alternative():
                    raise FileNotFoundError("所有ADB查找方法都失败")
                
            # 验证ADB工具是否可用
            if not self._verify_adb_exists():
                raise FileNotFoundError("ADB工具未找到或不可用")
            
            # 设置环境变量，让subprocess能够找到ADB
            os.environ['PATH'] = self.temp_dir + os.pathsep + os.environ['PATH']
            self.logger.info(f"ADB管理器初始化完成，ADB路径: {self.builtin_adb_path}")
            
        except Exception as e:
            self.logger.error(f"ADB管理器初始化失败: {e}")
            raise
    
    def _verify_adb_exists(self):
        """验证ADB工具是否存在并可执行"""
        if self.builtin_adb_path and self.builtin_adb_path.exists():
            self.logger.info(f"ADB工具已找到: {self.builtin_adb_path}")
            return True
        else:
            self.logger.error(f"ADB工具不存在: {self.builtin_adb_path}")
            return False
    
    def _copy_adb_from_e_drive(self):
        """从E盘复制ADB工具到临时目录"""
        try:
            source_dir = Path("E:/ADB")
            if not source_dir.exists():
                raise FileNotFoundError("E盘ADB目录不存在")
            
            # 复制所有ADB相关文件
            for file_path in source_dir.glob("*"):
                if file_path.is_file():
                    dest_path = Path(self.temp_dir) / file_path.name
                    shutil.copy2(file_path, dest_path)
                    self.logger.debug(f"复制文件: {file_path.name}")
            
            self.builtin_adb_path = Path(self.temp_dir) / "adb.exe"
            self.logger.info(f"从E盘复制ADB工具完成: {self.builtin_adb_path}")
            
        except Exception as e:
            self.logger.error(f"从E盘复制ADB失败: {e}")
            raise
    
    def _extract_adb_from_resources(self):
        """从EXE资源中提取ADB工具（打包时使用）"""
        try:
            # 在打包的EXE中，ADB工具应该被打包在临时目录的'adb'子目录中
            self.logger.info("在EXE环境中，尝试提取内置ADB工具")
            
            # 方法1: 检查_sys._MEIPASS目录（PyInstaller临时目录）
            if hasattr(sys, '_MEIPASS'):
                meipass_path = Path(sys._MEIPASS)
                adb_resources_path = meipass_path / 'adb'
                if adb_resources_path.exists():
                    # 从MEIPASS复制ADB工具到临时目录
                    for file_path in adb_resources_path.glob("*"):
                        if file_path.is_file():
                            dest_path = Path(self.temp_dir) / file_path.name
                            import shutil
                            shutil.copy2(file_path, dest_path)
                            self.logger.debug(f"从资源复制文件: {file_path.name}")
            
            # 方法2: 检查临时目录中的'adb'子目录
            adb_in_temp = Path(self.temp_dir) / 'adb'
            if adb_in_temp.exists():
                for file_path in adb_in_temp.glob("*"):
                    if file_path.is_file():
                        dest_path = Path(self.temp_dir) / file_path.name
                        import shutil
                        shutil.copy2(file_path, dest_path)
                        self.logger.debug(f"从临时子目录复制文件: {file_path.name}")
            
            # 检查是否复制成功
            temp_adb_path = Path(self.temp_dir) / "adb.exe"
            if temp_adb_path.exists():
                self.builtin_adb_path = temp_adb_path
                self.logger.info(f"成功使用内置ADB工具: {self.builtin_adb_path}")
                return True
            else:
                # 如果还是没有找到，尝试使用其他方法
                return self._try_find_adb_alternative()
                
        except Exception as e:
            self.logger.error(f"提取内置ADB工具失败: {e}")
            return self._try_find_adb_alternative()
        return False
    
    def _try_find_adb_alternative(self):
        """尝试其他方法找到ADB工具"""
        try:
            # 检查当前目录下的adb子目录
            current_dir_adb = Path.cwd() / 'adb'
            if current_dir_adb.exists():
                temp_adb_path = Path(self.temp_dir) / "adb.exe"
                import shutil
                shutil.copy2(current_dir_adb / "adb.exe", temp_adb_path)
                if temp_adb_path.exists():
                    self.builtin_adb_path = temp_adb_path
                    self.logger.info(f"从当前目录找到ADB工具: {self.builtin_adb_path}")
                    return True
            
            # 检查EXE同级目录的adb文件夹
            exe_dir_adb = Path(sys.executable).parent / "adb"
            if exe_dir_adb.exists():
                temp_adb_path = Path(self.temp_dir) / "adb.exe"
                import shutil
                shutil.copy2(exe_dir_adb / "adb.exe", temp_adb_path)
                if temp_adb_path.exists():
                    self.builtin_adb_path = temp_adb_path
                    self.logger.info(f"从EXE目录找到ADB工具: {self.builtin_adb_path}")
                    return True
            
            # 最后尝试从系统PATH中查找
            import shutil
            system_adb = shutil.which("adb")
            if system_adb:
                temp_adb_path = Path(self.temp_dir) / "adb.exe"
                shutil.copy2(system_adb, temp_adb_path)
                if temp_adb_path.exists():
                    self.builtin_adb_path = temp_adb_path
                    self.logger.info(f"从系统PATH复制ADB工具: {self.builtin_adb_path}")
                    return True
            
            # 如果所有方法都失败
            raise FileNotFoundError("无法找到可用的ADB工具")
            
        except Exception as e:
            self.logger.error(f"备用ADB查找方法失败: {e}")
            return False
    
    def run_adb_command(self, args, timeout=30, text=True, **kwargs):
        """运行ADB命令 - 增强调试版本"""
        try:
            cmd = [str(self.builtin_adb_path)] + args
            full_command = ' '.join(cmd)
            
            # 在控制台显示执行的命令
            print(f"\n🔧 ADB命令执行:")
            print(f"  命令: {full_command}")
            print(f"  超时: {timeout}s")
            
            # 根据text参数决定使用文本模式还是二进制模式
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=text,  # 使用传入的text参数
                timeout=timeout,
                **kwargs
            )
            
            if text:
                # 文本模式：直接使用字符串输出
                stdout = result.stdout or ""
                stderr = result.stderr or ""
            else:
                # 二进制模式：返回原始字节数据
                stdout = result.stdout or b""
                stderr = result.stderr or b""
            
            # 在控制台显示结果
            print(f"  返回码: {result.returncode}")
            
            if text and stdout:
                stdout_lines = stdout.strip().split('\n')
                print(f"  标准输出 ({len(stdout)} 字符):")
                for line in stdout_lines[:10]:  # 只显示前10行
                    print(f"    {line}")
                if len(stdout_lines) > 10:
                    remaining_lines = len(stdout_lines) - 10
                    print(f"    ... (还有 {remaining_lines} 行)")
            elif not text and stdout:
                print(f"  标准输出 (二进制数据，{len(stdout)} 字节)")
            
            if text and stderr:
                stderr_lines = stderr.strip().split('\n')
                print(f"  错误输出 ({len(stderr)} 字符):")
                for line in stderr_lines[:5]:  # 只显示前5行错误
                    print(f"    {line}")
                if len(stderr_lines) > 5:
                    remaining_lines = len(stderr_lines) - 5
                    print(f"    ... (还有 {remaining_lines} 行)")
            elif not text and stderr:
                print(f"  错误输出 (二进制数据，{len(stderr)} 字节)")
            
            return {
                'success': result.returncode == 0,
                'returncode': result.returncode,
                'stdout': stdout,
                'stderr': stderr
            }
            
        except subprocess.TimeoutExpired as e:
            error_msg = f"ADB命令超时: {e}"
            print(f"❌ {error_msg}")
            self.logger.error(error_msg)
            return {'success': False, 'error': f'命令超时: {timeout}秒'}
        except Exception as e:
            error_msg = f"ADB命令执行失败: {e}"
            print(f"❌ {error_msg}")
            self.logger.error(error_msg)
            return {'success': False, 'error': str(e)}
    
    def check_adb_availability(self):
        """检查内置ADB是否可用"""
        try:
            result = self.run_adb_command(['version'], timeout=10)
            return result['success']
        except Exception as e:
            self.logger.error(f"检查ADB可用性失败: {e}")
            return False
    
    def cleanup(self):
        """清理临时文件"""
        if self.temp_dir and Path(self.temp_dir).exists():
            try:
                shutil.rmtree(self.temp_dir)
                self.logger.info(f"清理临时ADB目录: {self.temp_dir}")
            except Exception as e:
                self.logger.warning(f"清理临时目录失败: {e}")


# 全局ADB管理器实例
_adb_manager = None


def get_adb_manager():
    """获取全局ADB管理器实例"""
    global _adb_manager
    if _adb_manager is None:
        _adb_manager = ADBManager()
    return _adb_manager


def cleanup_adb_manager():
    """清理ADB管理器"""
    global _adb_manager
    if _adb_manager:
        _adb_manager.cleanup()
        _adb_manager = None