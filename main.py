import sys
import os
import json
import xml.etree.ElementTree as ET
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QFileDialog,
    QLineEdit, QLabel, QComboBox, QCheckBox, QMessageBox, QHBoxLayout,
    QTabWidget, QGroupBox, QScrollArea, QInputDialog, QToolTip
)
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtCore import Qt

SETTINGS_FILE = 'settings.json'
ICON_PATH = 'icon.ico'

class AltVLauncher(QWidget):
    def __init__(self):
        super().__init__()

        self.profiles = {}
        self.current_profile = None
        self.altv_folder = ''

        self.initUI()
        self.load_settings()

    def initUI(self):
        self.setStyleSheet("""
            QWidget {
                font-family: Arial;
                font-size: 14px;
            }
            QGroupBox {
                font-weight: bold;
                border: 1px solid #AAAAAA;
                border-radius: 5px;
                margin-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 3px;
            }
            QPushButton {
                background-color: #5A9BD5;
                color: white;
                padding: 5px 10px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #4A89C7;
            }
            QPushButton:pressed {
                background-color: #3A79B7;
            }
            QLineEdit, QComboBox {
                border: 1px solid #CCCCCC;
                border-radius: 4px;
                padding: 4px;
            }
            QCheckBox, QLabel {
                padding: 2px;
            }
            QTabWidget::pane {
                border: 1px solid #AAAAAA;
                border-radius: 5px;
            }
            QTabBar::tab {
                background: #E0E0E0;
                border: 1px solid #AAAAAA;
                padding: 5px;
                margin: 1px;
            }
            QTabBar::tab:selected {
                background: #FFFFFF;
                border-bottom-color: #FFFFFF;
            }
        """)

        main_layout = QVBoxLayout()

        # alt:V Folder Path (Global Setting)
        folder_path_group = QGroupBox('alt:V Folder')
        folder_path_layout = QHBoxLayout()
        self.folder_path_input = QLineEdit(self)
        self.folder_path_input.setPlaceholderText('Path to alt:V folder')
        self.folder_path_input.setToolTip('Select the folder where altv.exe is located.')
        self.folder_path_input.textChanged.connect(self.save_settings)
        folder_path_btn = QPushButton('...', self)
        folder_path_btn.setIcon(QIcon.fromTheme('folder-open'))
        folder_path_btn.setToolTip('Browse for alt:V folder.')
        folder_path_btn.clicked.connect(self.browse_folder_path)
        folder_path_layout.addWidget(self.folder_path_input)
        folder_path_layout.addWidget(folder_path_btn)
        folder_path_group.setLayout(folder_path_layout)
        main_layout.addWidget(folder_path_group)

        # Profile Tabs
        self.profile_tabs = QTabWidget()
        self.profile_tabs.setTabsClosable(True)
        self.profile_tabs.tabCloseRequested.connect(self.delete_profile)
        self.profile_tabs.currentChanged.connect(self.change_profile)
        main_layout.addWidget(self.profile_tabs)

        # Profile Management Buttons
        profile_btn_layout = QHBoxLayout()
        self.add_profile_btn = QPushButton('Add Profile', self)
        self.add_profile_btn.setIcon(QIcon.fromTheme('list-add'))
        self.add_profile_btn.clicked.connect(self.add_profile)
        self.import_profile_btn = QPushButton('Import Profile', self)
        self.import_profile_btn.setIcon(QIcon.fromTheme('document-open'))
        self.import_profile_btn.clicked.connect(self.import_profile)
        self.export_profile_btn = QPushButton('Export Profile', self)
        self.export_profile_btn.setIcon(QIcon.fromTheme('document-save'))
        self.export_profile_btn.clicked.connect(self.export_profile)
        profile_btn_layout.addWidget(self.add_profile_btn)
        profile_btn_layout.addWidget(self.import_profile_btn)
        profile_btn_layout.addWidget(self.export_profile_btn)
        main_layout.addLayout(profile_btn_layout)

        # Common Buttons
        self.launch_btn = QPushButton('Launch', self)
        self.launch_btn.setIcon(QIcon.fromTheme('media-playback-start'))
        self.launch_btn.clicked.connect(self.launch)
        main_layout.addWidget(self.launch_btn)

        self.setLayout(main_layout)
        self.setWindowTitle('alt:V Easy Launch')
        self.setWindowIcon(QIcon(ICON_PATH))
        self.resize(700, 600)
        self.show()

    def create_profile_widget(self, profile_name):
        widget = QWidget()
        layout = QVBoxLayout()
        widget.graphics_controls = {}  # Храним элементы управления графикой внутри виджета профиля

        # Scroll Area for settings
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout()

        # Branch Selection
        branch_group = QGroupBox('Branch')
        branch_layout = QHBoxLayout()
        branch_combo = QComboBox(self)
        branch_combo.addItems(['release', 'rc', 'dev'])
        branch_combo.setToolTip('Select the alt:V branch to use.')
        branch_combo.currentIndexChanged.connect(self.save_settings)
        branch_layout.addWidget(branch_combo)
        branch_group.setLayout(branch_layout)
        scroll_layout.addWidget(branch_group)

        # Debug Mode
        debug_group = QGroupBox('Debug Mode')
        debug_layout = QHBoxLayout()
        debug_checkbox = QCheckBox('Enable Debug Mode', self)
        debug_checkbox.setToolTip('Enable or disable debug mode.')
        debug_checkbox.stateChanged.connect(self.save_settings)
        debug_layout.addWidget(debug_checkbox)
        debug_group.setLayout(debug_layout)
        scroll_layout.addWidget(debug_group)

        # Graphics Settings
        graphics_group = QGroupBox('Graphics Settings')
        graphics_layout = QVBoxLayout()

        # Define the important graphics settings
        graphics_settings = {
            'TextureQuality': ('Normal', 'High', 'Very High'),
            'ShaderQuality': ('Normal', 'High', 'Very High'),
            'ShadowQuality': ('Normal', 'High', 'Very High'),
            'ReflectionQuality': ('Normal', 'High', 'Very High'),
            'WaterQuality': ('Normal', 'High', 'Very High'),
            'GrassQuality': ('Normal', 'High', 'Very High', 'Ultra'),
            'AnisotropicFiltering': ('Off', 'x2', 'x4', 'x8', 'x16'),
            'AmbientOcclusion': ('Off', 'Normal', 'High'),
            'AntiAliasing': ('Off', 'FXAA', 'MSAA x2', 'MSAA x4', 'MSAA x8'),
            'VSync': ('Off', 'On')
        }

        # Используем widget.graphics_controls вместо self.graphics_controls
        for setting, options in graphics_settings.items():
            setting_layout = QHBoxLayout()
            label = QLabel(setting.replace('Quality', ' Quality'), self)
            label.setToolTip(f'Select the {setting.replace("Quality", " quality").lower()}.')
            combo = QComboBox(self)
            combo.addItems(options)
            combo.setToolTip(f'Select the {setting.replace("Quality", " quality").lower()}.')
            combo.currentIndexChanged.connect(self.save_settings)
            setting_layout.addWidget(label)
            setting_layout.addStretch()
            setting_layout.addWidget(combo)
            graphics_layout.addLayout(setting_layout)
            widget.graphics_controls[setting] = combo  # Храним контролы в виджете профиля

        graphics_group.setLayout(graphics_layout)
        scroll_layout.addWidget(graphics_group)

        scroll_widget.setLayout(scroll_layout)
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(scroll_widget)
        layout.addWidget(scroll_area)

        widget.setLayout(layout)
        return widget

    def browse_folder_path(self):
        folder_path = QFileDialog.getExistingDirectory(self, 'Select alt:V folder')
        if folder_path:
            self.folder_path_input.setText(folder_path)
            self.altv_folder = folder_path
            self.save_settings()

    def add_profile(self):
        profile_name, ok = QInputDialog.getText(self, 'Create Profile', 'Enter profile name:')
        if ok and profile_name:
            if profile_name in self.profiles:
                self.show_error_message('Profile already exists.')
                return
            self.profiles[profile_name] = {}
            profile_widget = self.create_profile_widget(profile_name)
            self.profile_tabs.addTab(profile_widget, profile_name)
            self.profile_tabs.setCurrentWidget(profile_widget)
            self.current_profile = profile_name
            self.save_settings()

    def delete_profile(self, index):
        if index >= 0:
            profile_name = self.profile_tabs.tabText(index)
            del self.profiles[profile_name]
            self.profile_tabs.removeTab(index)
            if self.profile_tabs.count() > 0:
                self.current_profile = self.profile_tabs.tabText(0)
            else:
                self.current_profile = None
            self.save_settings()

    def change_profile(self, index):
        if index >= 0:
            self.current_profile = self.profile_tabs.tabText(index)
            self.save_settings()
        else:
            self.current_profile = None

    def import_profile(self):
        file_name, _ = QFileDialog.getOpenFileName(self, 'Import Profile', '', 'JSON Files (*.json)')
        if file_name:
            try:
                with open(file_name, 'r') as file:
                    profile_data = json.load(file)
                    profile_name = os.path.basename(file_name).split('.')[0]
                    if profile_name in self.profiles:
                        self.show_error_message('Profile with this name already exists.')
                        return
                    self.profiles[profile_name] = profile_data
                    profile_widget = self.create_profile_widget(profile_name)
                    self.profile_tabs.addTab(profile_widget, profile_name)
                    self.profile_tabs.setCurrentWidget(profile_widget)
                    self.current_profile = profile_name
                    self.load_profile_settings(self.profile_tabs.currentIndex(), profile_data)
                    self.save_settings()
            except Exception as e:
                self.show_error_message(f'Failed to import profile: {e}')

    def export_profile(self):
        if self.current_profile:
            file_name, _ = QFileDialog.getSaveFileName(self, 'Export Profile', f'{self.current_profile}.json', 'JSON Files (*.json)')
            if file_name:
                try:
                    with open(file_name, 'w') as file:
                        json.dump(self.profiles[self.current_profile], file, indent=4)
                except Exception as e:
                    self.show_error_message(f'Failed to export profile: {e}')
        else:
            self.show_error_message('No profile selected.')

    def toggle_debug_mode(self, debug_checkbox):
        toml_path = os.path.join(self.altv_folder, 'altv.toml')

        if not os.path.exists(toml_path):
            self.show_error_message('altv.toml not found in the specified folder.')
            return

        try:
            with open(toml_path, 'r') as file:
                lines = file.readlines()

            new_lines = []
            debug_mode = debug_checkbox.isChecked()
            debug_set = False
            for line in lines:
                if line.strip().startswith('debug'):
                    new_lines.append(f'debug = {str(debug_mode).lower()}\n')
                    debug_set = True
                else:
                    new_lines.append(line)

            if not debug_set:
                new_lines.append(f'debug = {str(debug_mode).lower()}\n')

            with open(toml_path, 'w') as file:
                file.writelines(new_lines)
        except Exception as e:
            self.show_error_message(f'Failed to update altv.toml: {e}')

    def switch_branch(self, branch_combo):
        toml_path = os.path.join(self.altv_folder, 'altv.toml')
        branch_name = branch_combo.currentText()

        if not os.path.exists(toml_path):
            self.show_error_message('altv.toml not found in the specified folder.')
            return

        try:
            with open(toml_path, 'r') as file:
                lines = file.readlines()

            new_lines = []
            branch_set = False
            for line in lines:
                if line.strip().startswith('branch'):
                    new_lines.append(f'branch = "{branch_name}"\n')
                    branch_set = True
                else:
                    new_lines.append(line)

            if not branch_set:
                new_lines.append(f'branch = "{branch_name}"\n')

            with open(toml_path, 'w') as file:
                file.writelines(new_lines)
        except Exception as e:
            self.show_error_message(f'Failed to update altv.toml: {e}')

    def apply_graphics_settings(self, graphics_controls):
    # Get the path to the GTA 5 settings.xml file
        settings_path = os.path.join(os.environ['USERPROFILE'], 'Documents', 'Rockstar Games', 'GTA V', 'settings.xml')

        if not os.path.exists(settings_path):
            self.show_error_message('GTA V settings.xml not found in Documents.')
            return

        try:
            tree = ET.parse(settings_path)
            root = tree.getroot()

            # Update graphics settings based on user input

            # Update settings in the <graphics> section
            graphics_elem = root.find('graphics')
            if graphics_elem is not None:
                for setting, combo in graphics_controls.items():
                    value = combo.currentText()
                    xml_tag = self.get_xml_tag_for_setting(setting)
                    if xml_tag:
                        elem = graphics_elem.find(xml_tag)
                        if elem is not None:
                            elem.set('value', self.get_xml_value_for_setting(setting, value))
                        else:
                            # Create the element if it doesn't exist
                            ET.SubElement(graphics_elem, xml_tag, {'value': self.get_xml_value_for_setting(setting, value)})

            # Update settings in the <video> section
            video_elem = root.find('video')
            if video_elem is not None:
                for setting, combo in graphics_controls.items():
                    if setting == 'VSync':
                        value = combo.currentText()
                        xml_tag = self.get_xml_tag_for_setting(setting)
                        if xml_tag:
                            elem = video_elem.find(xml_tag)
                            if elem is not None:
                                elem.set('value', self.get_xml_value_for_setting(setting, value))
                            else:
                                # Create the element if it doesn't exist
                                ET.SubElement(video_elem, xml_tag, {'value': self.get_xml_value_for_setting(setting, value)})

            # Special handling for AntiAliasing (FXAA and MSAA)
            msaa_value = graphics_controls['AntiAliasing'].currentText()
            if msaa_value.startswith('MSAA'):
                msaa_level = self.get_xml_value_for_setting('AntiAliasing', msaa_value)
                fxaa_enabled = 'false'
            elif msaa_value == 'FXAA':
                msaa_level = '0'
                fxaa_enabled = 'true'
            else:
                msaa_level = '0'
                fxaa_enabled = 'false'

            # Update MSAA in <graphics>
            msaa_elem = graphics_elem.find('MSAA')
            if msaa_elem is not None:
                msaa_elem.set('value', msaa_level)
            else:
                ET.SubElement(graphics_elem, 'MSAA', {'value': msaa_level})

            # Update FXAA_Enabled in <graphics>
            fxaa_elem = graphics_elem.find('FXAA_Enabled')
            if fxaa_elem is not None:
                fxaa_elem.set('value', fxaa_enabled)
            else:
                ET.SubElement(graphics_elem, 'FXAA_Enabled', {'value': fxaa_enabled})

            # Save the modified settings.xml
            tree.write(settings_path, encoding='UTF-8', xml_declaration=True)
        except Exception as e:
            self.show_error_message(f'Failed to write graphics settings: {e}')

    def get_xml_tag_for_setting(self, setting):
    # Map the settings to their corresponding XML tags
        tag_mapping = {
            'TextureQuality': 'TextureQuality',
            'ShaderQuality': 'ShaderQuality',
            'ShadowQuality': 'ShadowQuality',
            'ReflectionQuality': 'ReflectionQuality',
            'WaterQuality': 'WaterQuality',
            'GrassQuality': 'GrassQuality',
            'AnisotropicFiltering': 'AnisotropicFiltering',
            'AmbientOcclusion': 'SSAO',  # В вашем settings.xml это называется SSAO
            'VSync': 'VSync',
        }
        return tag_mapping.get(setting)



    def get_xml_value_for_setting(self, setting, value):
        # Convert user-friendly values to XML values
        value_mapping = {
            'Off': '0',
            'On': '1',
            'FXAA': '1',
            'MSAA x2': '2',
            'MSAA x4': '4',
            'MSAA x8': '8',
            'Normal': '0',
            'High': '1',
            'Very High': '2',
            'Ultra': '3',
            'x2': '2',
            'x4': '4',
            'x8': '8',
            'x16': '16',
            'false': 'false',
            'true': 'true',
        }
        return value_mapping.get(value, '0')

    def launch(self):
        if self.current_profile is None:
            self.show_error_message('No profile selected.')
            return

        if not self.altv_folder:
            self.show_error_message('alt:V folder path is empty.')
            return

        index = self.profile_tabs.currentIndex()
        profile_widget = self.profile_tabs.widget(index)
        layout = profile_widget.layout()
        scroll_area = layout.itemAt(0).widget()
        scroll_widget = scroll_area.widget()
        scroll_layout = scroll_widget.layout()

        # Retrieve controls
        branch_group = scroll_layout.itemAt(0).widget()
        branch_combo = branch_group.layout().itemAt(0).widget()
        debug_group = scroll_layout.itemAt(1).widget()
        debug_checkbox = debug_group.layout().itemAt(0).widget()

        self.toggle_debug_mode(debug_checkbox)
        self.switch_branch(branch_combo)
        self.apply_graphics_settings(profile_widget.graphics_controls)

        exe_path = os.path.join(self.altv_folder, 'altv.exe')

        if not os.path.exists(exe_path):
            self.show_error_message('altv.exe not found in the specified folder.')
            return

        os.system(f'start "" "{exe_path}"')

    def load_settings(self):
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, 'r') as file:
                data = json.load(file)
                self.profiles = data.get('profiles', {})
                self.altv_folder = data.get('altv_folder', '')
                self.folder_path_input.setText(self.altv_folder)
                last_profile = data.get('last_selected_profile', '')

                for profile_name in self.profiles:
                    profile_widget = self.create_profile_widget(profile_name)
                    self.profile_tabs.addTab(profile_widget, profile_name)
                    index = self.profile_tabs.indexOf(profile_widget)
                    self.load_profile_settings(index, self.profiles[profile_name])

                if last_profile in self.profiles:
                    # Найдем индекс вкладки с последним выбранным профилем
                    for i in range(self.profile_tabs.count()):
                        if self.profile_tabs.tabText(i) == last_profile:
                            self.profile_tabs.setCurrentIndex(i)
                            self.current_profile = last_profile
                            break
                elif self.profile_tabs.count() > 0:
                    self.current_profile = self.profile_tabs.tabText(0)
                else:
                    self.current_profile = None


    def save_settings(self):
        # Gather settings from all profiles
        for index in range(self.profile_tabs.count()):
            profile_name = self.profile_tabs.tabText(index)
            profile_widget = self.profile_tabs.widget(index)
            layout = profile_widget.layout()
            scroll_area = layout.itemAt(0).widget()
            scroll_widget = scroll_area.widget()
            scroll_layout = scroll_widget.layout()

            # Retrieve controls
            branch_group = scroll_layout.itemAt(0).widget()
            branch_combo = branch_group.layout().itemAt(0).widget()
            debug_group = scroll_layout.itemAt(1).widget()
            debug_checkbox = debug_group.layout().itemAt(0).widget()

            graphics_settings = {}
            for setting, combo in profile_widget.graphics_controls.items():
                graphics_settings[setting] = combo.currentText()

            self.profiles[profile_name] = {
                'branch': branch_combo.currentText(),
                'debug_mode': debug_checkbox.isChecked(),
                'graphics_settings': graphics_settings
            }

        data = {
            'altv_folder': self.folder_path_input.text(),
            'last_selected_profile': self.current_profile,
            'profiles': self.profiles
        }

        with open(SETTINGS_FILE, 'w') as file:
            json.dump(data, file, indent=4)

    def load_profile_settings(self, index, settings):
        profile_widget = self.profile_tabs.widget(index)
        layout = profile_widget.layout()
        scroll_area = layout.itemAt(0).widget()
        scroll_widget = scroll_area.widget()
        scroll_layout = scroll_widget.layout()

        # Retrieve controls
        branch_group = scroll_layout.itemAt(0).widget()
        branch_combo = branch_group.layout().itemAt(0).widget()
        debug_group = scroll_layout.itemAt(1).widget()
        debug_checkbox = debug_group.layout().itemAt(0).widget()

        branch = settings.get('branch', '')
        if branch in ['release', 'rc', 'dev']:
            branch_combo.setCurrentText(branch)
        debug_checkbox.setChecked(settings.get('debug_mode', False))

        graphics_settings = settings.get('graphics_settings', {})
        for setting, value in graphics_settings.items():
            if setting in profile_widget.graphics_controls:
                profile_widget.graphics_controls[setting].setCurrentText(value)

    def closeEvent(self, event):
        self.save_settings()
        event.accept()

    def show_error_message(self, message):
        QMessageBox.critical(self, 'Error', message)

def main():
    app = QApplication(sys.argv)
    ex = AltVLauncher()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
