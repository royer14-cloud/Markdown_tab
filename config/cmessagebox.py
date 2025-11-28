from PySide2.QtCore import Qt
from PySide2.QtWidgets import QMessageBox


def show_info(self, title, text, tipo="info", theme="light"):
    box = QMessageBox(self)
    box.setWindowTitle(title)
    box.setTextFormat(Qt.RichText)
    box.setTextInteractionFlags(Qt.TextBrowserInteraction)
    box.setText(text)
    abrir = None
    if tipo == "info":
        box.setIcon(QMessageBox.Information)
    elif tipo == "adv":
        box.setIcon(QMessageBox.Warning)
    elif tipo == "error":
        box.setIcon(QMessageBox.Critical)
    elif tipo == "preg":
        box.setIcon(QMessageBox.Question)

    if theme == "light":
        box.setStyleSheet("""
            QMessageBox {
                background-color: white;
                color: black;
            }
            QPushButton {
                background-color: #e6e6e6;
                color: black;
            }
        """)
    else:
        box.setStyleSheet("""
            QMessageBox {
                background-color: #121212;
                color: white;
            }
            QPushButton {
                background-color: #333333;
                color: white;
            }
        """)
    box.exec_()
