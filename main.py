cat > main.py << 'MAINEOF'
#!/usr/bin/env python3
"""
OpenUnlock Linux - Main GUI Application
Complete with pre-payment confirmation and transparency
"""

import sys
import os
from datetime import datetime
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QTextEdit, QProgressBar, QDialog, QCheckBox,
    QMessageBox, QGroupBox, QStatusBar, QInputDialog, QLineEdit
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QIcon

# Add core to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.device import iOSDevice
from core.unlock import Unlocker

class DisclaimerDialog(QDialog):
    """Legal Disclaimer - Shows on first launch"""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("⚠️ Legal & Ethical Notice")
        self.setModal(True)
        self.setMinimumSize(600, 500)
        
        layout = QVBoxLayout()
        
        text = QLabel("""
        <h2>⚠️ LEGAL & ETHICAL NOTICE</h2>
        
        <p><b>This software is intended ONLY for:</b></p>
        <ul>
            <li>Devices you <b>OWN</b></li>
            <li>Devices you have <b>EXPLICIT PERMISSION</b> to access</li>
            <li>Legitimate recovery scenarios (forgotten passwords, etc.)</li>
        </ul>
        
        <p><b>Using this tool to access devices without authorization 
        may violate laws in your jurisdiction.</b></p>
        
        <p><b>What this tool does:</b></p>
        <ul>
            <li><b>iPhone 5S-X:</b> Permanent unlock via checkm8 (survives all reboots)</li>
            <li><b>iPhone XS/XR:</b> Tethered bypass (lost on full reboot, must re-run tool)</li>
            <li><b>iPhone 11+:</b> Server-based permanent unlock (via licensed partners)</li>
        </ul>
        
        <p>You, the user, are solely responsible for lawful use.</p>
        """)
        text.setWordWrap(True)
        layout.addWidget(text)
        
        self.check1 = QCheckBox("I confirm I own this device or have authority")
        self.check2 = QCheckBox("I understand misuse may violate laws")
        layout.addWidget(self.check1)
        layout.addWidget(self.check2)
        
        btn_layout = QHBoxLayout()
        self.btn_accept = QPushButton("ACCEPT & CONTINUE")
        self.btn_accept.setEnabled(False)
        self.btn_accept.clicked.connect(self.accept)
        
        self.btn_exit = QPushButton("EXIT")
        self.btn_exit.clicked.connect(self.reject)
        
        btn_layout.addWidget(self.btn_accept)
        btn_layout.addWidget(self.btn_exit)
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)
        
        self.check1.stateChanged.connect(self.update_button)
        self.check2.stateChanged.connect(self.update_button)
    
    def update_button(self):
        self.btn_accept.setEnabled(self.check1.isChecked() and self.check2.isChecked())


class PurchaseConfirmationDialog(QDialog):
    """Pre-Payment Confirmation - Forces acknowledgment before payment"""
    def __init__(self, parent, unlock_info, device):
        super().__init__(parent)
        self.unlock_info = unlock_info
        self.device = device
        self.setWindowTitle(f"{unlock_info['icon']} {unlock_info['title']}")
        self.setModal(True)
        self.setMinimumSize(550, 450)
        
        layout = QVBoxLayout()
        
        # Header
        header = QLabel(f"<h2>{unlock_info['icon']} {unlock_info['title']}</h2>")
        header.setAlignment(Qt.AlignCenter)
        layout.addWidget(header)
        
        # Device info
        device_text = QLabel(f"""
        <b>Device:</b> {device.get_model_name()}<br>
        <b>iOS Version:</b> {device.get_ios_version()}<br>
        <b>Serial:</b> {device.get_serial()[-4:]}****
        """)
        layout.addWidget(device_text)
        
        # Description
        desc = QLabel(f"<p style='font-size:12px;'>{unlock_info['description']}</p>")
        desc.setWordWrap(True)
        layout.addWidget(desc)
        
        # WARNING BOX (Only for tethered)
        if unlock_info.get('warning'):
            warning_box = QLabel(f"""
            <div style="background:#fff3cd; border:2px solid #ffc107; 
                        padding:15px; border-radius:5px;">
            <b>⚠️ IMPORTANT:</b><br><br>
            {unlock_info['warning']}<br><br>
            <small>💡 <b>Tip:</b> Avoid full reboots. Sleep/wake is fine.<br>
            After reboot, simply re-run this tool to restore access.</small>
            </div>
            """)
            warning_box.setWordWrap(True)
            layout.addWidget(warning_box)
        
        # Price
        price_label = QLabel(f"<h3>Price: ${unlock_info['price']:.2f}</h3>")
        price_label.setAlignment(Qt.AlignCenter)
        price_label.setStyleSheet("color: #2E86AB; font-weight: bold; font-size:16px;")
        layout.addWidget(price_label)
        
        # Mandatory checkbox for tethered
        if unlock_info['type'] == 'tethered':
            self.tethered_ack = QCheckBox(
                "✅ I understand I must re-run this tool after ANY full reboot"
            )
            self.tethered_ack.setStyleSheet("font-weight: bold; color:#d9534f;")
            layout.addWidget(self.tethered_ack)
        else:
            self.tethered_ack = None
        
        # General terms checkbox
        self.terms_ack = QCheckBox(
            "✅ I own this device or have explicit permission to unlock it"
        )
        layout.addWidget(self.terms_ack)
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        self.btn_confirm = QPushButton(f"Pay ${unlock_info['price']:.2f}")
        self.btn_confirm.setEnabled(False)
        self.btn_confirm.clicked.connect(self.accept)
        self.btn_confirm.setStyleSheet("""
            QPushButton {
                background: #28A745; color: white; padding: 12px 24px;
                border-radius: 5px; font-weight: bold; font-size:14px;
            }
            QPushButton:disabled { background: #ccc; }
            QPushButton:hover { background: #218838; }
        """)
        
        btn_cancel = QPushButton("Cancel")
        btn_cancel.clicked.connect(self.reject)
        btn_cancel.setStyleSheet("""
            QPushButton {
                background: #6c757d; color: white; padding: 12px 24px;
                border-radius: 5px;
            }
        """)
        
        btn_layout.addWidget(self.btn_confirm)
        btn_layout.addWidget(btn_cancel)
        layout.addLayout(btn_layout)
        
        # Enable button only when checkboxes are checked
        def update_button():
            if self.tethered_ack:
                enabled = self.tethered_ack.isChecked() and self.terms_ack.isChecked()
            else:
                enabled = self.terms_ack.isChecked()
            self.btn_confirm.setEnabled(enabled)
        
        if self.tethered_ack:
            self.tethered_ack.stateChanged.connect(update_button)
        self.terms_ack.stateChanged.connect(update_button)
        
        self.setLayout(layout)


class UnlockWorker(QThread):
    """Background worker for unlock operations"""
    log_signal = pyqtSignal(str)
    progress_signal = pyqtSignal(int)
    finished_signal = pyqtSignal(bool)
    
    def __init__(self, unlock_type, unlocker):
        super().__init__()
        self.unlock_type = unlock_type
        self.unlocker = unlocker
    
    def run(self):
        try:
            if self.unlock_type == 'checkm8':
                success = self.unlocker.run_checkm8_unlock()
            elif self.unlock_type == 'palera1n':
                success = self.unlocker.run_tethered_bypass()
            else:
                success = False
            
            self.finished_signal.emit(success)
        except Exception as e:
            self.log_signal.emit(f"❌ Error: {str(e)}")
            self.finished_signal.emit(False)


class MainWindow(QMainWindow):
    """Main Application Window"""
    def __init__(self):
        super().__init__()
        self.device = iOSDevice()
        self.worker = None
        self.base_path = os.path.dirname(os.path.abspath(__file__))
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("OpenUnlock Linux - iOS Device Recovery")
        self.setMinimumSize(900, 700)
        
        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        
        # Header
        header = QLabel("🔓 OpenUnlock Linux")
        header.setFont(QFont("Arial", 24, QFont.Bold))
        header.setAlignment(Qt.AlignCenter)
        header.setStyleSheet("color: #2E86AB; margin: 10px;")
        layout.addWidget(header)
        
        # Subtitle
        subtitle = QLabel("Professional iOS Unlock Tool for Linux")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("color: #666; margin-bottom: 20px;")
        layout.addWidget(subtitle)
        
        # Device Info Group
        device_group = QGroupBox("📱 Device Status")
        device_layout = QVBoxLayout()
        
        self.device_label = QLabel("⚪ No device connected")
        self.device_label.setFont(QFont("Arial", 12))
        device_layout.addWidget(self.device_label)
        
        self.info_label = QLabel("")
        self.info_label.setStyleSheet("color: #666;")
        device_layout.addWidget(self.info_label)
        
        self.unlock_type_label = QLabel("")
        self.unlock_type_label.setStyleSheet("color: #2E86AB; font-weight: bold;")
        device_layout.addWidget(self.unlock_type_label)
        
        device_group.setLayout(device_layout)
        layout.addWidget(device_group)
        
        # Action Buttons
        btn_layout = QHBoxLayout()

        self.btn_detect = QPushButton("🔄 Detect Device")
        self.btn_detect.clicked.connect(self.detect_device)
        self.btn_detect.setStyleSheet("""
            QPushButton {
                background: #17a2b8; color: white; padding: 10px 20px;
                border-radius: 5px; font-weight: bold;
            }
            QPushButton:hover { background: #138496; }
        """)
        btn_layout.addWidget(self.btn_detect)

        self.btn_unlock = QPushButton("🔓 Start Unlock")
        self.btn_unlock.clicked.connect(self.start_unlock)
        self.btn_unlock.setEnabled(False)
        self.btn_unlock.setStyleSheet("""
            QPushButton {
                background: #28A745; color: white; padding: 10px 20px;
                border-radius: 5px; font-weight: bold;
            }
            QPushButton:disabled { background: #ccc; }
            QPushButton:hover { background: #218838; }
        """)
        btn_layout.addWidget(self.btn_unlock)

        self.btn_recovery = QPushButton("🚪 Exit Recovery")
        self.btn_recovery.clicked.connect(self.exit_recovery)
        self.btn_recovery.setStyleSheet("""
            QPushButton {
                background: #ffc107; color: black; padding: 10px 20px;
                border-radius: 5px; font-weight: bold;
            }
            QPushButton:hover { background: #e0a800; }
        """)
        btn_layout.addWidget(self.btn_recovery)

        # TEST BUTTON - Remove before production
        self.btn_test = QPushButton("🧪 Test Tethered UI")
        self.btn_test.clicked.connect(self.test_tethered_ui)
        self.btn_test.setStyleSheet("""
            QPushButton {
                background: #6f42c1; color: white; padding: 10px 20px;
                border-radius: 5px; font-weight: bold;
            }
            QPushButton:hover { background: #5a32a3; }
        """)
        btn_layout.addWidget(self.btn_test)

        layout.addLayout(btn_layout)
        
        # Progress
        self.progress = QProgressBar()
        self.progress.setVisible(False)
        self.progress.setStyleSheet("""
            QProgressBar {
                border: 2px solid #2E86AB; border-radius: 5px;
                text-align: center;
            }
            QProgressBar::chunk {
                background: #2E86AB;
            }
        """)
        layout.addWidget(self.progress)
        
        # Log Output
        log_group = QGroupBox("📜 Activity Log")
        log_layout = QVBoxLayout()
        
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setFont(QFont("Monospace", 9))
        self.log_output.setStyleSheet("background: #f8f9fa;")
        log_layout.addWidget(self.log_output)
        
        log_group.setLayout(log_layout)
        layout.addWidget(log_group)
        
        # Status Bar
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage("Ready - Connect an iPhone to begin")
        
        self.log("✅ Application started")
        self.log("📱 Connect your iPhone and click 'Detect Device'")
    
    def log(self, message):
        """Add message to log output"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_output.append(f"[{timestamp}] {message}")
        self.log_output.verticalScrollBar().setValue(
            self.log_output.verticalScrollBar().maximum()
        )
    
    def detect_device(self):
        """Detect connected iOS device"""
        self.log("🔍 Searching for devices...")
        
        if self.device.is_connected():
            info = self.device.get_device_info()
            if info:
                model = self.device.get_model_name()
                ios = self.device.get_ios_version()
                serial = self.device.get_serial()
                
                self.device_label.setText(f"🟢 {model} Connected")
                self.info_label.setText(
                    f"iOS: {ios} | Serial: {serial[-4:]}**** | Battery: {self.device.get_battery_level()}%"
                )
                
                # Get unlock type
                unlock_info = self.device.get_unlock_type()
                self.unlock_type_label.setText(
                    f"{unlock_info['icon']} {unlock_info['title']} - ${unlock_info['price']:.2f}"
                )
                
                self.btn_unlock.setEnabled(True)
                self.log(f"✅ Device detected: {model} (iOS {ios})")
                self.log(f"💰 Unlock type: {unlock_info['title']}")
                self.statusBar.showMessage("Device connected - Ready to unlock")
            else:
                self.log("❌ Could not get device info")
        else:
            self.device_label.setText("⚪ No device connected")
            self.info_label.setText("")
            self.unlock_type_label.setText("")
            self.btn_unlock.setEnabled(False)
            self.log("⚠️ No iOS device found. Please connect and trust this computer.")
            self.statusBar.showMessage("No device detected")
    
    def start_unlock(self):
        """Start unlock process with confirmation"""
        # Get unlock type
        unlock_info = self.device.get_unlock_type()
        
        # Show pre-payment confirmation
        dialog = PurchaseConfirmationDialog(self, unlock_info, self.device)
        if dialog.exec_() != QDialog.Accepted:
            self.log("💰 Purchase cancelled by user")
            return
        
        # Log the purchase agreement
        self.log_purchase_agreement(unlock_info)
        
        # Process payment (simulate for now)
        self.log(f"💳 Processing payment of ${unlock_info['price']:.2f}...")
        # TODO: Integrate Stripe/PayPal/Flutterwave here
        
        # Start unlock process
        self.btn_unlock.setEnabled(False)
        self.progress.setVisible(True)
        self.progress.setValue(0)
        
        # Create unlocker
        unlocker = Unlocker(callback=self.log)
        
        # Start worker thread
        self.worker = UnlockWorker(unlock_info['method'], unlocker)
        self.worker.log_signal.connect(self.log)
        self.worker.finished_signal.connect(self.unlock_finished)
        self.worker.start()
        
        self.log("🚀 Unlock process started...")
    
    def unlock_finished(self, success):
        """Handle unlock completion"""
        self.progress.setVisible(False)
        self.btn_unlock.setEnabled(True)
        
        if success:
            self.log("✅ Unlock completed successfully!")
            QMessageBox.information(self, "Success", 
                "Device unlocked successfully!\n\nThank you for using OpenUnlock Linux.")
        else:
            self.log("❌ Unlock process failed")
            QMessageBox.warning(self, "Warning", 
                "Unlock process failed. Check logs for details.\n\nSupport: support@openunlock.com")
        
        self.statusBar.showMessage("Process complete")
    
    def exit_recovery(self):
        """Exit recovery mode"""
        self.log("🚪 Exiting recovery mode...")
        
        if self.device.exit_recovery():
            self.log("✅ Device exited recovery mode")
            QMessageBox.information(self, "Success", "Device exited recovery mode")
        else:
            self.log("❌ Failed to exit recovery mode")
            QMessageBox.warning(self, "Error", "Failed to exit recovery mode")
    
    def log_purchase_agreement(self, unlock_info):
        """Record customer acknowledgment for legal protection"""
        timestamp = datetime.now().isoformat()
        log_entry = f"""
[PURCHASE AGREEMENT]
Time: {timestamp}
Device: {self.device.get_model_name()}
iOS: {self.device.get_ios_version()}
Unlock Type: {unlock_info['type']}
Price: ${unlock_info['price']}
Method: {unlock_info['method']}
Tethered Acknowledged: {unlock_info['type'] != 'tethered' or True}
Terms Acknowledged: True
"""
        
        # Save to log file
        logs_dir = os.path.join(self.base_path, 'logs')
        os.makedirs(logs_dir, exist_ok=True)
        
        with open(os.path.join(logs_dir, 'purchase_logs.txt'), 'a') as f:
            f.write(log_entry + "\n" + "-"*50 + "\n")
        
        self.log("📄 Purchase agreement logged")
    
    def test_tethered_ui(self):
        """Force tethered mode for UI testing - REMOVE BEFORE PRODUCTION"""
        test_info = {
            'type': 'tethered',
            'price': 14.99,
            'title': '⚠️ Tethered Bypass (TEST)',
            'description': 'Testing UI flow - Works after sleep/wake. MUST re-run after reboot.',
            'icon': '🔄',
            'warning': '🧪 TEST MODE: This simulates tethered bypass. In production, only shows for iPhone XS/XR on iOS 15.0-16.3.1',
            'method': 'palera1n'
        }
        
        dialog = PurchaseConfirmationDialog(self, test_info, self.device)
        if dialog.exec_() == QDialog.Accepted:
            self.log("✅ Tethered UI test passed!")
            self.log("⚠️ In production, this would run palera1n jailbreak")
            QMessageBox.information(
                self, "Test Complete",
                "Tethered confirmation dialog works correctly!\n\n"
                "Key features verified:\n"
                "• Warning box visible\n"
                "• Two checkboxes required\n"
                "• Pay button disabled until both checked"
            )


def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # Modern look
    
    # Show disclaimer first
    disclaimer = DisclaimerDialog()
    if disclaimer.exec_() == QDialog.Rejected:
        sys.exit(0)
    
    # Show main window
