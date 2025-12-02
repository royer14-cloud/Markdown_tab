import os.path
import shutil

from PySide2.QtWidgets import QWidget, QLabel, QPushButton, QVBoxLayout, QScrollArea
from PySide2.QtGui import QPixmap, QIcon
from PySide2.QtCore import Qt, QSize, Signal

from Dialog import FileDialog
from config.cmessagebox import show_info
from load_dir import abs_path


class ImageViewer(QWidget):
    close_signal = Signal()

    def __init__(self, tempdir=None, pdfname=None, theme="light"):
        super().__init__()
        self.setWindowIcon(QIcon(abs_path("icons", "icon.png")))
        self.setWindowTitle("Preview")
        self.setGeometry(100, 100, 300, 400)
        self.setMinimumSize(300, 400)

        # variable usar
        self.images = []
        self.pdfname = pdfname
        self.tempdir = tempdir
        self.index = 0
        self.scale_factor = 1.0
        self.theme = theme
        self.icons_path = {
            "light": {
                "left": abs_path("icons", "light", "left.png"),
                "right": abs_path("icons", "light", "right.png")
            },
            "dark": {
                "left": abs_path("icons", "dark", "left.png"),
                "right": abs_path("icons", "dark", "right.png")
            }
        }

        temp = os.path.join(self.tempdir, "img")
        for nm in os.listdir(temp):
            rt = os.path.join(temp, nm)
            if os.path.isfile(rt):
                self.images.append(rt)

        # Cargar pixmap original para mantener calidad en escalado
        self.original_pixmap = QPixmap(self.images[self.index])

        # Layout principal
        layout = QVBoxLayout(self)

        self.label = QLabel()
        self.label.setAlignment(Qt.AlignCenter)
        # crear scroll area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidget(self.label)
        self.scroll_area.setWidgetResizable(True)

        layout.addWidget(self.scroll_area, 5)
        self.btnExport = QPushButton("Exportar")
        self.btnExport.setMinimumHeight(20)
        layout.addWidget(self.btnExport, 1)

        # Botones flotantes
        self.prev_btn = QPushButton(self)
        self.prev_btn.setFlat(True)
        self.prev_btn.setIcon(QIcon(abs_path("icons", "light", "left.png")))
        self.prev_btn.setIconSize(QSize(24, 24))
        self.prev_btn.setFixedSize(40, 40)
        self.prev_btn.setStyleSheet("""
            border: none;
        """)

        self.next_btn = QPushButton(self)
        self.next_btn.setFlat(True)
        self.next_btn.setIcon(QIcon(abs_path("icons", "light", "right.png")))
        self.next_btn.setIconSize(QSize(24, 24))
        self.next_btn.setFixedSize(40, 40)
        self.next_btn.setStyleSheet("""
            border: none;
        """)

        # Mostrar imagen inicialmente escalada al ancho de la ventana
        self.base_width = None
        self.update_image()

        self.update_floating_button_position()  # Posición inicial
        self.prev_btn.clicked.connect(self.show_prev)
        self.next_btn.clicked.connect(self.show_next)
        self.btnExport.clicked.connect(self.export)
        self.change_theme(theme)

    def change_theme(self, theme):
        self.theme = theme
        self.prev_btn.setIcon(QIcon(self.icons_path[theme]["left"]))
        self.next_btn.setIcon(QIcon(self.icons_path[theme]["right"]))
        if theme == "light":
            self.btnExport.setStyleSheet('''QPushButton {background-color: #2196F3;color: white;border: none;
            border-radius: 15px;padding: 10px 20px;min-width: 60px; font-size: 12px;font-weight: bold;}
            QPushButton:hover, QPushButton:focus {background-color: #1976D2;}
            QPushButton:pressed {background-color: #1565C0;}''')
        else:
            self.btnExport.setStyleSheet('''QPushButton {background-color: #424242;color: #FFC107;
            border: 2px solid #FFC107; border-radius: 15px;padding: 10px 20px;min-width: 60px;font-size: 12px;
            font-weight: bold;}
            QPushButton:hover {background-color: #616161;border: 2px solid #FFEB3B;}
            QPushButton:pressed {background-color: #212121;border: 2px solid #FFA000;}''')

    def resizeEvent(self, event):
        self.update_image(self.new)
        super().resizeEvent(event)
        self.update_floating_button_position()

    def show_prev(self):
        if self.index > 0:
            self.index -= 1
            self.original_pixmap = QPixmap(self.images[self.index])
            self.update_image(self.new)

    def show_next(self):
        if self.index < len(self.images) - 1:
            self.index += 1
            self.original_pixmap = QPixmap(self.images[self.index])
            self.update_image(self.new)

    def update_image(self, reset_base=False):
        if self.original_pixmap.isNull():
            return
        # limitar ancho a la mitad del procesado
        if reset_base or self.base_width is None:
            self.base_width = self.label.width() / 2

        # establecer ancho definido
        final_width = int(self.base_width * self.scale_factor)
        final_pixmap = self.original_pixmap.scaledToWidth(
            final_width,
            Qt.SmoothTransformation
        )

        self.label.setPixmap(final_pixmap)

    def clean_img(self):
        self.label.setPixmap(None)

    def new_view(self, tempdir, pdfname, theme):
        self.tempdir = tempdir
        temp = os.path.join(self.tempdir, "img")
        self.index = 0
        self.pdfname = pdfname
        self.images = []
        for nm in os.listdir(temp):
            rt = os.path.join(temp, nm)
            if os.path.isfile(rt):
                self.images.append(rt)
        self.original_pixmap = QPixmap(self.images[self.index])
        self.update_image(False)
        self.change_theme(theme)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Minus:
            self.scale_factor /= 1.1  # Reducir tamaño
        elif event.key() == Qt.Key_Plus or event.key() == Qt.Key_Equal:
            self.scale_factor *= 1.1  # Aumentar tamaño

        # Limitar factor para no desaparecer ni agrandar demasiado
        self.scale_factor = max(0.3, min(self.scale_factor, 2.0))
        self.update_image(False)

    def export(self):
        path = FileDialog.get_file(self, "Exportar", "", "PDF Files (*.pdf)", self.theme, True)
        if path:
            pdf = os.path.join(self.tempdir, self.pdfname)
            if os.path.isfile(pdf):
                shutil.copy2(pdf, path)
                show_info(self, "Exportado", f'El documento ha sido exportado con éxito en:<br><a href="file:///{os.path.dirname(path)}">{path}</a>', "info", self.theme)
            else:
                show_info(self, "Error al exportar", "Hubo un problema con la exportación<br>Porfavor no eliminar la carpeta de los temporales en windows", "adv", self.theme)

    def update_floating_button_position(self):
        button_width = self.next_btn.width()
        padding = 10
        y = int(self.height() / 2.5)
        self.next_btn.move(self.width() - button_width - padding, y)
        self.prev_btn.move(padding, y)

    def closeEvent(self, event):
        self.close_signal.emit()
        super().closeEvent(event)
