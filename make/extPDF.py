import re
import os
from fpdf import FPDF
from fpdf.enums import XPos, YPos
from datetime import datetime
import json


class SongbookPDF(FPDF):
    def __init__(self, twocolumn=False, x_pos=0, page_format=(125.8, 247.5), size_verse=12, size_body=11, size_code=11,
                 scale=0.6, **kwargs):
        super().__init__(format=page_format, **kwargs)

        # parametros general de formato
        self.is_twocolumm = twocolumn
        self.x_pos = x_pos  # margen extra (offset en x)
        self.x_lpos = x_pos # posicion x para <bis>
        self.page_format = page_format
        self.size_tverse = size_verse
        self.size_tbody = size_body
        self.size_text_code = size_code

        # interno
        self.column = 0  # 0 izquierda, 1 derecha
        self.col_width = self.epw / 2  # ancho de columna (se recalcula si cambias márgenes)
        self.columns_active = False
        self.y_start = None  # Y superior del marco de columnas actual
        self.y_col = [0.0, 0.0]  # Y alcanzada por cada columna
        self.scale = scale  # tamaño de los acordes
        self.no_free = []  # espacios Y ocupados por el bloque tab

        # fuentes
        self.add_font("Osans", "", fname="make/fonts/OpenSans_Condensed-Bold.ttf")
        self.add_font("Consolas", "", fname="make/fonts/Inconsolata.ttf")
        self.add_font("Consolas", "B", fname="make/fonts/Inconsolata-ExtraBold.ttf")
        self.add_font("Fira", "B", fname="make/fonts/FiraCode-Bold.ttf")
        self.add_font("Fira", "", fname="make/fonts/FiraCode-Regular.ttf")

    # ---------- helpers de columnas ----------
    def current_col_x(self):
        return self.l_margin + (self.col_width * self.column)

    def begin_columns(self):
        """Activar modo columnas anclado a la Y actual."""
        if not self.columns_active:
            # por si cambiaste márgenes en runtime:
            self.col_width = self.epw / 2
            self.y_start = self.get_y()
            self.y_col = [self.y_start, self.y_start]
            self.column = 0
            self.columns_active = True
            self.set_xy(self.current_col_x(), self.y_start)

    def end_columns(self):
        """Cerrar columnas y llevar el cursor a la Y mayor alcanzada."""
        if self.columns_active:
            y = max(self.y_col)
            self.columns_active = False
            self.column = 0
            self.set_xy(self.l_margin, y)

    def switch_column(self):
        """Cambiar entre izquierda/derecha o saltar a nueva página."""
        if not self.columns_active:
            return
        if self.column == 0:
            self.column = 1
            self.set_xy(self.l_margin + self.col_width, self.y_start)
        else:
            # nueva página, reiniciar marco de columnas bajo el header
            self.newpage()

    def newpage(self):
        self.add_page()
        self.y_start = self.get_y()
        self.y_col = [self.y_start, self.y_start]
        self.column = 0
        self.set_xy(self.current_col_x(), self.y_start)

    def check_space(self, h=6):
        """Si no cabe 'h', cambiar de columna / página."""
        if self.columns_active and (self.get_y() + h > self.page_break_trigger):
            self.switch_column()

    def write_col(self, text, h, font=None):
        """multi_cell dentro de la columna, restaurando X y actualizando Y de la columna."""
        if font:
            fam, style, size = font
            self.set_font(fam, style, size)

        if self.is_twocolumm:
            x = self.current_col_x() + self.x_pos
            self.x_lpos = x
            y_test = self.get_y()
            for (y_start, y_end) in self.no_free:
                if y_start - 5.0 <= y_test <= y_end + 5.0:
                    self.set_y(y_end + 3.0)
                    break

            self.set_xy(x, self.get_y())
            self.multi_cell(self.col_width, h, text, wrapmode="CHAR")
            # multi_cell deja X en margen izquierdo → restauramos
            self.y_col[self.column] = self.get_y()
            self.set_x(x)
        else:
            # self.set_xy(x, self.get_y())
            self.set_x(self.x_pos)
            self.multi_cell(self.epw, h, text, wrapmode="CHAR")
            # self.set_x(x)

    def col_lf(self, h):
        """Salto vertical dentro de la columna sin romper X."""
        self.set_y(self.get_y() + h)
        self.y_col[self.column] = self.get_y()
        self.set_x(self.current_col_x())

    # ---------- resto de tu flujo ----------
    def footer(self):
        pass
        # self.set_y(-15)
        # self.set_font("Helvetica", 'I', 8)
        # self.cell(0, 10, f"Página {self.page_no()}",
        #           new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")

    def add_song(self, meta, body):
        # Agregando metadatos al pdf
        self.set_title(meta.get("title", " "))
        self.set_author(meta.get("autor", " "))
        self.set_creator("Markdown Tab")
        self.set_subject("Puedes descargar el software en: https://github.com/royer14-cloud/Markdown_tab")
        self.set_creation_date(datetime.now())

        # Título/autor a ancho completo
        self.set_font("Fira", 'B', 16)
        x = self.w-13
        bpm = meta.get("BPM", "  ")
        self.rect(x-1, 1, self.get_string_width(bpm)+2, 9)
        self.text(x, 8, bpm)
        self.cell(0, 4, meta.get("title", "Sin título"),
                  new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
        self.set_font("Helvetica", 'I', 12)
        self.cell(0, 8, f"{meta.get('autor', 'Desconocido')}",
                  new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
        self.ln(3)
        # Contenido
        self.parse_body(body)
        # Por si el archivo termina con columnas abiertas
        self.end_columns()

    def parse_body(self, body_text):
        lines = body_text.strip().splitlines()
        i = 0
        bis_active = False
        while i < len(lines):
            line = lines[i]

            # -- linea con  <bis> </bis>
            start_bis = "<bis>" in line
            end_bis = "</bis>" in line
            if start_bis:
                bis_active = True
                line = line.replace("<bis>", "")
            if end_bis:
                line = line.replace("</bis>", "")

            # --- Bloque ::chord (ancho completo) ---
            if line.startswith(":::chord"):
                # asegurarnos de no pisar columnas abiertas
                self.end_columns()

                # detectar nota raiz
                m = re.match(r":::chord\{(\d+)\}", line)
                rootnote = int(m.group(1)) if m else None

                chord_block = []
                i += 1
                while i < len(lines) and not lines[i].startswith(":::"):
                    chord_block.append(lines[i])
                    i += 1
                self.add_chords(" ".join(chord_block), rootnote)
                i += 1
                continue

            # --- Bloque ```tab (ancho completo) ---
            if line.startswith("```tab"):
                tab_block = []
                i += 1
                while i < len(lines) and not lines[i].startswith("```"):
                    tab_block.append(lines[i])
                    i += 1
                self.add_tab(tab_block)

                i += 1
                continue

            # nueva hoja
            if line.startswith("/newpage"):
                self.newpage()
                i += 1
                continue

            # --- Verso (## ...) → activar columnas ---
            if line.startswith("##"):
                if self.is_twocolumm:
                    self.begin_columns()
                    self.check_space(6)
                section_title = line.strip("# ").strip()
                self.set_text_color("#b30000")
                self.write_col(section_title, 3, font=("Osans", "", self.size_tverse))
                self.set_text_color("#000000")
                if self.is_twocolumm:
                    self.col_lf(2)
                else:
                    self.ln(2)
                i += 1
                continue

            # --- Línea con acordes incrustados (en columnas) ---
            if line.strip():
                if self.is_twocolumm:
                    self.begin_columns()
                    self.check_space(6)
                # construimos líneas acorde/letra con tu método de espacios
                acorde_regex = r"^([A-G](?:[#b])?(?:m|maj|min|dim|aug|sus[24]|add\d+|maj7|7)? \s*)+$"
                if re.match(acorde_regex, line.strip(), re.VERBOSE):
                    self.set_font("Fira", "B", self.size_tbody)
                else:
                    self.set_font("Fira", "", self.size_tbody)
                y_in_b = self.get_y()
                self.write_col(line, 4)
                y_end_b = self.get_y()

                # imprimir linea bis
                if bis_active:
                    self.set_line_width(1.2)
                    self.set_draw_color(255, 0, 0)
                    self.line(x1=self.x_lpos - 1, y1=y_in_b, x2=self.x_lpos - 1, y2=y_end_b)
                # cerrar si el tag </bis>
                if end_bis:
                    bis_active = False

                i += 1
                continue

            # --- Línea en blanco ---
            if self.is_twocolumm:
                if self.columns_active:
                    self.col_lf(4)
                else:
                    self.ln(3)
            else:
                self.ln(2)
            i += 1

    # --- Ancho completo para chord/tab (usando escala) ---
    def add_chords(self, chord_block, rootnote=None):
        cantidad, lista = self.parse_chords(chord_block)
        x_start = self.get_x() + 5
        y_start = self.get_y()

        # parámetros base (valores originales) y se escalan por self.scale
        base_max_per_row = 5
        base_spacing_x = 30  # separación horizontal base entre cajas
        base_spacing_y = 40  # separación vertical base entre filas
        base_margin_extra = 10  # pequeño offset extra entre cajas

        spacing_x = base_spacing_x * self.scale
        spacing_y = base_spacing_y * self.scale
        max_per_row = base_max_per_row

        # tamaño de la caja base escalada (box_w, box_h se usan también en draw_chord_box)
        # draw_chord_box usará self.scale internamente, pero necesitamos el box_h para calcular salto vertical
        base_box_h = 30
        box_h = base_box_h * self.scale

        for idx, (root, pos) in enumerate(lista, 1):
            col = (idx - 1) % max_per_row
            row = (idx - 1) // max_per_row
            x = x_start + col * (spacing_x + base_margin_extra * self.scale)
            y = y_start + row * spacing_y
            self.draw_chord_box(x, y, root, pos, idx, rootnote)

        # calcular altura ocupada y mover cursor hacia abajo preservando columnas
        rows = (len(lista) + max_per_row - 1) // max_per_row
        if rows > 0:
            total_h = (rows - 1) * spacing_y + box_h
        else:
            total_h = box_h

        # dejamos un pequeño padding
        pad = 4 * self.scale
        new_y = y_start + total_h + pad
        self.set_y(new_y)
        # actualizar estado de la columna actual
        if self.columns_active:
            self.y_col[self.column] = self.get_y()
        else:
            # si no hay columnas, dejamos una separación vertical normal
            self.ln(pad)

    # --- Dibuja una caja de acorde con escala aplicada ---
    def draw_chord_box(self, x, y, chord_name, pos, idx, rootnote):
        """
        Dibuja una caja de acorde en (x,y) escalada por self.scale.
        Toma las definiciones desde ./chords/{nota}.json y multiplica
        todas las coordenadas / tamaños por self.scale.
        """
        s = self.scale

        # base sizes (valores originales)
        base_box_w = 30
        base_box_h = 30

        box_w = base_box_w * s
        box_h = base_box_h * s

        # espacio entre cuerdas y trastes (calculado desde box dims)
        string_spacing = box_w / 5.0  # 6 cuerdas -> 5 espacios
        fret_spacing = box_h / 3.0  # 3 trastes -> 3 divisiones

        # --- Dibujar 6 cuerdas (verticales) ---
        self.set_line_width(max(0.01, 0.4 * s))
        self.set_draw_color("#323232")
        for i in range(6):
            x_pos = x + i * string_spacing
            self.line(x_pos, y, x_pos, y + box_h)

        # --- Dibujar trastes (horizontales) ---
        for j in range(4):  # 3 espacios → 4 líneas (incluye nut)
            y_pos = y + j * fret_spacing
            self.line(x, y_pos, x + box_w, y_pos)

        # --- Nombre del acorde (centrado arriba) ---
        # escalamos tamaño de fuente del nombre
        font_name_size = max(6, 14 * s)
        self.set_font("Osans", "", font_name_size)

        # pintar nota raiz
        if rootnote == idx:
            self.set_text_color("#d60d0d")
        else:
            self.set_text_color("#000000")
        self.set_xy(x, y - (6 * s))
        # cell acepta float width/height; centramos en la caja
        self.cell(box_w, 4 * s, chord_name, align="C")

        # --- Posicion del acorde (leer JSON y escalar cada shape) ---
        num_x = x + string_spacing  # referencia para algunos textos

        note = chord_name[0].upper()
        directory = os.path.join("make/chords", f"{note}.json")
        if not os.path.exists(directory):
            # si no existe archivo, no dibuja shapes pero sigue devolviendo
            # opcional: dibujar una X o algo para indicar falta
            # print(f"No hay archivo para acorde {note}")
            return

        with open(directory, "r", encoding="utf-8") as f:
            chord_raw = json.load(f)

        # buscar por nombre exacto (Am) o por root si está estructurado distinto
        entry = chord_raw.get(chord_name) or chord_raw.get(note)
        if not entry or pos not in entry:
            # print(f"No hay definicion para {chord_name} pos {pos}")
            return

        shapes = entry[pos]

        # Dibujar cada elemento escalando coordenadas y tamaños
        self.set_line_width(max(0.01, 0.2 * s))
        self.set_draw_color("#000000")
        for shape in shapes:
            t = shape.get("type")
            # extraer coords (soporta 'y' o 'cy')
            sx = shape.get("x", 0) or 0
            sy = shape.get("y", shape.get("cy", 0)) or 0

            # convertir/escala seguro
            try:
                sx = float(sx) * s
            except Exception:
                sx = 0.0
            try:
                sy = float(sy) * s
            except Exception:
                sy = 0.0

            if t == "circle":
                # radius puede venir como "radius" o "r"
                r = shape.get("radius", shape.get("r", 3))
                try:
                    r = float(r) * s
                except Exception:
                    r = 1.0 * s
                self.set_fill_color("#424649")
                # x + sx, y + sy => coordenadas relativas escaladas
                self.circle(x + sx, y + sy, radius=r, style="FD")

            elif t == "ellipse":
                w = shape.get("w", 0)
                h = shape.get("h", 0)
                try:
                    w = float(w) * s
                    h = float(h) * s
                except Exception:
                    w = 0.0
                    h = 0.0
                self.set_fill_color("#4c4c4c")
                self.set_line_width(max(0.01, 1.0 * s))
                self.set_draw_color("#666666")
                self.ellipse(x + sx, y + sy, w=w, h=h, style="FD")
                self.set_line_width(max(0.01, 0.2 * s))
                self.set_draw_color("#000000")

            elif t == "rect":
                w = shape.get("w", 0);
                h = shape.get("h", 0)
                try:
                    w = float(w) * s;
                    h = float(h) * s
                except Exception:
                    w = 0.0;
                    h = 0.0
                self.set_fill_color("#424649")
                self.set_line_width(max(0.01, 1.0 * s))
                self.set_draw_color("#666666")
                self.rect(x + sx, y + sy, w=w, h=h, round_corners=True, style="FD")
                self.set_line_width(max(0.01, 0.2 * s))
                self.set_draw_color("#000000")

            elif t == "text":  # Posicion del acorde en la guitarra
                txt = str(shape.get("text", ""))
                txt_size = shape.get("size", 16)  # si el json trae size lo usamos
                try:
                    txt_size = float(txt_size) * s
                except Exception:
                    txt_size = 11 * s
                self.set_font("Osans", '', max(4, txt_size))
                # colocamos el texto relativo a num_x y fret_spacing
                if len(txt) > 1:
                    self.text(num_x + sx - 2, y + fret_spacing + sy + 1, txt)
                else:
                    self.text(num_x + sx - 1, y + fret_spacing + sy + 1, txt)

            elif t == "textx":
                txt = str(shape.get("text", ""))
                txt_size = shape.get("size", 11)
                try:
                    txt_size = float(txt_size) * s
                except Exception:
                    txt_size = 9 * s
                self.set_text_color("#cc0000")
                self.set_font("Helvetica", 'B', max(4, txt_size + 1))
                self.text(num_x + sx, y + fret_spacing + sy, " o" if txt == "o" else txt)
                self.set_text_color("#000000")

        # self.circle(x=x+24, y=y+25, radius=3, style="FD")
        # self.rect(x=x+5, y=y+2, w=25, h=5, style="FD")
        # self.text(num_x+10, y + fret_spacing - 10, "O")

    @staticmethod
    def parse_chords(chord_block: str):
        chords = []
        # pattern = r"([A-G][#b]?(?:m|dim|aug)?)([IVXLCDM]*)"
        pattern = r"([A-G][#b]?(?:m|dim|aug)?\d*)([IVXLCDM]*)"
        for match in re.finditer(pattern, chord_block):
            root, pos = match.groups()
            if not pos:
                pos = "I"
            chords.append([root, pos])
        return len(chords), chords

    def add_tab(self, tab_block):
        """
        Mantiene tu estilo original pero:
        - maneja líneas con '\n' (procesando sub-líneas)
        - calcula X absoluto usando self.l_margin para alinear iconos con cell(..., new_x=XPos.LMARGIN)
        - respeta bloques literales {…}
        """
        y_in = self.get_y()
        self.set_font("Consolas", '', self.size_text_code)

        icon_map = {
            "h": ("make/img/hammer.svg", 1, -1.5, 4),  # (archivo, dx, dy, ancho)
            "p": ("make/img/hammer.svg", 1, -1.5, 4),
            "b": ("make/img/bend.svg", 2.2, -2.4, 2),
        }

        # patrón que captura símbolo o bloque literal
        pattern = re.compile(r"([hpb])|\{([^}]+)\}")

        # altura por línea (usa la misma que en cell)
        line_h = 4

        for raw_line in tab_block:
            # Si la "línea" trae saltos, procesamos cada sub-línea por separado
            sublines = raw_line.splitlines() or ['']
            for sub in sublines:
                # Y actual antes de imprimir la sub-línea
                y_t = self.get_y()

                clean_line = ""
                last_index = 0

                # buscar coincidencias en la sub-línea
                # print("tablatura: ", sub)
                for m in pattern.finditer(sub):
                    start, end = m.span()

                    # texto anterior tal cual
                    clean_line += sub[last_index:start]

                    if m.group(1):
                        self.set_font("Consolas", '', self.size_text_code)
                        # símbolo h/p/b
                        symbol = m.group(1)
                        file, dx, dy, w = icon_map[symbol]

                        # prefix tal como se verá (reemplazando símbolos por espacios para medir)
                        prefix = sub[:start]
                        prefix_display = prefix.replace("h", " ").replace("p", " ").replace("b", " ")

                        # ancho absoluto desde el margen izquierdo
                        x_offset = self.get_string_width(prefix_display)
                        x_abs = self.l_margin + x_offset + dx-1

                        # colocar la imagen con coordenadas absolutas
                        self.image(file, x=x_abs, y=y_t + dy, w=w)

                        # sustituimos el símbolo por un solo espacio en la salida impresa
                        clean_line += " "

                    elif m.group(2):
                        # bloque literal {…} -> mantener su contenido SIN llaves
                        literal = m.group(2)
                        clean_line += literal
                        # self.set_font("Consolas", 'B', self.size_text_code)

                    last_index = end

                # añadir resto de la sub-línea
                clean_line += sub[last_index:]

                # imprimir la sub-línea (si está vacía hacemos salto)
                if clean_line == "":
                    self.ln(line_h)
                else:
                    # imprimimos anclando al margen izquierdo, como antes
                    self.cell(0, line_h, clean_line, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

            # fin for sublines

        y_end = self.get_y()

        # tu lógica de no_free
        if any(len(t) > 30 for t in tab_block):
            if self.get_y() > 98.0:
                self.no_free.append((y_in, y_end))

        self.ln(4)

