import os
from PyQt5.QtCore import QProcess
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTextEdit,
    QComboBox, QLabel, QFileDialog, QMessageBox, QCheckBox
)

class AppWindow(QWidget):
    def __init__(self, scripts_dir: str):
        super().__init__()
        self.setWindowTitle("Windows Fix Tool (PyQt5)")
        self.resize(900, 560)

        self.scripts_dir = os.path.normpath(scripts_dir)
        os.makedirs(self.scripts_dir, exist_ok=True)

        # --- UI ---
        self.cboScripts = QComboBox()
        self.btnBrowse = QPushButton("Add script…")
        self.btnRun = QPushButton("Run")
        self.btnRefresh = QPushButton("Refresh")
        self.chkPwsh = QCheckBox("Prefer PowerShell 7 (pwsh)")
        self.chkPwsh.setChecked(True)

        self.txtLog = QTextEdit()
        self.txtLog.setReadOnly(True)
        self.txtLog.setLineWrapMode(QTextEdit.NoWrap)

        top = QHBoxLayout()
        top.addWidget(QLabel("Script:"))
        top.addWidget(self.cboScripts, 1)
        top.addWidget(self.btnBrowse)
        top.addWidget(self.btnRefresh)
        top.addWidget(self.chkPwsh)
        top.addWidget(self.btnRun)

        root = QVBoxLayout(self)
        root.addLayout(top)
        root.addWidget(self.txtLog, 1)

        # --- Data ---
        self.refresh_scripts()

        # --- Process (captures output without freezing UI) ---
        self.proc = QProcess(self)
        self.proc.setProcessChannelMode(QProcess.MergedChannels)

        # --- Signals ---
        self.btnRun.clicked.connect(self.on_run)
        self.btnBrowse.clicked.connect(self.on_browse)
        self.btnRefresh.clicked.connect(self.refresh_scripts)
        self.proc.readyReadStandardOutput.connect(self.on_ready_read)
        self.proc.finished.connect(self.on_finished)
        self.proc.errorOccurred.connect(self.on_error)

    # ---------- helpers ----------
    def append_log(self, text: str):
        self.txtLog.moveCursor(self.txtLog.textCursor().End)
        self.txtLog.insertPlainText(text)
        self.txtLog.moveCursor(self.txtLog.textCursor().End)

    def is_on_path(self, exe: str) -> bool:
        for p in os.environ.get("PATH", "").split(os.pathsep):
            full = os.path.join(p.strip('"'), exe)
            if os.path.isfile(full):
                return True
        return False

    def find_ps_host(self, prefer_pwsh: bool) -> str:
        # Prefer PowerShell 7 (pwsh.exe), then Windows PowerShell (powershell.exe)
        order = ["pwsh.exe", "powershell.exe"] if prefer_pwsh else ["powershell.exe", "pwsh.exe"]
        for candidate in order:
            if self.is_on_path(candidate):
                return candidate
        # Fallback to System32 Windows PowerShell
        system_root = os.environ.get("SystemRoot", r"C:\\Windows")
        return os.path.join(system_root, r"System32\WindowsPowerShell\v1.0\powershell.exe")

    def refresh_scripts(self):
        self.cboScripts.clear()
        if os.path.isdir(self.scripts_dir):
            for name in sorted(os.listdir(self.scripts_dir)):
                if name.lower().endswith(".ps1"):
                    self.cboScripts.addItem(os.path.join(self.scripts_dir, name))
        if self.cboScripts.count() == 0:
            self.cboScripts.addItem("<< No .ps1 scripts found in /scripts >>")

    # ---------- slots ----------
    def on_browse(self):
        path, _ = QFileDialog.getOpenFileName(self, "Choose PowerShell script", "", "PowerShell (*.ps1)")
        if not path:
            return
        base = os.path.basename(path)
        dest = os.path.join(self.scripts_dir, base)
        try:
            if os.path.abspath(path) != os.path.abspath(dest):
                import shutil
                shutil.copy2(path, dest)
        except Exception as e:
            QMessageBox.critical(self, "Copy failed", str(e))
            return
        self.refresh_scripts()

    def on_run(self):
        script_path = self.cboScripts.currentText()
        if not (script_path and script_path.lower().endswith(".ps1") and os.path.isfile(script_path)):
            QMessageBox.warning(self, "Select script", "Please select a valid .ps1 script.")
            return

        self.txtLog.clear()
        host = self.find_ps_host(self.chkPwsh.isChecked())
        args = ["-NoProfile", "-ExecutionPolicy", "Bypass", "-File", script_path]

        self.append_log(f"Running: {host} {' '.join(args)}\n\n")
        self.btnRun.setEnabled(False)
        self.proc.start(host, args)

    def on_ready_read(self):
        data = bytes(self.proc.readAllStandardOutput()).decode(errors="replace")
        if data:
            self.append_log(data)

    def on_finished(self, exit_code, exit_status):
        self.append_log(f"\n\nProcess exited with code {exit_code} (status {exit_status}).\n")
        self.btnRun.setEnabled(True)

    def on_error(self, err):
        self.append_log(f"\n[QProcess Error] {err}\n")
        self.btnRun.setEnabled(True)
