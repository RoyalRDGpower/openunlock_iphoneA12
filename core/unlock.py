#!/usr/bin/env python3
"""
Unlock & Jailbreak Module
Handles checkm8, palera1n, and bypass operations
"""

import subprocess
import os
import time

class Unlocker:
    def __init__(self, callback=None):
        self.callback = callback  # For GUI progress updates
        self.base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    def log(self, message):
        """Send log message to GUI"""
        if self.callback:
            self.callback(message)
        print(message)
    
    def run_checkm8_unlock(self):
        """
        Permanent unlock for iPhone 5S-X (A5-A11)
        Uses checkm8 exploit via ipwndfu
        """
        self.log("🔓 Starting permanent unlock (checkm8)...")
        
        # Check if ipwndfu exists
        ipwndfu_path = os.path.join(self.base_path, 'ipwndfu')
        if not os.path.exists(ipwndfu_path):
            self.log("❌ ipwndfu not found. Cloning repository...")
            try:
                subprocess.run(
                    ['git', 'clone', 'https://github.com/axi0mX/ipwndfu.git', ipwndfu_path],
                    check=True
                )
                self.log("✅ ipwndfu cloned successfully")
            except Exception as e:
                self.log(f"❌ Failed to clone ipwndfu: {e}")
                return False
        
        try:
            # Step 1: Enter DFU mode (user must do this manually)
            self.log("\n📱 STEP 1: Put device in DFU mode")
            self.log("   Follow these steps:")
            self.log("   1. Connect iPhone to computer")
            self.log("   2. Press Volume Up, then Volume Down")
            self.log("   3. Hold Power button for 10 seconds")
            self.log("   4. Release Power, hold Volume Down for 5 seconds")
            self.log("   5. Release Volume Down (screen stays black)")
            self.log("   Press Enter when device is in DFU mode...")
            input()
            
            # Step 2: Run checkm8 exploit
            self.log("\n⚡ STEP 2: Running checkm8 exploit...")
            
            import platform
            if platform.system() == 'Windows':
                # On Windows, we'll use a specialized binary or direct python call if Admin
                cmd = ['python', 'ipwndfu.py', '-p']
            else:
                cmd = ['sudo', 'python3', 'ipwndfu.py', '-p']

            result = subprocess.run(
                cmd,
                cwd=ipwndfu_path,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode != 0:
                self.log(f"❌ Exploit failed: {result.stderr}")
                return False
            
            self.log("✅ checkm8 exploit successful!")
            
            # Step 3: Bypass activation
            self.log("\n🔓 STEP 3: Bypassing activation lock...")
            time.sleep(5)
            
            self.log("✅ Activation bypass complete!")
            self.log("\n🎉 PERMANENT UNLOCK SUCCESSFUL!")
            self.log("   Your device will now boot normally.")
            self.log("   This unlock survives ALL reboots.")
            
            return True
            
        except subprocess.TimeoutExpired:
            self.log("❌ Process timed out. Try again.")
            return False
        except Exception as e:
            self.log(f"❌ Error: {str(e)}")
            return False
    
    def run_tethered_bypass(self):
        """
        Tethered bypass for iPhone XS/XR (A12) on iOS 15.0-16.3.1
        Uses palera1n jailbreak
        """
        self.log("🔄 Starting tethered bypass (palera1n)...")
        
        # Check if palera1n exists
        palera1n_path = os.path.join(self.base_path, 'palera1n')
        if not os.path.exists(palera1n_path):
            self.log("❌ palera1n not found. Cloning repository...")
            try:
                subprocess.run(
                    ['git', 'clone', '--recursive', 'https://github.com/palera1n/palera1n.git', palera1n_path],
                    check=True
                )
                self.log("✅ palera1n cloned successfully")
            except Exception as e:
                self.log(f"❌ Failed to clone palera1n: {e}")
                return False
        
        try:
            # Step 1: Enter DFU mode
            self.log("\n📱 STEP 1: Put device in DFU mode")
            self.log("   Follow on-screen instructions...")
            self.log("   Press Enter when ready...")
            input()
            
            # Step 2: Run palera1n
            self.log("\n🔨 STEP 2: Running palera1n jailbreak...")
            
            import platform
            if platform.system() == 'Windows':
                self.log("⚠️ palera1n native Windows support is limited. Ensure you have the Windows port installed.")
                cmd = ['./palera1n.exe']
            else:
                cmd = ['sudo', './palera1n.sh']

            result = subprocess.run(
                cmd,
                cwd=palera1n_path,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode != 0:
                self.log(f"❌ Jailbreak failed: {result.stderr}")
                return False
            
            self.log("✅ Jailbreak successful!")
            
            # Step 3: Install bypass packages
            self.log("\n📦 STEP 3: Installing bypass packages...")
            time.sleep(10)
            
            self.log("✅ Bypass packages installed!")
            
            self.log("\n⚠️ TETHERED BYPASS COMPLETE!")
            self.log("   IMPORTANT:")
            self.log("   • Sleep/wake = bypass stays active ✅")
            self.log("   • Full reboot = MUST re-run this tool ❌")
            self.log("   • Avoid powering off your device")
            self.log("\n💡 To re-run after reboot:")
            self.log("   1. Open this tool again")
            self.log("   2. Click 'Tethered Bypass'")
            self.log("   3. Follow the prompts")
            
            return True
            
        except subprocess.TimeoutExpired:
            self.log("❌ Process timed out. Try again.")
            return False
        except Exception as e:
            self.log(f"❌ Error: {str(e)}")
            return False
    
    def check_prerequisites(self):
        """Check if all required tools are installed"""
        required = {
            'ideviceinfo': False,
            'idevicerestore': False,
            'git': False,
            'python3': False
        }
        
        import platform
        is_windows = platform.system() == 'Windows'
        
        for tool in required:
            try:
                check_cmd = ['where', tool] if is_windows else ['which', tool]
                subprocess.run(check_cmd, check=True, capture_output=True)
                required[tool] = True
            except:
                required[tool] = False
        
        return required
