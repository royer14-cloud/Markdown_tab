# -*- coding: utf-8 -*-
import os
import re
from PySide2.QtWidgets import QFileDialog
from PySide2.QtCore import QSettings, QStandardPaths


class FileDialog(QFileDialog):
    """
    QFileDialog con:
      - Recordatorio de la última carpeta
      - Tema oscuro/claro
      - Modo abrir o crear archivo nuevo
      - Agregado automático de extensión (según el filtro)
    """

    SETTINGS_GROUP = "PersistentFileDialog"
    SETTINGS_KEY_LAST_PATH = "last_path"
    SETTINGS_ORG = "MiEmpresa"
    SETTINGS_APP = "MiApp"

    def __init__(self, parent=None, title="Seleccionar archivo", initial_dir="",
                 name_filter="All Files (*)", theme="light", save_mode=False):
        super().__init__(parent)

        self.save_mode = save_mode
        self.name_filter = name_filter

        # Configuración base
        self.setOption(QFileDialog.DontUseNativeDialog, True)
        self.setViewMode(QFileDialog.Detail)
        self.setWindowTitle(title)

        # Configurar modo abrir o guardar
        if save_mode:
            self.setAcceptMode(QFileDialog.AcceptSave)
            self.setFileMode(QFileDialog.AnyFile)
        else:
            self.setAcceptMode(QFileDialog.AcceptOpen)
            self.setFileMode(QFileDialog.ExistingFile)

        # Aplicar filtros
        if name_filter:
            self.setNameFilters(name_filter.split(";;"))

        # Restaurar última carpeta o usar inicial
        self._restore_directory(initial_dir)

        # Aplicar tema visual
        self.setStyleSheet(self._style(theme))

    # ---------- Método de clase ----------
    @classmethod
    def get_file(cls, parent=None, title="Seleccionar archivo", initial_dir="",
                 name_filter="All Files (*)", theme="light", save_mode=False):
        """
        Muestra el diálogo y devuelve la ruta seleccionada o None.
        - save_mode=True → permite escribir archivo nuevo (y añade extensión si falta)
        - save_mode=False → abrir archivo existente
        """
        dlg = cls(parent=parent, title=title, initial_dir=initial_dir,
                  name_filter=name_filter, theme=theme, save_mode=save_mode)

        result = dlg.exec_()
        if result == QFileDialog.Accepted:
            selected = dlg.selectedFiles()
            if selected:
                file_path = selected[0]
                folder = os.path.dirname(file_path)

                # Guardar carpeta para próxima vez
                dlg._save_last_directory(folder)

                # Si estamos guardando, permitir archivos nuevos
                if save_mode:
                    # Agregar extensión si no tiene
                    file_path = dlg._ensure_extension(file_path)
                    return file_path
                else:
                    # Solo devolver si el archivo existe
                    if os.path.exists(file_path):
                        return file_path
        return None

    # ---------- Persistencia ----------
    def _restore_directory(self, initial_dir):
        """Determina la carpeta inicial para el diálogo."""
        settings = QSettings(self.SETTINGS_ORG, self.SETTINGS_APP)
        settings.beginGroup(self.SETTINGS_GROUP)

        last_path = settings.value(self.SETTINGS_KEY_LAST_PATH, "")
        chosen = None

        if initial_dir and os.path.exists(initial_dir):
            chosen = initial_dir
        elif last_path and os.path.exists(last_path):
            chosen = last_path
        else:
            chosen = QStandardPaths.writableLocation(QStandardPaths.DesktopLocation)

        if chosen:
            self.setDirectory(chosen)

        settings.endGroup()

    def _save_last_directory(self, folder_path):
        """Guarda la carpeta actual en QSettings."""
        if not folder_path:
            return
        settings = QSettings(self.SETTINGS_ORG, self.SETTINGS_APP)
        settings.beginGroup(self.SETTINGS_GROUP)
        settings.setValue(self.SETTINGS_KEY_LAST_PATH, folder_path)
        settings.endGroup()

    # ---------- Agregar extensión automáticamente ----------
    def _ensure_extension(self, file_path: str) -> str:
        """Si no tiene extensión, agrega la del primer filtro."""
        _, ext = os.path.splitext(file_path)
        if ext:  # ya tiene extensión
            return file_path

        # Buscar la extensión principal del filtro activo (por ejemplo .mdc)
        current_filter = self.selectedNameFilter() or self.name_filter
        match = re.search(r"\*\.(\w+)", current_filter)
        if match:
            extension = match.group(1)
            return f"{file_path}.{extension}"
        return file_path

    # ---------- Estilos ----------
    def _style(self, theme):
        if theme == "dark":
            return """
            QWidget {
                background-color: #1e1e1e;
                color: #dddddd;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                font-size: 10.5pt;
            }
            QPushButton {
                background-color: #0078d7;
                color: white;
                border: none;
                padding: 6px 14px;
                border-radius: 4px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #005a9e;
            }
            QLineEdit, QListView, QTreeView {
                background: #2a2a2a;
                border: 1px solid #444;
                border-radius: 4px;
                padding: 4px;
                color: #eee;
            }
            QHeaderView::section {
                background-color: #2b2b2b;
                border: none;
                padding: 4px;
                font-weight: 600;
                color: #bbb;
            }
            QFileDialog QLabel {
                font-weight: 600;
                color: #ccc;
            }
            """
        else:
            return """
            QWidget {
                background-color: #ffffff;
                color: #333333;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                font-size: 10.5pt;
            }
            QPushButton {
                background-color: #0078d7;
                color: white;
                border: none;
                padding: 6px 14px;
                border-radius: 4px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #005a9e;
            }
            QLineEdit, QListView, QTreeView {
                background: #f9f9f9;
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 4px;
            }
            QHeaderView::section {
                background-color: #f3f3f3;
                border: none;
                padding: 4px;
                font-weight: 600;
                color: #555;
            }
            QFileDialog QLabel {
                font-weight: 600;
                color: #555;
            }
            """
