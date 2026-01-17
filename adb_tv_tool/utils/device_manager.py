#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
设备管理器
管理当前连接的设备状态，实现页面间设备信息共享
"""

import logging
from dataclasses import dataclass
from typing import Optional, Dict, Any


@dataclass
class DeviceInfo:
    """设备信息类"""
    serial: str
    name: Optional[str] = None
    model: Optional[str] = None
    status: str = "unknown"


class DeviceManager:
    """设备管理器 - 单例模式"""
    
    _instance = None
    _current_device: Optional[DeviceInfo] = None
    _device_listeners = []  # 设备变化监听器列表
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.logger = logging.getLogger("utils.device_manager")
        return cls._instance
    
    def set_current_device(self, device_info: DeviceInfo):
        """设置当前连接的设备"""
        self._current_device = device_info
        self.logger.info(f"设置当前设备: {device_info.serial}")
        
        # 通知所有监听器
        for listener in self._device_listeners:
            try:
                listener(device_info)
            except Exception as e:
                self.logger.error(f"通知监听器失败: {e}")
    
    def get_current_device(self) -> Optional[DeviceInfo]:
        """获取当前连接的设备"""
        return self._current_device
    
    def clear_current_device(self):
        """清除当前设备连接"""
        self._current_device = None
        self.logger.info("清除当前设备")
        
        # 通知所有监听器
        for listener in self._device_listeners:
            try:
                listener(None)
            except Exception as e:
                self.logger.error(f"通知监听器失败: {e}")
    
    def add_listener(self, listener):
        """添加设备状态变化监听器"""
        if listener not in self._device_listeners:
            self._device_listeners.append(listener)
            self.logger.debug(f"添加设备监听器: {len(self._device_listeners)} 个")
    
    def remove_listener(self, listener):
        """移除设备状态变化监听器"""
        if listener in self._device_listeners:
            self._device_listeners.remove(listener)
            self.logger.debug(f"移除设备监听器: {len(self._device_listeners)} 个")


# 全局设备管理器实例
device_manager = DeviceManager()


def get_device_manager() -> DeviceManager:
    """获取设备管理器实例"""
    return device_manager


def set_current_device(serial: str, name: str = None, model: str = None, status: str = "device"):
    """设置当前设备的便捷函数"""
    device_info = DeviceInfo(
        serial=serial,
        name=name,
        model=model,
        status=status
    )
    device_manager.set_current_device(device_info)


def get_current_device() -> Optional[DeviceInfo]:
    """获取当前设备的便捷函数"""
    return device_manager.get_current_device()


def clear_current_device():
    """清除当前设备的便捷函数"""
    device_manager.clear_current_device()