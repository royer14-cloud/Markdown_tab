# -*- coding: utf-8 -*-
import configparser
import os
from PySide2.QtCore import Qt, QSize
from PySide2.QtGui import QIcon
from PySide2.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QComboBox, QDoubleSpinBox, QSpinBox,
    QSlider, QSpacerItem, QSizePolicy, QTabWidget, QWidget,
    QDialogButtonBox, QGroupBox, QPushButton, QButtonGroup
)


class MainPop(QDialog):
    def __init__(self, tema="light"):
        super().__init__()
        self.setWindowTitle("Configuracion")
        self.resize(369, 387)
        self.setWindowIcon(QIcon("icons/dark/config.png"))
        self.theme = tema

        self.cfg_file = "config/config.cfg"
        self.config = configparser.ConfigParser()

        main_layout = QVBoxLayout(self)

        # --- Tabs ---
        self.tabWidget = QTabWidget()
        main_layout.addWidget(self.tabWidget)

        # ================= TAB 1 =================
        tab1 = QWidget()
        vbox1 = QVBoxLayout(tab1)
        inner_vbox = QVBoxLayout()

        # Label Tipo
        lbl_tipo = QLabel("Tipo", alignment=Qt.AlignCenter)
        inner_vbox.addWidget(lbl_tipo)

        # ComboBox tipo
        self.comboBox = QComboBox()
        self.comboBox.addItems(["None", "a3", "a4", "a5", "letter", "legal"])
        inner_vbox.addWidget(self.comboBox)

        # SpinBox Width / Height
        hbox = QHBoxLayout()
        self.doubleSpinBox = QDoubleSpinBox(maximum=1240.0, value=125.8)
        self.doubleSpinBox_2 = QDoubleSpinBox(maximum=1280.0, value=250.0)
        hbox.addWidget(self.doubleSpinBox)
        hbox.addWidget(self.doubleSpinBox_2)
        inner_vbox.addLayout(hbox)

        # Two columns or One column
        groupbox = QGroupBox()
        buton1 = QPushButton()
        buton1.setIcon(QIcon(f"icons/{self.theme}/oneP.png"))
        buton1.setIconSize(QSize(72, 72))
        buton1.setCheckable(True)
        buton1.setFlat(True)
        buton2 = QPushButton()
        buton2.setIcon(QIcon(f"icons/{self.theme}/twoP.png"))
        buton2.setIconSize(QSize(72, 72))
        buton2.setFlat(True)
        buton2.setCheckable(True)

        self.buton_grup = QButtonGroup()
        self.buton_grup.addButton(buton1, 0)
        self.buton_grup.addButton(buton2, 1)
        self.buton_grup.setExclusive(True)

        lybtn = QHBoxLayout()
        lybtn.addWidget(buton1)
        lybtn.addWidget(buton2)
        groupbox.setLayout(lybtn)

        inner_vbox.addWidget(groupbox, 2, Qt.AlignCenter)

        lbl_x = QLabel("Posicion x", alignment=Qt.AlignCenter)
        inner_vbox.addWidget(lbl_x)

        self.spinBox_3 = QSpinBox()
        inner_vbox.addWidget(self.spinBox_3)

        # Spacer
        inner_vbox.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # Stretch factors
        inner_vbox.setStretch(0, 1)
        inner_vbox.setStretch(1, 1)
        inner_vbox.setStretch(2, 1)
        inner_vbox.setStretch(3, 2)
        inner_vbox.setStretch(4, 1)
        inner_vbox.setStretch(5, 2)
        inner_vbox.setStretch(6, 3)

        vbox1.addLayout(inner_vbox)
        self.tabWidget.addTab(tab1, "Formato")

        # ================= TAB 2 =================
        tab2 = QWidget()
        vbox2 = QVBoxLayout(tab2)

        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        form.setFormAlignment(Qt.AlignHCenter | Qt.AlignTop)
        form.setVerticalSpacing(12)

        def add_combo(label_text):
            lbl = QLabel(label_text)
            combo = QComboBox()
            combo.addItems([str(i) for i in range(6, 23)])
            form.addRow(lbl, combo)
            return combo

        self.cmb_chn = add_combo("Chord number")
        self.cmb_chs = add_combo("Chord Symbol")
        self.cmb_tab = add_combo("Tablature")
        self.cmb_verse = add_combo("Versos")
        self.cmb_body = add_combo("Cuerpo")

        vbox2.addLayout(form)
        self.tabWidget.addTab(tab2, "Fuente")

        # ================= TAB 3 =================
        tab3 = QWidget()
        vbox3 = QVBoxLayout(tab3)

        inner_vbox3 = QVBoxLayout()
        inner_vbox3.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

        lbl_acorde = QLabel("Acorde escala", alignment=Qt.AlignCenter)
        lbl_acorde.setFixedHeight(24)
        inner_vbox3.addWidget(lbl_acorde)

        hbox_slider = QHBoxLayout()
        hbox_slider.addItem(QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))

        self.horizontalSlider = QSlider(Qt.Horizontal)
        self.horizontalSlider.setMaximum(30)
        self.horizontalSlider.setFixedHeight(20)
        self.horizontalSlider.valueChanged.connect(self.change_slider)
        hbox_slider.addWidget(self.horizontalSlider)

        hbox_slider.addItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        hbox_slider.setStretch(1, 2)

        inner_vbox3.addLayout(hbox_slider)

        self.lbl_test = QLabel("Testear", alignment=Qt.AlignCenter)
        inner_vbox3.addWidget(self.lbl_test)

        # Stretch factors
        inner_vbox3.setStretch(0, 1)
        inner_vbox3.setStretch(1, 2)
        inner_vbox3.setStretch(2, 2)
        inner_vbox3.setStretch(3, 10)

        vbox3.addLayout(inner_vbox3)
        self.tabWidget.addTab(tab3, "Grafico")

        # ================= BUTTON BOX =================
        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        main_layout.addWidget(self.buttonBox)

        # Temas
        self.change_theme()

        # Conexiones
        self.load_config()
        self.comboBox.currentIndexChanged.connect(self.update_spin_boxes)
        self.update_spin_boxes()

        # guardar config
        self.buttonBox.accepted.connect(self.save_config)

    def select_page(self, id_btn):
        buton = self.buton_grup.button(id_btn)
        if buton:
            buton.setChecked(True)

    def change_slider(self):
        self.lbl_test.setText(str(self.horizontalSlider.value() / 10))

    def load_config(self):
        if not os.path.exists(self.cfg_file):
            print("Archivo config.cfg no encontrado, usando valores por defecto")
            return

        self.config.read(self.cfg_file)

        # === PAGE ===
        # self.checkBox.setChecked(self.config.getboolean("PAGE", "twocolumn", fallback=False))
        self.select_page(self.config.getboolean("PAGE", "twocolumn", fallback=False))
        self.spinBox_3.setValue(self.config.getint("PAGE", "xpos", fallback=4))
        self.comboBox.setCurrentText(self.config.get("PAGE", "format", fallback="None"))
        self.doubleSpinBox.setValue(self.config.getfloat("PAGE", "width", fallback=125.8))
        self.doubleSpinBox_2.setValue(self.config.getfloat("PAGE", "height", fallback=250))

        # === FONTSIZE ===
        self.cmb_chn.setCurrentText(self.config.get("FONTSIZE", "chordnumber", fallback="16"))
        self.cmb_chs.setCurrentText(self.config.get("FONTSIZE", "chordsymbol", fallback="11"))
        self.cmb_tab.setCurrentText(self.config.get("FONTSIZE", "tab", fallback="11"))
        self.cmb_verse.setCurrentText(self.config.get("FONTSIZE", "verse", fallback="12"))
        self.cmb_body.setCurrentText(self.config.get("FONTSIZE", "body", fallback="11"))

        # === CHORD ===
        self.horizontalSlider.setValue(int(float(self.config.get("CHORD", "scale", fallback="0.6")) * 10))

    def save_config(self):
        if not self.config.has_section("PAGE"):
            self.config.add_section("PAGE")
        if not self.config.has_section("FONTSIZE"):
            self.config.add_section("FONTSIZE")
        if not self.config.has_section("CHORD"):
            self.config.add_section("CHORD")

        # === PAGE ===
        self.config.set("PAGE", "twocolumn", str(self.buton_grup.checkedId()))
        self.config.set("PAGE", "xpos", str(self.spinBox_3.value()))
        self.config.set("PAGE", "format", self.comboBox.currentText())
        self.config.set("PAGE", "width", str(self.doubleSpinBox.value()))
        self.config.set("PAGE", "height", str(self.doubleSpinBox_2.value()))

        # === FONTSIZE ===
        self.config.set("FONTSIZE", "chordnumber", self.cmb_chn.currentText())
        self.config.set("FONTSIZE", "chordsymbol", self.cmb_chs.currentText())
        self.config.set("FONTSIZE", "tab", self.cmb_tab.currentText())
        self.config.set("FONTSIZE", "verse", self.cmb_verse.currentText())
        self.config.set("FONTSIZE", "body", self.cmb_body.currentText())

        # === CHORD ===
        self.config.set("CHORD", "scale", str(self.horizontalSlider.value() / 10))

        with open(self.cfg_file, "w") as configfile:
            self.config.write(configfile)

        print("Archivo config.cfg actualizado")

    def update_spin_boxes(self):
        enabled = (self.comboBox.currentText() == "None")
        self.doubleSpinBox.setEnabled(enabled)
        self.doubleSpinBox_2.setEnabled(enabled)

    def change_theme(self):
        try:
            path = f"config/{self.theme}.css"
            with open(path, "r") as file:
                self.setStyleSheet(file.read())
        except FileNotFoundError:
            print(f"El archivo {self.theme}.css no existe en config")
