import sys
from typing import List

from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QDialog,
    QFormLayout,
    QMainWindow,
    QMenu,
    QMessageBox,
    QPushButton,
    QStatusBar,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

APP_VERSION = "1.0.1"


class LogStream(QObject):
    text_written = Signal(str)

    def __init__(self, original_stream):
        super().__init__()
        self.original_stream = original_stream

    def write(self, message: str):
        self.original_stream.write(message)
        if message.strip():
            self.text_written.emit(message.rstrip("\n"))

    def flush(self):
        self.original_stream.flush()


class InterfaceSettingDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Interface Setting")
        self.setFixedSize(600, 200)

        self.combo_labels = ["Power", "Load", "DVM Voltage", "DVM Current"]
        self.combos: dict[str, QComboBox] = {}

        form = QFormLayout()
        form.setSpacing(12)

        for label in self.combo_labels:
            combo = QComboBox(self)
            combo.currentIndexChanged.connect(self._on_combo_changed)
            self.combos[label] = combo
            form.addRow(f"{label}:", combo)

        self.refresh_button = QPushButton("Refresh", self)
        self.refresh_button.clicked.connect(self.refresh_usb_endpoints)

        layout = QVBoxLayout()
        layout.addLayout(form)
        layout.addWidget(self.refresh_button)
        self.setLayout(layout)

        self.refresh_usb_endpoints()

    def scan_usb_endpoints(self) -> List[str]:
        """Scan USB serial endpoints. Returns endpoint names such as COM3, /dev/ttyUSB0."""
        try:
            from serial.tools import list_ports

            return [port.device for port in list_ports.comports()]
        except Exception:
            return []

    def refresh_usb_endpoints(self):
        endpoints = self.scan_usb_endpoints()

        for combo in self.combos.values():
            current_value = combo.currentText()
            combo.blockSignals(True)
            combo.clear()
            combo.addItem("")
            combo.addItems(endpoints)

            index = combo.findText(current_value)
            combo.setCurrentIndex(index if index >= 0 else 0)
            combo.blockSignals(False)

    def _on_combo_changed(self):
        sender = self.sender()
        if not isinstance(sender, QComboBox):
            return

        selected_endpoint = sender.currentText()
        if not selected_endpoint:
            return

        for combo in self.combos.values():
            if combo is sender:
                continue
            if combo.currentText() == selected_endpoint:
                combo.blockSignals(True)
                combo.setCurrentIndex(0)
                combo.blockSignals(False)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PySide6 Main Window")
        self.resize(1024, 600)
        self.setMinimumSize(640, 360)

        self.interface_dialog = InterfaceSettingDialog(self)

        central_widget = QWidget(self)
        central_layout = QVBoxLayout()
        self.log_text = QTextEdit(self)
        self.log_text.setReadOnly(True)
        self.log_text.setPlaceholderText("Application logs will appear here...")
        central_layout.addWidget(self.log_text)
        central_widget.setLayout(central_layout)
        self.setCentralWidget(central_widget)

        status_bar = QStatusBar(self)
        status_bar.showMessage("Ready")
        self.setStatusBar(status_bar)

        self._install_log_redirect()
        self._create_menu()
        print("Application started.")

    def _install_log_redirect(self):
        self._original_stdout = sys.stdout
        self._original_stderr = sys.stderr

        self.stdout_stream = LogStream(self._original_stdout)
        self.stderr_stream = LogStream(self._original_stderr)
        self.stdout_stream.text_written.connect(self.append_log)
        self.stderr_stream.text_written.connect(self.append_log)

        sys.stdout = self.stdout_stream
        sys.stderr = self.stderr_stream

    def append_log(self, text: str):
        self.log_text.append(text)

    def _create_menu(self):
        menu_bar = self.menuBar()

        file_menu: QMenu = menu_bar.addMenu("File")
        config_menu: QMenu = menu_bar.addMenu("Config")
        help_menu: QMenu = menu_bar.addMenu("Help")

        exit_action = file_menu.addAction("Exit")
        exit_action.triggered.connect(self.close)

        interface_action = config_menu.addAction("Interface Setting")
        interface_action.triggered.connect(self.open_interface_setting)

        about_action = help_menu.addAction("About")
        about_action.triggered.connect(self.show_about)

    def open_interface_setting(self):
        self.interface_dialog.refresh_usb_endpoints()
        self.interface_dialog.exec()
        print("Interface Setting dialog opened.")

    def show_about(self):
        QMessageBox.information(self, "About", f"Current version: {APP_VERSION}")
        print(f"About opened. Version: {APP_VERSION}")

    def closeEvent(self, event):
        sys.stdout = self._original_stdout
        sys.stderr = self._original_stderr
        super().closeEvent(event)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
