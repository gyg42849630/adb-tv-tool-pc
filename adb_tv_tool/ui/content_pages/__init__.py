# -*- coding: utf-8 -*-
"""
内容页面包初始化文件
"""

from .environment_check import EnvironmentCheckPage
from .device_connect import DeviceConnectPage
from .screen_mirror import ScreenMirrorPage
from .app_manager import AppManagerPage
from .apk_import import APKImportPage
from .install_execute import InstallExecutePage
from .result_summary import ResultSummaryPage
from .settings import SettingsPage

__all__ = [
    'EnvironmentCheckPage',
    'DeviceConnectPage',
    'ScreenMirrorPage',
    'AppManagerPage',
    'APKImportPage',
    'InstallExecutePage',
    'ResultSummaryPage',
    'SettingsPage'
]