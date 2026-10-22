#!/usr/bin/env python3
from pathlib import Path
import pymupdf

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "assets"
PAGE_WIDTH = 612.0
PAGE_HEIGHT = 842.25
BACKGROUND_RECT = pymupdf.Rect(-0.0042724609375, -14.44415283203125, 611.9957275390625, 932.8058471679688)
LOGO_RECT = pymupdf.Rect(60.0, 648.0, 245.0, 715.0)

pdf = pymupdf.open()
page = pdf.new_page(width=PAGE_WIDTH, height=PAGE_HEIGHT)
page.insert_image(BACKGROUND_RECT, filename=str(ASSETS / "33labs-report-cover-background.png"), rotate=90, keep_proportion=False)
page.insert_image(LOGO_RECT, filename=str(ASSETS / "33labs-logo-white.png"), overlay=True)
font_name = "DarkerGrotesqueBold"
page.insert_font(fontname=font_name, fontfile=str(ASSETS / "DarkerGrotesque-Bold.ttf"))
page.insert_text(pymupdf.Point(61.2, 750.8553), "Plazm", fontname=font_name, fontsize=36, color=(1, 1, 1), overlay=True)
page.insert_text(pymupdf.Point(61.2, 784.6053), "Launch-Path Audit Report", fontname=font_name, fontsize=30, color=(1, 1, 1), overlay=True)

path = ASSETS / "plazm-launch-path-cover.pdf"
pdf.set_metadata({"title": "Plazm Launch-Path Security Audit Report Cover", "author": "33Labs"})
pdf.save(path, garbage=4, deflate=True)
pdf.close()
print(path)
