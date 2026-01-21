import sys
import json
import os
import glob
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QListWidget, QLineEdit, QLabel, 
                             QPushButton, QMessageBox,
                             QComboBox, QRadioButton, QButtonGroup, QFrame)
from PyQt6.QtCore import Qt

CONFIG_FILE = "config.json"

STYLESHEET = """
QMainWindow {
    background-color: #181825; /* Очень темный фон подложки */
}
QWidget {
    color: #cdd6f4;
    font-family: 'Segoe UI', 'Roboto', sans-serif;
    font-size: 14px;
}

/* КАРТОЧКИ (ЛЕВАЯ И ПРАВАЯ ПАНЕЛИ) */
QFrame#Panel {
    background-color: #1e1e2e; /* Цвет карточек */
    border-radius: 20px;       /* СИЛЬНОЕ ЗАКРУГЛЕНИЕ БЛОКОВ */
    border: 1px solid #313244;
}

/* ЗАГОЛОВКИ ВНУТРИ БЛОКОВ */
QLabel#Header {
    font-size: 16px;
    font-weight: bold;
    color: #89b4fa;
    margin-bottom: 10px;
}

/* СПИСОК */
QListWidget {
    background-color: #252535; /* Чуть светлее фона карточки */
    border: none;
    border-radius: 12px;
    padding: 8px;
    outline: none;
}
QListWidget::item {
    padding: 14px;
    margin-bottom: 6px;
    border-radius: 10px;
    color: #a6adc8;
}
QListWidget::item:selected {
    background-color: #3b82f6;
    color: white;
    font-weight: bold;
}
QListWidget::item:hover {
    background-color: #313244;
}

/* ПОЛЯ ВВОДА */
QLineEdit, QComboBox {
    background-color: #252535;
    border: 1px solid #45475a;
    border-radius: 12px; /* Закругленные поля */
    padding: 0 15px;
    color: white;
    min-height: 45px; /* Высокие поля */
}
QLineEdit:focus, QComboBox:focus {
    border: 1px solid #89b4fa;
    background-color: #2a2a3d;
}

/* РАДИО КНОПКИ */
QRadioButton {
    spacing: 12px;
    font-weight: 500;
}
QRadioButton::indicator {
    width: 22px;
    height: 22px;
    border-radius: 12px;
    border: 2px solid #585b70;
}
QRadioButton::indicator:checked {
    background-color: #3b82f6;
    border-color: #3b82f6;
}

/* ОБЫЧНЫЕ КНОПКИ (Добавить/Удалить) */
QPushButton {
    border-radius: 12px;
    font-weight: bold;
    min-height: 40px;
}
QPushButton#btnAdd {
    background-color: transparent;
    color: #a6e3a1;
    border: 2px solid #313244;
}
QPushButton#btnAdd:hover {
    background-color: #a6e3a1;
    color: #1e1e2e;
    border: 2px solid #a6e3a1;
}
QPushButton#btnDel {
    background-color: transparent;
    color: #f38ba8;
    border: 2px solid #313244;
}
QPushButton#btnDel:hover {
    background-color: #f38ba8;
    color: #1e1e2e;
    border: 2px solid #f38ba8;
}

/* КНОПКА СОХРАНЕНИЯ (ОБВОДКА) */
QPushButton#btnSave {
    background-color: transparent;
    color: #3b82f6;
    border: 3px solid #3b82f6; /* Жирная обводка */
    border-radius: 16px;       /* Круглая кнопка */
    font-size: 16px;
    font-weight: 800;
    min-height: 55px;
    margin-top: 10px;
}
QPushButton#btnSave:hover {
    background-color: #3b82f6;
    color: white;
}
QPushButton#btnSave:pressed {
    background-color: #2563eb;
    border-color: #2563eb;
}
"""

class ConfigEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("G.O.S.H.A Config Editor")
        self.resize(1100, 750)
        
        self.config_data = {}
        self.commands = []
        self.linux_apps = self.scan_linux_apps()
        self.current_index = -1

        self.setStyleSheet(STYLESHEET)

        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        main_layout = QHBoxLayout(main_widget)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(30)

        left_frame = QFrame()
        left_frame.setObjectName("Panel")
        left_layout = QVBoxLayout(left_frame)
        left_layout.setContentsMargins(20, 25, 20, 20)
        left_layout.setSpacing(15)

        lbl_list = QLabel("СПИСОК КОМАНД")
        lbl_list.setObjectName("Header")
        lbl_list.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.cmd_list_widget = QListWidget()
        self.cmd_list_widget.currentRowChanged.connect(self.load_command_to_form)
        
        btn_layout = QHBoxLayout()
        btn_add = QPushButton("+ Добавить")
        btn_add.setObjectName("btnAdd")
        btn_add.clicked.connect(self.add_command)

        btn_del = QPushButton("− Удалить")
        btn_del.setObjectName("btnDel")
        btn_del.clicked.connect(self.delete_command)

        btn_layout.addWidget(btn_add)
        btn_layout.addWidget(btn_del)

        left_layout.addWidget(lbl_list)
        left_layout.addWidget(self.cmd_list_widget)
        left_layout.addLayout(btn_layout)

        right_frame = QFrame()
        right_frame.setObjectName("Panel")
        right_layout = QVBoxLayout(right_frame)
        right_layout.setContentsMargins(30, 30, 30, 30)
        right_layout.setSpacing(20)

        lbl_edit = QLabel("РЕДАКТИРОВАНИЕ")
        lbl_edit.setObjectName("Header")
        right_layout.addWidget(lbl_edit)
        
        right_layout.addWidget(QLabel("Слова-триггеры (через запятую):"))
        self.input_triggers = QLineEdit()
        self.input_triggers.setPlaceholderText("Пример: браузер, firefox")
        right_layout.addWidget(self.input_triggers)

        right_layout.addWidget(QLabel("Голосовой ответ:"))
        self.input_response = QLineEdit()
        self.input_response.setPlaceholderText("Пример: Запускаю браузер")
        right_layout.addWidget(self.input_response)

        right_layout.addSpacing(10)

        right_layout.addWidget(QLabel("Что делать:"))
        radio_layout = QHBoxLayout()
        self.radio_manual = QRadioButton("Своя команда")
        self.radio_app = QRadioButton("Приложение Linux")
        radio_layout.addWidget(self.radio_manual)
        radio_layout.addWidget(self.radio_app)
        radio_layout.addStretch()
        right_layout.addLayout(radio_layout)

        self.btn_group = QButtonGroup()
        self.btn_group.addButton(self.radio_manual)
        self.btn_group.addButton(self.radio_app)

        self.lbl_app = QLabel("Выберите приложение:")
        right_layout.addWidget(self.lbl_app)
        self.combo_apps = QComboBox()
        self.combo_apps.addItems(sorted(self.linux_apps.keys()))
        right_layout.addWidget(self.combo_apps)

        self.lbl_exec = QLabel("Итоговая команда (Terminal):")
        right_layout.addWidget(self.lbl_exec)
        self.input_exec = QLineEdit()
        self.input_exec.setPlaceholderText("Например: gnome-terminal -- htop")
        right_layout.addWidget(self.input_exec)

        right_layout.addStretch()

        btn_save = QPushButton("СОХРАНИТЬ КОНФИГ")
        btn_save.setObjectName("btnSave")
        btn_save.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_save.clicked.connect(self.save_config_file)
        right_layout.addWidget(btn_save)

        main_layout.addWidget(left_frame, 1)
        main_layout.addWidget(right_frame, 2)

        self.radio_manual.toggled.connect(self.toggle_exec_mode)
        self.radio_app.toggled.connect(self.toggle_exec_mode)
        self.combo_apps.currentTextChanged.connect(self.on_app_selected)
        
        self.input_triggers.textChanged.connect(self.update_current_data)
        self.input_response.textChanged.connect(self.update_current_data)
        self.input_exec.textChanged.connect(self.update_current_data)

        self.load_config_file()

    def scan_linux_apps(self):
        apps = {}
        paths = ["/usr/share/applications/*.desktop", os.path.expanduser("~/.local/share/applications/*.desktop")]
        for path_pattern in paths:
            for filepath in glob.glob(path_pattern):
                try:
                    name, exec_cmd = None, None
                    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                        for line in f:
                            if line.startswith("Name=") and not name: name = line.strip().split("=")[1]
                            if line.startswith("Exec=") and not exec_cmd: 
                                exec_cmd = line.strip().split("=")[1].split("%")[0].strip()
                    if name and exec_cmd: apps[name] = exec_cmd
                except: pass
        return apps

    def toggle_exec_mode(self):
        is_app = self.radio_app.isChecked()
        
        self.lbl_app.setVisible(is_app)
        self.combo_apps.setVisible(is_app)
        
        self.lbl_exec.setVisible(not is_app)
        self.input_exec.setVisible(not is_app)

        if is_app:
            self.on_app_selected(self.combo_apps.currentText())

    def on_app_selected(self, app_name):
        if self.radio_app.isChecked() and app_name in self.linux_apps:
            self.input_exec.setText(self.linux_apps[app_name])

    def load_config_file(self):
        if not os.path.exists(CONFIG_FILE): return
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            self.config_data = json.load(f)
            self.commands = self.config_data.get("commands", [])
        self.refresh_list()

    def refresh_list(self):
        self.cmd_list_widget.clear()
        for cmd in self.commands:
            triggers = cmd.get("triggers", ["???"])
            main_trigger = triggers[0] if triggers else "Без имени"
            self.cmd_list_widget.addItem(main_trigger)

    def load_command_to_form(self, index):
        if index < 0 or index >= len(self.commands): return
        self.current_index = index
        cmd = self.commands[index]
        
        self.input_triggers.setText(", ".join(cmd.get("triggers", [])))
        self.input_response.setText(cmd.get("response", ""))
        self.input_exec.setText(cmd.get("exec", ""))
        
        exec_val = cmd.get("exec", "")
        if exec_val in self.linux_apps.values():
            self.radio_app.setChecked(True)
            for name, val in self.linux_apps.items():
                if val == exec_val:
                    self.combo_apps.setCurrentText(name)
                    break
        else:
            self.radio_manual.setChecked(True)
        
        self.toggle_exec_mode()

    def update_current_data(self):
        if self.current_index < 0: return
        triggers_list = [t.strip() for t in self.input_triggers.text().split(",") if t.strip()]
        self.commands[self.current_index] = {
            "triggers": triggers_list,
            "response": self.input_response.text(),
            "exec": self.input_exec.text()
        }
        item = self.cmd_list_widget.item(self.current_index)
        if item and triggers_list:
            item.setText(triggers_list[0])

    def add_command(self):
        self.commands.append({"triggers": ["Новая команда"], "response": "", "exec": ""})
        self.refresh_list()
        self.cmd_list_widget.setCurrentRow(len(self.commands) - 1)

    def delete_command(self):
        row = self.cmd_list_widget.currentRow()
        if row >= 0:
            del self.commands[row]
            self.refresh_list()
            if not self.commands: 
                self.input_triggers.clear()
                self.input_response.clear()
                self.input_exec.clear()
                self.current_index = -1

    def save_config_file(self):
        self.config_data["commands"] = self.commands
        try:
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(self.config_data, f, indent=4, ensure_ascii=False)
            msg = QMessageBox(self)
            msg.setWindowTitle("Готово")
            msg.setText("✅ Конфиг сохранен!")
            msg.setStyleSheet("background-color: #1e1e2e; color: white;")
            msg.exec()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ConfigEditor()
    window.show()
    sys.exit(app.exec())