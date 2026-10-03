# -*- coding: utf-8 -*-
import winreg, os, glob, subprocess

HKLM = winreg.HKEY_LOCAL_MACHINE
HKCU = winreg.HKEY_CURRENT_USER


def v(root, path, name):
    try:
        k = winreg.OpenKey(root, path)
        d, t = winreg.QueryValueEx(k, name)
        return d
    except Exception:
        return 'N/A'


print('===== 4. 缓解措施 / 安全 =====')
print('  FeatureSettingsOverride      =', v(HKLM, r'SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management', 'FeatureSettingsOverride'))
print('  FeatureSettingsOverrideMask  =', v(HKLM, r'SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management', 'FeatureSettingsOverrideMask'))
print('  DisableExceptionChainValid.  =', v(HKLM, r'SYSTEM\CurrentControlSet\Control\Session Manager\kernel', 'DisableExceptionChainValidation'))
print('  ProtectionMode               =', v(HKLM, r'SYSTEM\CurrentControlSet\Control\Session Manager', 'ProtectionMode'))
print('  MitigationOptions            =', v(HKLM, r'SYSTEM\CurrentControlSet\Control\Session Manager\kernel', 'MitigationOptions'))
print('  VBS EnableVBS                =', v(HKLM, r'SYSTEM\CurrentControlSet\Control\DeviceGuard', 'EnableVirtualizationBasedSecurity'))
print('  HVCI Enabled                 =', v(HKLM, r'SYSTEM\CurrentControlSet\Control\DeviceGuard\Scenarios\HypervisorEnforcedCodeIntegrity', 'Enabled'))

print('\n===== 5. 休眠 / 快速启动 =====')
print('  hiberfil.sys 存在 =', os.path.exists('C:\\hiberfil.sys'))
print('  HiberbootEnabled(快速启动) =', v(HKLM, r'SYSTEM\CurrentControlSet\Control\Session Manager\Power', 'HiberbootEnabled'))
print('  HibernateEnabled =', v(HKLM, r'SYSTEM\CurrentControlSet\Control\Power', 'HibernateEnabled'))

print('\n===== 6. 电源节流 =====')
print('  PowerThrottlingOff =', v(HKLM, r'SYSTEM\CurrentControlSet\Control\Power\PowerThrottling', 'PowerThrottlingOff'))
print('  NVMe IdlePowerMode =', v(HKLM, r'SYSTEM\CurrentControlSet\Services\stornvme\Parameters\Device', 'IdlePowerMode'))
print('  StorageD3InModernStandby =', v(HKLM, r'SYSTEM\CurrentControlSet\Control\Storage', 'StorageD3InModernStandby'))

print('\n===== 7. 截图工具 / PrtSc =====')
print('  PrintScreenKeyForSnippingEnabled =', v(HKCU, r'Control Panel\Keyboard', 'PrintScreenKeyForSnippingEnabled'))
print('  PixPin 目录存在 =', os.path.exists('C:\\Users\\h3189\\AppData\\Local\\Programs\\PixPin'))
print('  PixPin Run 自启 =', v(HKCU, r'SOFTWARE\Microsoft\Windows\CurrentVersion\Run', 'PixPin'))

print('\n===== 8. 更新策略 =====')
print('  AU\\AUOptions =', v(HKLM, r'SOFTWARE\Policies\Microsoft\Windows\WindowsUpdate\AU', 'AUOptions'))
print('  DeferFeatureUpdates =', v(HKLM, r'SOFTWARE\Policies\Microsoft\Windows\WindowsUpdate', 'DeferFeatureUpdates'))
print('  TargetReleaseVersionInfo =', v(HKLM, r'SOFTWARE\Policies\Microsoft\Windows\WindowsUpdate', 'TargetReleaseVersionInfo'))

print('\n===== 9. Edge / WebView2 =====')
print('  Edge 安装 =', os.path.exists('C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe'))
wv = glob.glob('C:\\Program Files (x86)\\Microsoft\\EdgeWebView\\Application\\*\\msedgewebview2.exe')
print('  WebView2 运行时 =', wv[:3] if wv else 'NOT FOUND')
appdata = os.environ.get('APPDATA', '')
print('  StartMenu Edge 快捷 =', os.path.exists(os.path.join(appdata, r'Microsoft\Windows\Start Menu\Programs\Microsoft Edge.lnk')))

print('\n===== 10. Defender =====')
for p in ['C:\\Program Files\\Windows Defender\\MsMpEng.exe', 'C:\\Program Files\\Windows Defender']:
    print('  %s = %s' % (p, os.path.exists(p)))
try:
    r = subprocess.run(['cmd', '/c', 'sc query WinDefend'], capture_output=True, text=True, timeout=20)
    lines = [l.strip() for l in r.stdout.splitlines() if 'STATE' in l or 'FAILED' in l or '1060' in l]
    print('  sc query WinDefend:', lines[:2] if lines else r.stdout.strip()[:120])
except Exception as e:
    print('  查询失败:', e)

print('\n===== 11. 其他精简痕迹 =====')
print('  Bing/Cortana 搜索策略 =', v(HKCU, r'SOFTWARE\Policies\Microsoft\Windows\Explorer', 'DisableSearchBoxSuggestions'))
print('  AdvertisingID =', v(HKCU, r'SOFTWARE\Microsoft\Windows\CurrentVersion\AdvertisingInfo', 'Enabled'))
print('  Copilot 策略 =', v(HKCU, r'SOFTWARE\Policies\Microsoft\Windows\WindowsCopilot', 'TurnOffWindowsCopilot'))
print('  Telemetry AllowTelemetry =', v(HKLM, r'SOFTWARE\Policies\Microsoft\Windows\DataCollection', 'AllowTelemetry'))
print('  GameDVR 禁用 =', v(HKCU, r'SYSTEM\GameConfigStore', 'GameDVR_Enabled'))
print('  StartupDelayInMSec =', v(HKCU, r'SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Serialize', 'StartupDelayInMSec'))
print('  MenuShowDelay =', v(HKCU, r'Control Panel\Desktop', 'MenuShowDelay'))
print('  VisualFXSetting =', v(HKCU, r'SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\VisualEffects', 'VisualFXSetting'))
print('  MMCSS SystemResponsiveness =', v(HKLM, r'SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile', 'SystemResponsiveness'))
print('  NetworkThrottlingIndex =', v(HKLM, r'SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile', 'NetworkThrottlingIndex'))
print('  Games TaskPriority =', v(HKLM, r'SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile\Tasks\Games', 'Priority'))
