import re
import shutil
import time

from make.extPDF import SongbookPDF
import tempfile
import os
import fitz
from configparser import ConfigParser


def make_book(pathin, new=True, temp=""):
    with open(pathin, "r", encoding="utf-8") as f:
        md_content = f.read()

    # extraer metadatos (entre --- ---)
    meta_match = re.search(r"---(.*?)---", md_content, re.DOTALL)
    meta = {}
    if meta_match:
        for line in meta_match.group(1).splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                meta[k.strip()] = v.strip()
        body = md_content[meta_match.end():]
    else:
        body = md_content
    # crear temporales
    if new:
        tempdir = tempfile.mkdtemp(prefix="pdf_view_")
    else:
        tempdir = temp

    filename = os.path.basename(pathin)
    filename = os.path.splitext(filename)[0]
    filename = filename + ".pdf"
    file = os.path.join(tempdir, filename)

    if os.path.exists(file):
        for _ in range(5):
            try:
                if os.path.exists(file):
                    os.remove(file)
                break
            except PermissionError:
                time.sleep(0.1)

    # generar pdf
    argument = [False, 0, None, 125.0, 250, 16, 11, 11, 12, 11, 0.6]
    if os.path.isfile("config/config.cfg"):
        cfg = ConfigParser()
        cfg.read("config/config.cfg")
        page = cfg["PAGE"]
        argument[0] = bool(int(page["twocolumn"]))  # 1 True 0 False
        argument[1] = float(page["xpos"])
        argument[2] = page["format"]  # 'None' 'a3', 'a4', 'a5', 'letter', or 'legal'
        argument[3] = float(page["width"])
        argument[4] = float(page["height"])
        fontsize = cfg["FONTSIZE"]
        argument[5] = int(fontsize["chordnumber"])
        argument[6] = int(fontsize["chordsymbol"])
        argument[7] = int(fontsize["tab"])
        argument[8] = int(fontsize["verse"])
        argument[9] = int(fontsize["body"])
        chord = cfg["CHORD"]
        argument[10] = float(chord["scale"])

    pdf = None
    if argument[2] == "None":
        pdf = SongbookPDF(twocolumn=argument[0], x_pos=argument[1], page_format=(argument[3], argument[4]),
                          size_code=argument[7], size_verse=argument[8], size_body=argument[9], scale=argument[10])
    else:
        pdf = SongbookPDF(twocolumn=argument[0], x_pos=argument[1], page_format=argument[2], size_code=argument[7],
                          size_verse=argument[8], size_body=argument[9], scale=argument[10])
    pdf.add_page()
    pdf.set_left_margin(1)
    pdf.set_right_margin(1)
    pdf.add_song(meta, body)
    pdf.output(file)

    # generar imagenes
    pdfz = fitz.open(file)
    filepng = os.path.join(tempdir, "img")

    if os.path.isdir(filepng):  # si existe - eliminar y crear nuevo
        shutil.rmtree(filepng)
        os.mkdir(filepng)
    else:
        os.mkdir(filepng)

    for pg in range(pdfz.page_count):
        page = pdfz.load_page(pg)
        pix = page.get_pixmap(dpi=250)
        files = os.path.join(filepng, f"{pg}.png")
        pix.save(files)
    pdf = None
    pdfz = None

    return [filename, tempdir]
