#!/usr/bin/env python3
"""
Device Detection & Unlock Type Module
Detects device and determines unlock method with clear customer messaging
"""

import subprocess
import os

class iOSDevice:
    def __init__(self):
        self.connected = False
        self.device_info = {}
    
    def is_connected(self):
        """Check if iOS device is connected"""
        try:
            result = subprocess.run(
                ['ideviceinfo'],
                capture_output=True,
                text=True,
                timeout=5
            )
            self.connected = result.returncode == 0
            return self.connected
        except Exception as e:
            print(f"Error checking device: {e}")
            return False
    
    def get_device_info(self):
        """Get detailed device information"""
        if not self.is_connected():
            return None
        
        try:
            result = subprocess.run(
                ['ideviceinfo'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            info = {}
            for line in result.stdout.split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    info[key.strip()] = value.strip()
            
            self.device_info = info
            return info
        except Exception as e:
            print(f"Error getting device info: {e}")
            return None
    
    def get_model_name(self):
        """Get human-readable model name"""
        product_type = self.device_info.get('ProductType', '')
        
        model_map = {
            # iPhone 5S (A7) - ✅ PERMANENT
            'iPhone6,1': 'iPhone 5S (GSM)',
            'iPhone6,2': 'iPhone 5S (Global)',
            
            # iPhone 6 (A8) - ✅ PERMANENT
            'iPhone7,1': 'iPhone 6 Plus',
            'iPhone7,2': 'iPhone 6',
            
            # iPhone 6S (A9) - ✅ PERMANENT
            'iPhone8,1': 'iPhone 6S',
            'iPhone8,2': 'iPhone 6S Plus',
            'iPhone8,4': 'iPhone SE (1st Gen)',
            
            # iPhone 7 (A10) - ✅ PERMANENT
            'iPhone9,1': 'iPhone 7 (GSM)',
            'iPhone9,2': 'iPhone 7 Plus (GSM)',
            'iPhone9,3': 'iPhone 7 (Global)',
            'iPhone9,4': 'iPhone 7 Plus (Global)',
            
            # iPhone 8 / X (A11) - ✅ PERMANENT
            'iPhone10,1': 'iPhone 8 (GSM)',
            'iPhone10,2': 'iPhone 8 Plus (GSM)',
            'iPhone10,3': 'iPhone X (Global)',
            'iPhone10,4': 'iPhone 8 (Global)',
            'iPhone10,5': 'iPhone 8 Plus (Global)',
            'iPhone10,6': 'iPhone X (GSM)',
            
            # iPhone XS / XR (A12) - ⚠️ TETHERED (if iOS 15-16.3.1)
            'iPhone11,2': 'iPhone XS',
            'iPhone11,4': 'iPhone XS Max',
            'iPhone11,6': 'iPhone XS Max (China)',
            'iPhone11,8': 'iPhone XR',
            
            # iPhone 11 (A13) - ❌ SERVER ONLY
            'iPhone12,1': 'iPhone 11',
            'iPhone12,3': 'iPhone 11 Pro',
            'iPhone12,5': 'iPhone 11 Pro Max',
            
            # iPhone 12+ - ❌ SERVER ONLY
            'iPhone13,1': 'iPhone 12 mini',
            'iPhone13,2': 'iPhone 12',
            'iPhone13,3': 'iPhone 12 Pro',
            'iPhone13,4': 'iPhone 12 Pro Max',
            'iPhone14,2': 'iPhone 13 Pro',
            'iPhone14,3': 'iPhone 13 Pro Max',
            'iPhone14,4': 'iPhone 13 mini',
            'iPhone14,5': 'iPhone 13',
        }
        
        return model_map.get(product_type, f'{product_type} (Unknown Model)')
    
    def get_ios_version(self):
        """Get iOS version"""
        return self.device_info.get('ProductVersion', 'Unknown')
    
    def get_serial(self):
        """Get device serial number"""
        return self.device_info.get('SerialNumber', 'Unknown')
    
    def get_battery_level(self):
        """Get battery percentage"""
        try:
            result = subprocess.run(
                ['ideviceinfo', '-k', 'BatteryCurrentCapacity'],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.stdout.strip()
        except:
            return 'N/A'
    
    def get_unlock_type(self):
        """
        Returns unlock type with clear customer-facing messaging
        """
        product_type = self.device_info.get('ProductType', '')
        ios_version = self.device_info.get('ProductVersion', '')
        
        # Checkm8 devices (A5-A11) - PERMANENT
        checkm8_models = [
            'iPhone6,1','iPhone6,2','iPhone7,1','iPhone7,2',
            'iPhone8,1','iPhone8,2','iPhone8,4',
            'iPhone9,1','iPhone9,2','iPhone9,3','iPhone9,4',
            'iPhone10,1','iPhone10,2','iPhone10,3','iPhone10,4','iPhone10,5','iPhone10,6'
        ]
        
        if product_type in checkm8_models:
            return {
                'type': 'permanent',
                'price': 9.99,
                'title': '✅ Permanent Unlock',
                'description': 'One-time process. Survives ALL reboots. No re-run needed.',
                'icon': '🔓',
                'warning': None,
                'method': 'checkm8'
            }
        
        # A12 devices (XS/XR) with supported iOS - TETHERED
        a12_models = ['iPhone11,2','iPhone11,4','iPhone11,6','iPhone11,8']
        
        if product_type in a12_models:
            try:
                ios_major = int(ios_version.split('.')[0])
                ios_minor = int(ios_version.split('.')[1]) if '.' in ios_version else 0
                
                if 15 <= ios_major <= 16 and (ios_major < 16 or ios_minor <= 3):
                    return {
                        'type': 'tethered',
                        'price': 14.99,
                        'title': '⚠️ Tethered Bypass',
                        'description': 'Works after sleep/wake. MUST re-run tool after full reboot.',
                        'icon': '🔄',
                        'warning': '❗ This bypass is LOST if you fully power off/on your device. You will need to re-run this tool to restore access.',
                        'method': 'palera1n'
                    }
            except:
                pass
            
            # A12 with unsupported iOS = Server only
            return {
                'type': 'server',
                'price': 34.99,
                'title': '✅ Permanent Server Unlock',
                'description': 'Works on ANY iOS version. Permanent. No re-run ever needed.',
                'icon': '☁️',
                'warning': None,
                'method': 'server_api'
            }
        
        # Everything else (A13+) = Server only
        return {
            'type': 'server',
            'price': 34.99,
            'title': '✅ Permanent Server Unlock',
            'description': 'Works on ANY iOS version. Permanent. No re-run ever needed.',
            'icon': '☁️',
            'warning': None,
            'method': 'server_api'
        }
    
    def exit_recovery(self):
        """Exit recovery mode"""
        try:
            subprocess.run(
                ['idevicerestore', '--exit-recovery'],
                capture_output=True,
                timeout=10
            )
            return True
        except Exception as e:
            print(f"Error exiting recovery: {e}")
            return False
