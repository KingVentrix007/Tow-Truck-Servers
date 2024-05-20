import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QTextEdit, QListWidget, QVBoxLayout, QWidget, QListWidgetItem, QTabWidget
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from PyQt5.QtGui import QTextCursor
import re
import subprocess
import time

missing_mods_list = []

def extract_missing_mod(line):
    pattern = r"Mod ID: '(.*?)', Requested by: '(.*?)', Expected range: '\[(.*?)\)', Actual version: '\[MISSING\]'"
    match = re.match(pattern, line)
    if match:
        return line.strip(), match.group(1), match.group(3)  # Return the full line, mod ID, and expected range
    else:
        return None

class OutputWindow(QTextEdit):
    def __init__(self):
        super().__init__()
        self.setReadOnly(True)

    def append_with_format(self, text, color):
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.End)
        cursor.insertHtml(f'<font color="{color}">{text}</font><br>')
        self.ensureCursorVisible()

class MissingModsWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        # Create a text edit for missing mods
        self.missing_mods_textedit = QTextEdit(self)
        self.missing_mods_textedit.setReadOnly(True)
        layout.addWidget(self.missing_mods_textedit)

        # Create a list widget for missing mods
        self.missing_mods_list = QListWidget(self)
        layout.addWidget(self.missing_mods_list)

        self.setLayout(layout)

        self.missing_mods = set()  # Set to store missing mods

    def add_missing_mod(self, missing_mod, mod_id, expected_range):
        if missing_mod not in self.missing_mods:
            self.missing_mods.add(missing_mod)
            self.missing_mods_textedit.append(missing_mod)
            item = QListWidgetItem(f"{mod_id}")
            if(mod_id not in missing_mods_list):

                self.missing_mods_list.addItem(item)
                missing_mods_list.append(mod_id)

class ExecuteBatThread(QThread):
    update_output = pyqtSignal(str, str)
    add_missing_mod = pyqtSignal(str, str, str)

    def __init__(self):
        super().__init__()
        self.proc = None

    def run(self):
        self.proc = subprocess.Popen(['sample.bat'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True, bufsize=1, universal_newlines=True)
        for line in self.proc.stdout:
            line_str = line.rstrip()
            if "Missing or unsupported mandatory dependencies:" in line_str:
                self.update_output.emit("[EZ Server Warning]:" + line_str, "red")
            elif "ERROR]" in line_str:
                self.update_output.emit(line_str, "red")
            elif "INFO]" in line_str:
                self.update_output.emit(line_str, "green")
            elif "WARN]" in line_str:
                self.update_output.emit(line_str, "orange")
            elif "FATAL]" in line_str:
                self.update_output.emit(line_str, "red")
            else:
                missing_mod_info = extract_missing_mod(line_str)
                if missing_mod_info:
                    self.update_output.emit(line_str, "black")
                    self.add_missing_mod.emit(*missing_mod_info)
            time.sleep(0.1)  # Throttle the rate of output

    def stop(self):
        if self.proc:
            self.proc.terminate()
            self.proc = None

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Output and Missing Mods')

        # Create a tab widget
        self.tab_widget = QTabWidget()

        # Create tabs
        self.output_tab = OutputWindow()
        self.missing_mods_tab = MissingModsWindow()

        # Add tabs to the tab widget
        self.tab_widget.addTab(self.output_tab, 'Output')
        self.tab_widget.addTab(self.missing_mods_tab, 'Missing Mods')

        self.setCentralWidget(self.tab_widget)

    def closeEvent(self, event):
        self.execute_thread.stop()
        event.accept()

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()

    window.execute_thread = ExecuteBatThread()
    window.execute_thread.update_output.connect(window.output_tab.append_with_format)
    window.execute_thread.add_missing_mod.connect(window.missing_mods_tab.add_missing_mod)
    window.execute_thread.start()

    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
