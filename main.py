import sys
import os
import json
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QFileDialog, QLineEdit, QLabel, QComboBox, QCheckBox, QMessageBox, QHBoxLayout
from PyQt5.QtGui import QIcon

SETTINGS_FILE = 'settings.json'
ICON_PATH = 'icon.ico'  

class AltVLauncher(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()
        self.load_settings()

    def initUI(self):
        layout = QVBoxLayout()

        self.folder_path_layout = QHBoxLayout()
        self.folder_path_input = QLineEdit(self)
        self.folder_path_input.setPlaceholderText('Path to alt:V folder')
        self.folder_path_btn = QPushButton('...', self)
        self.folder_path_btn.clicked.connect(self.browse_folder_path)
        self.folder_path_layout.addWidget(self.folder_path_input)
        self.folder_path_layout.addWidget(self.folder_path_btn)
        layout.addLayout(self.folder_path_layout)

        self.branch_combo = QComboBox(self)
        self.branch_combo.addItems(['release', 'rc', 'dev'])
        layout.addWidget(self.branch_combo)

        self.debug_checkbox = QCheckBox('Debug Mode', self)
        layout.addWidget(self.debug_checkbox)

        self.launch_btn = QPushButton('Launch', self)
        self.launch_btn.clicked.connect(self.launch)
        layout.addWidget(self.launch_btn)

        self.setLayout(layout)
        self.setWindowTitle('alt:V Easy Launch')
        self.setWindowIcon(QIcon(ICON_PATH))
        self.show()

    def browse_folder_path(self):
        folder_path = QFileDialog.getExistingDirectory(self, 'Select alt:V folder')
        if folder_path:
            self.folder_path_input.setText(folder_path)

    def toggle_debug_mode(self):
        folder_path = self.folder_path_input.text()
        toml_path = os.path.join(folder_path, 'altv.toml')

        if not os.path.exists(toml_path):
            self.show_error_message('altv.toml not found in the specified folder.')
            return

        with open(toml_path, 'r') as file:
            lines = file.readlines()

        new_lines = []
        debug_mode = self.debug_checkbox.isChecked()
        for line in lines:
            if line.startswith('debug'):
                new_lines.append(f'debug = {str(debug_mode).lower()}\n')
            else:
                new_lines.append(line)

        with open(toml_path, 'w') as file:
            file.writelines(new_lines)

    def switch_branch(self):
        folder_path = self.folder_path_input.text()
        toml_path = os.path.join(folder_path, 'altv.toml')
        branch_name = self.branch_combo.currentText()

        if not os.path.exists(toml_path):
            self.show_error_message('altv.toml not found in the specified folder.')
            return

        with open(toml_path, 'r') as file:
            lines = file.readlines()

        new_lines = []
        for line in lines:
            if line.startswith('branch'):
                new_lines.append(f'branch = "{branch_name}"\n')
            else:
                new_lines.append(line)

        with open(toml_path, 'w') as file:
            file.writelines(new_lines)

    def launch(self):
        self.toggle_debug_mode()
        self.switch_branch()

        folder_path = self.folder_path_input.text()
        exe_path = os.path.join(folder_path, 'altv.exe')

        if not os.path.exists(exe_path):
            self.show_error_message('altv.exe not found in the specified folder.')
            return

        os.system(f'start {exe_path}')

    def load_settings(self):
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, 'r') as file:
                settings = json.load(file)
                self.folder_path_input.setText(settings.get('folder_path', ''))
                branch = settings.get('branch', '')
                if branch in ['release', 'rc', 'dev']:
                    self.branch_combo.setCurrentText(branch)
                self.debug_checkbox.setChecked(settings.get('debug_mode', False))

    def save_settings(self):
        settings = {
            'folder_path': self.folder_path_input.text(),
            'branch': self.branch_combo.currentText(),
            'debug_mode': self.debug_checkbox.isChecked(),
        }
        with open(SETTINGS_FILE, 'w') as file:
            json.dump(settings, file)

    def closeEvent(self, event):
        self.save_settings()
        event.accept()

    def show_error_message(self, message):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setText(message)
        msg.setWindowTitle('Error')
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()

def main():
    app = QApplication(sys.argv)
    ex = AltVLauncher()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
