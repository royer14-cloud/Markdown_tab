import os.path
import subprocess
import sys

from PySide2.QtWidgets import QApplication, QPlainTextEdit, QMainWindow, QShortcut, QAction, QToolBar, \
    QWidget, QSizePolicy, QProgressDialog
from PySide2.QtGui import QColor, QTextCharFormat, QFont, QSyntaxHighlighter, QWheelEvent, QKeySequence, QIcon, QPalette
from PySide2.QtCore import QRegExp, Qt, QSize, Signal, QThread

from View import ImageViewer
from Dialog import FileDialog
from make.export import make_book
from config.CFG import MainPop
from config.cmessagebox import show_info

from load_dir import load_init, abs_path

# congelar ruta
BASE_DIR = ""


class PdfThread(QThread):
    terminado = Signal(object)

    def __init__(self, current_file, tempdir):
        super().__init__()
        self.currentfile = current_file
        self.tmpdir = tempdir
        self._cancel = False

    def cancel(self):
        self._cancel = True

    def run(self):
        try:
            if not self.tmpdir:
                self.tmpdir = make_book(self.currentfile, True)
            else:
                self.tmpdir = make_book(self.currentfile, False, self.tmpdir[1])

            if self._cancel:
                self.terminado.emit(None)
            else:
                self.terminado.emit(self.tmpdir)

        except Exception as e:
            show_info(self, "Error en compilacion", f"Hubo un error al tratar de compilar el proyecto: {e}", "adv")
            # print("Error en make_book ", e)
            self.terminado.emit(None)


class MarkdownHighlighter(QSyntaxHighlighter):
    def __init__(self, document):
        super().__init__(document)
        # definir los patrones una vez
        self.titlePattern = QRegExp(r"^##.*$")
        self.codeblockStartPattern = QRegExp(r"^:::chord")
        self.codeblockEndPattern = QRegExp(r"^:::$")
        self.tabblockStartPattern = QRegExp(r"^```tab\s*$")
        self.tabblockEndPattern = QRegExp(r"^```\s*$")
        self.bisPattern = QRegExp(r"</?bis>")

        # Token de acorde (A-G obligatorio, extensiones comunes, slash opcional)
        token = (
            r"[A-G](?:#|b)?"
            r"(?:maj7|maj9|maj|min|m7|m9|m|dim|aug|sus2|sus4|sus|add\d+|7|6|9)?"
            r"(?:/[A-G](?:#|b)?)?"
        )
        # Línea que solo contiene acordes
        self.chordLinePattern = QRegExp(r"^\s*(?:" + token + r")(?:\s+" + token + r")*\s*$")
        # Para encontrar cada acorde dentro de la línea
        self.chordTokenPattern = QRegExp(token)

        self.apply_theme(theme="light")

    def apply_theme(self, theme="light"):
        if theme == "light":
            self.titleFormat = QTextCharFormat()
            self.titleFormat.setFontWeight(QFont.Bold)
            self.titleFormat.setForeground(QColor("#D45500"))
            self.titleFormat.setBackground(QColor("#FFCCAA"))

            self.chordTokenFormat = QTextCharFormat()
            self.chordTokenFormat.setFontWeight(QFont.Bold)
            self.chordTokenFormat.setForeground(QColor("blue"))

            self.codeFormat = QTextCharFormat()
            self.codeFormat.setBackground(QColor("#f5f5dc"))
            self.codeFormat.setForeground(QColor("darkGreen"))
            self.codeFormat.setFontItalic(True)

            self.tabFormat = QTextCharFormat()
            self.tabFormat.setForeground(QColor("#000000"))
            self.tabFormat.setBackground(QColor("#CCCCCC"))

            self.bisFormat = QTextCharFormat()
            self.bisFormat.setFontWeight(QFont.Bold)
            self.bisFormat.setForeground(QColor("#0277BD"))
            self.bisFormat.setBackground(QColor("#E1F5FE"))

        elif theme == "dark":
            self.titleFormat = QTextCharFormat()
            self.titleFormat.setFontWeight(QFont.Bold)
            self.titleFormat.setForeground(QColor("#FFA726"))
            self.titleFormat.setBackground(QColor("#424242"))

            self.chordTokenFormat = QTextCharFormat()
            self.chordTokenFormat.setFontWeight(QFont.Bold)
            self.chordTokenFormat.setForeground(QColor("#64B5F6"))

            self.codeFormat = QTextCharFormat()
            self.codeFormat.setBackground(QColor("#263238"))
            self.codeFormat.setForeground(QColor("#A5D6A7"))
            self.codeFormat.setFontItalic(True)

            self.tabFormat = QTextCharFormat()
            self.tabFormat.setForeground(QColor("#EEEEEE"))
            self.tabFormat.setBackground(QColor("#616161"))

            self.bisFormat = QTextCharFormat()
            self.bisFormat.setFontWeight(QFont.Bold)
            self.bisFormat.setForeground(QColor("#4FC3F7"))  # celeste claro
            self.bisFormat.setBackground(QColor("#01579B"))  # azul oscuro

        # Forzar repintado
        self.rehighlight()

    def highlightBlock(self, text):
        # Resaltar títulos
        if self.titlePattern.indexIn(text) != -1:
            self.setFormat(0, len(text), self.titleFormat)

        # Detectar línea de acordes
        if hasattr(self, "chordLinePattern") and self.chordLinePattern.exactMatch(text):

            # Negrita + color en cada acorde
            index = self.chordTokenPattern.indexIn(text, 0)
            while index != -1:
                length = len(self.chordTokenPattern.cap(0))
                self.setFormat(index, length, self.chordTokenFormat)
                index = self.chordTokenPattern.indexIn(text, index + length)

        # Multilínea para bloques de código (estado 1)
        if self.previousBlockState() == 1:
            self.setCurrentBlockState(1)
            self.setFormat(0, len(text), self.codeFormat)
            if self.codeblockEndPattern.indexIn(text) != -1:
                self.setCurrentBlockState(0)  # Finaliza bloque
        elif self.codeblockStartPattern.indexIn(text) != -1:
            self.setCurrentBlockState(1)
            self.setFormat(0, len(text), self.codeFormat)
        else:
            if self.currentBlockState() != 2:  # no sobreescribir bloque tab
                self.setCurrentBlockState(0)

        # Multilínea para bloques de tablatura (estado 2)
        if self.previousBlockState() == 2:
            self.setCurrentBlockState(2)
            self.setFormat(0, len(text), self.tabFormat)
            if self.tabblockEndPattern.indexIn(text) != -1:
                self.setCurrentBlockState(0)  # Finaliza bloque
        elif self.tabblockStartPattern.indexIn(text) != -1:
            self.setCurrentBlockState(2)
            self.setFormat(0, len(text), self.tabFormat)
        else:
            if self.currentBlockState() != 1:  # no sobreescribir bloque chord
                self.setCurrentBlockState(0)

        index = self.bisPattern.indexIn(text, 0)
        while index != -1:
            length = len(self.bisPattern.cap(0))
            self.setFormat(index, length, self.bisFormat)
            index = self.bisPattern.indexIn(text, index + length)


class CodeEditor(QPlainTextEdit):
    def __init__(self):
        super().__init__()
        self.highlighter = MarkdownHighlighter(self.document())
        self.zoom_level = 0
        self.wrap_enable = False
        self.update_wrap_mode()
        self.zoom_in_shortcut = QShortcut(QKeySequence("Ctrl++"), self)
        self.zoom_in_shortcut.activated.connect(self.zoom_in)

        self.zoom_out_shortcut = QShortcut(QKeySequence("Ctrl+-"), self)
        self.zoom_out_shortcut.activated.connect(self.zoom_out)
        sample_document(self, True) # Abrir nuevo con tutorial

    def zoom_in(self):
        if self.zoom_level < 10:
            self.zoom_level += 1
            self.zoomIn(1)

    def zoom_out(self):
        if self.zoom_level > -8:
            self.zoom_level -= 1
            self.zoomOut(1)

    def wheelEvent(self, event: QWheelEvent) -> None:
        if event.modifiers() == Qt.ControlModifier:
            if event.angleDelta().y() > 0:
                self.zoom_in()
            else:
                self.zoom_out()
            event.accept()
        else:
            super().wheelEvent(event)

    def update_wrap_mode(self):
        if self.wrap_enable:
            self.setLineWrapMode(QPlainTextEdit.WidgetWidth)
        else:
            self.setLineWrapMode(QPlainTextEdit.NoWrap)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Markdown Tab")
        self.resize(500, 600)
        self.setWindowIcon(QIcon(abs_path("icons", "icon.png")))
        self.theme = "light"
        self.icon_paths = {
            "light": {
                "new": abs_path("icons", "light", "new.png"),
                "import": abs_path("icons", "light", "import.png"),
                "save": abs_path("icons", "light", "save.png"),
                "save1": abs_path("icons", "light", "save1.png"),
                "song": abs_path("icons", "light", "music_note.png"),
                "preview": abs_path("icons", "light", "preview.png"),
                "theme": abs_path("icons", "light", "theme.png"),
                "config": abs_path("icons", "light", "config.png")
            },
            "dark": {
                "new": abs_path("icons", "dark", "new.png"),
                "import": abs_path("icons", "dark", "import.png"),
                "save": abs_path("icons", "dark", "save.png"),
                "save1": abs_path("icons", "dark", "save1.png"),
                "song": abs_path("icons", "dark", "music_note.png"),
                "preview": abs_path("icons", "dark", "preview.png"),
                "theme": abs_path("icons", "dark", "theme.png"),
                "config": abs_path("icons", "dark", "config.png")
            }
        }

        self.SCROLLBAR_QSS = {
            "light": """
                QScrollBar:vertical { background: #f0f0f0; width: 12px; }
                QScrollBar::handle:vertical { background: #888; border-radius: 6px; }
                QScrollBar::handle:vertical:hover { background: #555; }
                QScrollBar:horizontal { background: #f0f0f0; height: 12px; }
                QScrollBar::handle:horizontal { background: #888; border-radius: 6px; }
                QScrollBar::handle:horizontal:hover { background: #555; }
            """,
            "dark": """
                QScrollBar:vertical { background: #1e1e1e; width: 12px; }
                QScrollBar::handle:vertical { background: #555; border-radius: 6px; }
                QScrollBar::handle:vertical:hover { background: #999; }
                QScrollBar:horizontal { background: #1e1e1e; height: 12px; }
                QScrollBar::handle:horizontal { background: #555; border-radius: 6px; }
                QScrollBar::handle:horizontal:hover { background: #999; }
            """
        }

        toolbar = QToolBar("Herramientas", self)
        toolbar.setIconSize(QSize(24, 24))
        self.addToolBar(toolbar)

        # Nuevo
        self.btn_new = QAction(QIcon(self.icon_paths[self.theme]["new"]), "New", self)
        self.btn_new.setShortcut(QKeySequence.New)
        self.btn_new.triggered.connect(self.new_md)
        toolbar.addAction(self.btn_new)

        # Importar
        self.btn_add = QAction(QIcon(self.icon_paths[self.theme]["import"]), "Add", self)
        self.btn_add.triggered.connect(self.import_md)
        toolbar.addAction(self.btn_add)

        # Guardar
        self.btn_save = QAction(QIcon(self.icon_paths[self.theme]["save"]), "Save", self)
        self.btn_save.setShortcut(QKeySequence.Save)
        self.btn_save.triggered.connect(self.save_md)
        toolbar.addAction(self.btn_save)

        # add chords
        self.btn_chords = QAction(QIcon(self.icon_paths[self.theme]["song"]), "Song", self)
        self.btn_chords.triggered.connect(self.add_chords)
        toolbar.addAction(self.btn_chords)

        # agregar separador
        sep_l = QWidget()
        sep_l.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        toolbar.addWidget(sep_l)
        # Botón para la vista previa HTML
        self.floating_btn = QAction(QIcon(self.icon_paths[self.theme]["preview"]), "Show", self)
        self.floating_btn.triggered.connect(self.view_html)
        toolbar.addAction(self.floating_btn)

        # agregar separador
        sep_r = QWidget()
        sep_r.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        toolbar.addWidget(sep_r)

        # crear un boton para cambiar el tema de claro a oscuro
        toolbar.addWidget(QWidget())
        self.id_icons = False
        self.theme_btn = QAction(QIcon(self.icon_paths[self.theme]["theme"]), "Theme", self)
        self.theme_btn.triggered.connect(self.theme_change)
        toolbar.addAction(self.theme_btn)

        # boton configuracion
        self.config_btn = QAction(QIcon(self.icon_paths[self.theme]["config"]), "Configuracion", self)
        self.config_btn.triggered.connect(self.on_config)
        toolbar.addAction(self.config_btn)

        self.editor = CodeEditor()
        self.editor.setFont(QFont("Consolas", 12))
        self.setCentralWidget(self.editor)

        self.editor.textChanged.connect(self.on_editor_changed)

        self.txt_editor_update = False
        self.current_file = None
        self.tempdir = None
        self.viewPDF = None
        self.progreso = None
        self.thread_pdf = None

    def on_editor_changed(self):
        if self.editor.toPlainText().strip():  # verificar si no esta vacio
            if not self.txt_editor_update:
                self.txt_editor_update = True
                # cambiar icono de guardar
                self.btn_save.setIcon(QIcon(self.icon_paths[self.theme]["save1"]))

    def view_html(self):
        if self.txt_editor_update:
            if self.editor.toPlainText().strip():
                if not self.save_md():
                    return

        if self.thread_pdf and self.thread_pdf.isRuning():
            show_info(self, "Procesando", "La visualización aun esta procesandose", "info", self.theme)
            return

        if not self.current_file:
            if not self.save_md():
                return

        # crear status
        self.progreso = QProgressDialog("Generando vista ..", "Cancelar", 0, 0, self)
        self.progreso.setWindowTitle("Procesando")
        self.progreso.setWindowModality(Qt.WindowModal)
        self.progreso.setCancelButtonText("Cancelar")
        self.progreso.canceled.connect(self.cancel_build)
        self.progreso.show()

        self.thread_pdf = PdfThread(self.current_file, self.tempdir)
        self.thread_pdf.terminado.connect(self.on_pdf_end)
        self.thread_pdf.start()

    def on_pdf_end(self, result):
        if self.progreso:
            self.progreso.close()
            self.progreso = None

        if not result:
            show_info(self, "Aviso", f"no es posible generar visualizador porque:\n{result}", "adv", self.theme)
            return
        self.tempdir = result

        if not self.viewPDF:
            self.viewPDF = ImageViewer(self.tempdir[1], self.tempdir[0], self.theme)
        else:  # corregir
            self.viewPDF.clean_img()
            self.viewPDF.new_view(self.tempdir[1], self.tempdir[0], self.theme)

        save_folder(self.tempdir[1])
        self.viewPDF.show()
        self.viewPDF.raise_()
        self.viewPDF.activateWindow()
        self.viewPDF.setFocus()
        self.viewPDF.close_signal.connect(self.close_viewpdf)
        self.thread_pdf = None

    def cancel_build(self):
        if self.thread_pdf:
            try:
                self.thread_pdf.cancel()
            except Exception as e:
                show_info(self, "Error", f"Error al compilar la visualizacion en:\n{e}", "error", self.theme)
                # print("Error cancel build: ", e)

        if self.progreso:
            self.progreso.close()
            self.progreso = None

    def close_viewpdf(self):
        self.viewPDF = None

    def on_config(self):
        config_pop = MainPop(self.theme)
        config_pop.exec_()

    def new_md(self):
        self.current_file = None
        self.tempdir = None
        sample_document(self.editor, False)

    def import_md(self):
        path = FileDialog.get_file(self, "Importar cancion", "", "MarkdownG Files (*.mdg)", self.theme)
        # path, _ = QFileDialog.getOpenFileName(self, "Importar cancion", "", "SongChord Files (*.mdc);;All Files (*)")
        if path:
            with open(path, "r", encoding="utf-8") as f:
                text = f.read()
            self.editor.setPlainText(text)
            self.current_file = path
            self.tempdir = None

    def save_md(self):
        if self.editor.toPlainText().strip():  # Verificar si hay contenido
            if self.current_file is None:  # verificar si es nuevo archivo
                path = FileDialog.get_file(self, "Guardar", "", "MarkdownG Files (*.mdg)", self.theme, True)
                if path:
                    self.current_file = path
                else:
                    return False
            content = self.editor.toPlainText()
            with open(self.current_file, "w", encoding="utf-8") as f:
                f.write(content)
            self.txt_editor_update = False
            self.btn_save.setIcon(QIcon(self.icon_paths[self.theme]["save"]))
        else:
            show_info(self, "No guardado", "El documento esta vacio", "adv", self.theme)
            return False
        return True

    def add_chords(self):
        show_info(self, "Acordes", "Proximamente estará disponible\n ésta característica", "info", self.theme)

    def theme_change(self):
        self.id_icons = not self.id_icons
        # aqui va toda lógica del cambio de tema
        if self.id_icons:  # modo oscuro
            app.setPalette(get_dark_palette())
            self.editor.highlighter.apply_theme("dark")
            self.theme = "dark"
        else:
            app.setPalette(get_light_palette())
            self.editor.highlighter.apply_theme("light")
            self.theme = "light"

        # cambiar de tema botonos
        self.btn_new.setIcon(QIcon(self.icon_paths[self.theme]["new"]))
        self.btn_add.setIcon(QIcon(self.icon_paths[self.theme]["import"]))
        if self.txt_editor_update:
            self.btn_save.setIcon(QIcon(self.icon_paths[self.theme]["save1"]))
        else:
            self.btn_save.setIcon(QIcon(self.icon_paths[self.theme]["save"]))
        self.btn_chords.setIcon(QIcon(self.icon_paths[self.theme]["song"]))
        self.floating_btn.setIcon(QIcon(self.icon_paths[self.theme]["preview"]))
        self.theme_btn.setIcon(QIcon(self.icon_paths[self.theme]["theme"]))
        self.config_btn.setIcon(QIcon(self.icon_paths[self.theme]["config"]))

        # cambiar estylos boton exportar
        if self.viewPDF:
            self.viewPDF.change_theme(self.theme)

        # cambiar los scrollbars del editor
        self.editor.setStyleSheet(self.SCROLLBAR_QSS[self.theme])

    @staticmethod
    def get_light_palette():
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor("#ffffff"))
        palette.setColor(QPalette.WindowText, Qt.black)
        palette.setColor(QPalette.Base, QColor("#fdf6e3"))  # fondo editor
        palette.setColor(QPalette.Text, Qt.black)
        palette.setColor(QPalette.Button, QColor("#e6e6e6"))
        palette.setColor(QPalette.ButtonText, Qt.black)

        # # Selección y cursor visibles
        # palette.setColor(QPalette.Highlight, QColor("#3399ff"))  # azul claro
        # palette.setColor(QPalette.HighlightedText, Qt.white)  # texto blanco seleccionado
        return palette

    @staticmethod
    def get_dark_palette():
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor("#121212"))
        palette.setColor(QPalette.WindowText, Qt.white)
        palette.setColor(QPalette.Base, QColor("#1e1e1e"))  # fondo editor
        palette.setColor(QPalette.Text, Qt.white)
        palette.setColor(QPalette.Button, QColor("#333333"))
        palette.setColor(QPalette.ButtonText, Qt.white)
        return palette

    def closeEvent(self, event):
        if self.editor.toPlainText().strip():
            if self.txt_editor_update and self.current_file:
                self.save_md()
        if self.viewPDF:  # es la 2da ventana
            self.viewPDF.close()

        # eliminar temporales
        if self.current_file:
            startinfo = subprocess.STARTUPINFO()
            startinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startinfo.wShowWindow = subprocess.SW_HIDE
            ruta = abs_path("make", "tutorial", "remove.exe")
            try:
                subprocess.Popen([ruta], startupinfo=startinfo, creationflags=subprocess.CREATE_NO_WINDOW)
            except Exception as e:
                show_info(self, "Error", f"Ha ocurrido un error al eliminar los temporales:\n{e}", "adv", self.theme)
        super().closeEvent(event)
        QApplication.quit()



def get_light_palette():
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor("#ffffff"))
    palette.setColor(QPalette.WindowText, Qt.black)
    palette.setColor(QPalette.Base, QColor("#fdf6e3"))  # fondo editor
    palette.setColor(QPalette.Text, Qt.black)
    palette.setColor(QPalette.Button, QColor("#e6e6e6"))
    palette.setColor(QPalette.ButtonText, Qt.black)
    return palette


def get_dark_palette():
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor("#121212"))
    palette.setColor(QPalette.WindowText, Qt.white)
    palette.setColor(QPalette.Base, QColor("#1e1e1e"))  # fondo editor
    palette.setColor(QPalette.Text, Qt.white)
    palette.setColor(QPalette.Button, QColor("#333333"))
    palette.setColor(QPalette.ButtonText, Qt.white)
    return palette


def save_folder(path):
    ruta = abs_path("make", "tutorial", "path.lib")
    with open(ruta, "a", encoding="utf-8") as file:
        file.write("\n"+path)


def sample_document(self, tutorial=False):
    if tutorial:
        ruta = abs_path("make", "tutorial", "example.mdg")
        if os.path.exists(ruta):
            with open(ruta, "r", encoding="utf-8") as file:
                text = file.read()
            self.setPlainText(text)
        return None
    else:
        ruta = abs_path("make", "tutorial", "new.mdg")
        if os.path.exists(ruta):
            with open(ruta, "r", encoding="utf-8") as file:
                text = file.read()
            self.setPlainText(text)
        return None


if __name__ == "__main__":
    load_init()  # cargar directorio
    app = QApplication(sys.argv)
    app.setPalette(get_light_palette())
    ventana = MainWindow()
    # argumento al abrir con un archivo
    if len(sys.argv) > 1:
        ventana.current_file = os.path.abspath(sys.argv[1])
        with open(ventana.current_file, "r", encoding="utf-8") as f:
            ventana.editor.setPlainText(f.read())
    ventana.show()
    sys.exit(app.exec_())
