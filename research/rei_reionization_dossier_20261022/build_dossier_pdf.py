#!/usr/bin/env python3
"""Typeset the frozen reionization dossier and its auditable figure appendices.

Prepare only: run this script once the authored Markdown and renderer outputs are
frozen. PDF authoring is gated externally by the mandatory PDF skill marker.
"""
from __future__ import annotations

import argparse
import html
import json
import os
import re
from pathlib import Path

from PIL import Image as PILImage
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A3, A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.utils import simpleSplit
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate, Flowable, Frame, HRFlowable, Image, KeepTogether,
    NextPageTemplate, PageBreak, PageTemplate, Paragraph, Preformatted, Spacer, Table,
    TableStyle,
)
from reportlab.platypus.tableofcontents import TableOfContents

HERE = Path(__file__).resolve().parent
RESEARCH = HERE.parent
DEFAULT_MD = HERE / "REIONIZATION_DOSSIER_20261022.md"
DEFAULT_PDF = HERE / "REIONIZATION_DOSSIER_20261022.pdf"
DEFAULT_MANIFEST = HERE / "FIGURE_MANIFEST.json"
DEFAULT_STRONG_MANIFEST = HERE / "strong_pi_m" / "FIGURE_MANIFEST.json"
DEFAULT_INTERPRETATIONS = HERE / "FIGURE_PHYSICAL_INTERPRETATIONS.json"
DEFAULT_ATLAS_INDEX = HERE / "ATLAS_INDEX.json"
PRIOR_ATOMIC = RESEARCH / "rei_isotope_quotient_pilot_20261022" / "pilot" / "figures_final"
PRIOR_NUCLEAR = RESEARCH / "rei_tritium_production_audit_20261022"
NUCLEAR_FIGURES = (
    "NUCLEAR_NETWORK_T_BIRTHS.png", "02_births_vs_survival.png",
    "NUCLEAR_NETWORK_POPULATIONS.png", "01_DD_source.png",
    "NUCLEAR_NETWORK_TIME_TEMPERATURE.png",
)

INK = colors.HexColor("#18263d")
MUTED = colors.HexColor("#52657a")
ACCENT = colors.HexColor("#14688a")
PALE = colors.HexColor("#eaf2f5")
RULE = colors.HexColor("#c9d7df")
PAGE_W, PAGE_H = A4
LEFT = RIGHT = 52
TOP = 59
BOTTOM = 53
WIDTH = PAGE_W - LEFT - RIGHT
FRAME_HEIGHT = PAGE_H - TOP - BOTTOM
ATLAS_W, ATLAS_H = A3
ATLAS_LEFT = ATLAS_RIGHT = 45
ATLAS_TOP = 60
ATLAS_BOTTOM = 55
ATLAS_WIDTH = ATLAS_W - ATLAS_LEFT - ATLAS_RIGHT
ATLAS_HEIGHT = ATLAS_H - ATLAS_TOP - ATLAS_BOTTOM


def register_fonts() -> None:
    root = Path("/usr/share/fonts/truetype/dejavu")
    candidates = [
        ("Dossier", "DejaVuSans.ttf"),
        ("Dossier-Bold", "DejaVuSans-Bold.ttf"),
        ("Dossier-Mono", "DejaVuSansMono.ttf"),
    ]
    for name, filename in candidates:
        path = root / filename
        if not path.exists():
            raise FileNotFoundError(f"Unicode font missing: {path}")
        pdfmetrics.registerFont(TTFont(name, str(path)))
    pdfmetrics.registerFontFamily(
        "Dossier", normal="Dossier", bold="Dossier-Bold",
        italic="Dossier", boldItalic="Dossier-Bold",
    )


def styles() -> dict[str, ParagraphStyle]:
    base = dict(fontName="Dossier", allowWidows=0,
                allowOrphans=0, splitLongWords=1)
    return {
        "cover_kicker": ParagraphStyle("cover_kicker", fontSize=10, leading=16,
                                       textColor=ACCENT, spaceAfter=16, **base),
        "cover": ParagraphStyle("cover", fontSize=28, leading=37,
                                spaceAfter=22, **base),
        "cover_sub": ParagraphStyle("cover_sub", fontSize=12, leading=19,
                                    textColor=MUTED, **base),
        "h1": ParagraphStyle("h1", fontSize=17, leading=24, spaceBefore=0,
                             spaceAfter=12, keepWithNext=True, **base),
        "h2": ParagraphStyle("h2", fontSize=12.7, leading=19,
                             textColor=ACCENT, spaceBefore=17, spaceAfter=7,
                             keepWithNext=True, **base),
        "h3": ParagraphStyle("h3", fontSize=10.8, leading=16,
                             spaceBefore=12, spaceAfter=5,
                             keepWithNext=True, **base),
        "body": ParagraphStyle("body", fontSize=9.45, leading=15.1,
                               spaceAfter=9, **base),
        "bullet": ParagraphStyle("bullet", fontSize=9.45, leading=15.1,
                                 leftIndent=17, firstLineIndent=-11,
                                 spaceAfter=5, **base),
        "caption": ParagraphStyle("caption", fontSize=8.1, leading=12,
                                  textColor=MUTED, spaceBefore=5,
                                  spaceAfter=12, **base),
        "atlas_caption": ParagraphStyle("atlas_caption", fontSize=9.2, leading=14,
                                         textColor=MUTED, spaceBefore=6,
                                         spaceAfter=10, **base),
        "figure_interpretation": ParagraphStyle(
            "figure_interpretation", fontSize=9, leading=14,
            textColor=INK, spaceAfter=5, **base),
        "table_header": ParagraphStyle("table_header", fontSize=8,
                                       leading=11.4, textColor=colors.white,
                                       **base),
        "table_cell": ParagraphStyle("table_cell", fontSize=8,
                                     leading=11.4, **base),
        "toc_title": ParagraphStyle("toc_title", fontSize=17, leading=24,
                                    spaceAfter=16, **base),
        "code": ParagraphStyle("code", fontName="Dossier-Mono", fontSize=7.1,
                               leading=10, textColor=INK, spaceAfter=7),
        "note": ParagraphStyle("note", fontSize=8.5, leading=13,
                               textColor=MUTED, spaceAfter=9, **base),
    }


class DossierDoc(BaseDocTemplate):
    def __init__(self, output: Path, title: str, **kwargs):
        super().__init__(str(output), pagesize=A4, leftMargin=LEFT,
                         rightMargin=RIGHT, topMargin=TOP,
                         bottomMargin=BOTTOM, title=title,
                         author="REI Bianchi research dossier", **kwargs)
        frame = Frame(LEFT, BOTTOM, WIDTH, FRAME_HEIGHT, id="normal",
                      leftPadding=0, rightPadding=0, topPadding=0,
                      bottomPadding=0)
        atlas_frame = Frame(ATLAS_LEFT, ATLAS_BOTTOM, ATLAS_WIDTH,
                            ATLAS_HEIGHT, id="atlas", leftPadding=0,
                            rightPadding=0, topPadding=0, bottomPadding=0)
        self.addPageTemplates([
            PageTemplate(id="dossier", frames=frame, pagesize=A4,
                         onPage=self.decorate),
            PageTemplate(id="atlas", frames=atlas_frame, pagesize=A3,
                         onPage=self.decorate),
        ])
        self.section = "Research dossier"
        self._bookmark_seq = 0

    def beforeDocument(self):
        # multiBuild repeats the same flowables while resolving TOC page numbers.
        # Stable bookmark names are essential for convergence across passes.
        self._bookmark_seq = 0
        self.section = "Research dossier"

    def decorate(self, canvas, doc):
        canvas.saveState()
        page_w, page_h = canvas._pagesize
        margin = ATLAS_LEFT if doc.pageTemplate.id == "atlas" else LEFT
        page_width = page_w - 2 * margin
        if doc.page > 1:
            canvas.setStrokeColor(RULE)
            canvas.setLineWidth(.55)
            canvas.line(margin, page_h - 40, page_w - margin, page_h - 40)
            canvas.setFont("Dossier", 7.3)
            canvas.setFillColor(MUTED)
            header = self.section
            while pdfmetrics.stringWidth(header, "Dossier", 7.3) > page_width:
                header = header[:-4].rstrip() + "…"
            canvas.drawString(margin, page_h - 32, header)
        canvas.setStrokeColor(RULE)
        canvas.line(margin, 39, page_w - margin, 39)
        canvas.setFont("Dossier", 7.1)
        canvas.setFillColor(MUTED)
        canvas.drawString(margin, 26, "REIONIZATION · RESEARCH DOSSIER · SERIES 20261022")
        canvas.drawRightString(page_w - margin, 26, str(doc.page))
        canvas.restoreState()

    def afterFlowable(self, flowable):
        if isinstance(flowable, Paragraph) and hasattr(flowable, "dossier_level"):
            level = flowable.dossier_level
            title = flowable.dossier_title
            self._bookmark_seq += 1
            key = f"section-{self._bookmark_seq}"
            self.canv.bookmarkPage(key)
            self.notify("TOCEntry", (level, title, self.page, key))
            if level == 0:
                self.section = title


TEX = {
    r"\alpha": "α", r"\beta": "β", r"\gamma": "γ", r"\delta": "δ",
    r"\epsilon": "ε", r"\zeta": "ζ", r"\eta": "η", r"\theta": "θ",
    r"\lambda": "λ", r"\mu": "μ", r"\nu": "ν", r"\pi": "π",
    r"\rho": "ρ", r"\sigma": "σ", r"\tau": "τ", r"\phi": "φ",
    r"\omega": "ω", r"\Gamma": "Γ", r"\Delta": "Δ", r"\Sigma": "Σ",
    r"\Pi": "Π", r"\Omega": "Ω", r"\infty": "∞", r"\pm": "±",
    r"\times": "×", r"\cdot": "·", r"\leq": "≤", r"\geq": "≥",
    r"\le": "≤", r"\ge": "≥", r"\neq": "≠", r"\to": "→",
    r"\rightarrow": "→", r"\approx": "≈", r"\propto": "∝",
    r"\sum": "Σ", r"\partial": "∂", r"\nabla": "∇",
    r"\mathrm": "", r"\text": "", r"\left": "", r"\right": "",
}


def normalize_math(s: str) -> str:
    for source, target in sorted(TEX.items(), key=lambda x: -len(x[0])):
        s = s.replace(source, target)
    s = re.sub(r"\\frac\s*\{([^{}]+)\}\s*\{([^{}]+)\}", r"(\1)/(\2)", s)
    s = re.sub(r"\\(?:mathbf|mathcal|operatorname)\{([^{}]+)\}", r"\1", s)
    s = re.sub(r"_\{([^{}]+)\}", r"₍\1₎", s)
    s = re.sub(r"\^\{([^{}]+)\}", r"^(\1)", s)
    s = s.replace("$", "").replace("{", "").replace("}", "")
    return s


def inline(s: str) -> str:
    code_spans: list[str] = []

    def shield_code(match):
        code_spans.append(match.group(1))
        return f"CODETOKEN{len(code_spans) - 1:06d}END"

    s = re.sub(r"`([^`]+)`", shield_code, s)
    s = html.escape(normalize_math(s), quote=False)
    s = re.sub(r"!\[([^]]*)\]\(([^)]+)\)", r"\1 (\2)", s)
    s = re.sub(r"\[([^]]+)\]\(([^)]+)\)", r"\1", s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s)
    # Single '*' is also multiplication in the scientific manuscript. Only
    # tight, word-boundary emphasis is safe; code spans are restored afterward.
    s = re.sub(r"(?<![\w*])\*([^\s*]+)\*(?![\w*])", r"<i>\1</i>", s)
    for idx, code in enumerate(code_spans):
        token = f"CODETOKEN{idx:06d}END"
        s = s.replace(token, f"<font color='#14688a'>{html.escape(code, quote=False)}</font>")
    return s.replace("  ", " ")


def image_flow(path: Path, caption: str, sty: dict, max_height=460,
               max_width=WIDTH, caption_style="caption"):
    if not path.exists():
        raise FileNotFoundError(f"Figure referenced but missing: {path}")
    with PILImage.open(path) as im:
        w, h = im.size
    scale = min(max_width / w, max_height / h)
    visual = Image(str(path), width=w * scale, height=h * scale)
    visual.hAlign = "CENTER"
    return KeepTogether([
        visual,
        Paragraph(inline(caption), sty[caption_style]),
    ])


INTERPRETATION_LABELS = (
    ("what_to_read", "What to read"),
    ("physical_interpretation", "Physical interpretation"),
    ("nuclear_astro_context", "Nuclear astrophysics"),
    ("claim_limit", "Claim limit"),
)


def load_interpretations(path: Path, atlas_index: Path) -> dict[str, dict]:
    if not path.exists() or not atlas_index.exists():
        raise FileNotFoundError(f"Figure interpretations/index missing: {path}, {atlas_index}")
    data = json.loads(path.read_text(encoding="utf-8"))
    interpretations = data.get("figures", data)
    indexed = json.loads(atlas_index.read_text(encoding="utf-8"))
    keys = [entry["png"] for entry in indexed["figures"]]
    if len(keys) != 53 or len(set(keys)) != 53 or indexed.get("figure_designs") != 53:
        raise ValueError("ATLAS_INDEX must identify 53 unique PNG paths")
    if not isinstance(interpretations, dict) or set(interpretations) != set(keys):
        missing = sorted(set(keys) - set(interpretations)) if isinstance(interpretations, dict) else keys
        extra = sorted(set(interpretations) - set(keys)) if isinstance(interpretations, dict) else []
        raise ValueError(f"Interpretation/atlas path mismatch: missing={missing}, extra={extra}")
    for key, interpretation in interpretations.items():
        if not isinstance(interpretation, dict) or any(
            not isinstance(interpretation.get(field), str) or
            not interpretation[field].strip() for field, _ in INTERPRETATION_LABELS
        ):
            raise ValueError(f"Figure interpretation lacks four prose fields: {key}")
    return interpretations


def interpreted_figure(path: Path, caption: str, sty: dict,
                       interpretations: dict[str, dict], consumed: set[str]):
    key = Path(os.path.relpath(path, HERE)).as_posix()
    if key not in interpretations:
        raise ValueError(f"Figure absent from interpretation registry: {key}")
    if key in consumed:
        raise ValueError(f"Figure repeated in PDF appendices: {key}")
    consumed.add(key)
    content = [image_flow(path, caption, sty, max_height=780,
                          max_width=ATLAS_WIDTH, caption_style="atlas_caption")]
    for field, label in INTERPRETATION_LABELS:
        value = interpretations[key][field]
        content.append(Paragraph(f"<b>{label}.</b> {inline(value)}",
                                 sty["figure_interpretation"]))
    return content


def heading(title: str, level: int, sty):
    p = Paragraph(inline(title), sty[f"h{level}"])
    p.dossier_title = normalize_math(title)
    p.dossier_level = min(level - 1, 2)
    return p


def table_flow(rows: list[list[str]], sty: dict):
    if not rows:
        return []
    cols = max(map(len, rows))
    if cols > 8:
        raise ValueError("Table exceeds eight columns; simplify Markdown layout")
    width = WIDTH / cols
    contents = []
    for i, row in enumerate(rows):
        contents.append([
            Paragraph(inline(row[j]) if j < len(row) else "",
                      sty["table_header"] if i == 0 else sty["table_cell"])
            for j in range(cols)
        ])
    tbl = Table(contents, colWidths=[width] * cols, repeatRows=1,
                hAlign="LEFT", splitByRow=1)
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), ACCENT),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, PALE]),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 7),
        ("RIGHTPADDING", (0, 0), (-1, -1), 7),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LINEBELOW", (0, 0), (-1, 0), .5, ACCENT),
    ]))
    return [Spacer(1, 6), tbl, Spacer(1, 9)]


def parse_table(lines: list[str]):
    rows = [[cell.strip() for cell in line.strip().strip("|").split("|")]
            for line in lines]
    if len(rows) > 1 and all(re.fullmatch(r":?-{2,}:?", c) for c in rows[1]):
        del rows[1]
    return rows


def markdown_story(source: str, sty: dict, base: Path):
    story = []
    lines = source.splitlines()
    i = 0
    first_h1 = True
    while i < len(lines):
        line = lines[i].rstrip()
        if not line.strip():
            i += 1
            continue
        if line.startswith("```"):
            i += 1
            code = []
            while i < len(lines) and not lines[i].startswith("```"):
                code.extend(simpleSplit(lines[i].expandtabs(4), "Dossier-Mono", 7.1,
                                        WIDTH - 25) or [""])
                i += 1
            story.append(Preformatted("\n".join(code), sty["code"],
                                      maxLineLength=90, splitChars=" "))
            i += 1
            continue
        m = re.match(r"^(#{1,4})\s+(.+)$", line)
        if m:
            raw_level = len(m.group(1))
            title = m.group(2)
            if raw_level == 1 and first_h1:
                first_h1 = False  # title is already printed on the cover
                i += 1
                continue
            chapter = raw_level == 2 and bool(re.match(r"(?:\d+\.\s|References\b)", title))
            level = 1 if chapter else (raw_level - 1 if raw_level >= 3 else raw_level)
            level = max(1, min(level, 3))
            if raw_level == 1 or chapter:
                story.append(PageBreak())
            story.append(heading(title, level, sty))
            i += 1
            continue
        if line.lstrip().startswith("|"):
            group = []
            while i < len(lines) and lines[i].lstrip().startswith("|"):
                group.append(lines[i])
                i += 1
            story += table_flow(parse_table(group), sty)
            continue
        m = re.match(r"^!\[([^]]*)\]\(([^)]+)\)$", line.strip())
        if m:
            path = (base / m.group(2)).resolve()
            story.append(image_flow(path, m.group(1), sty))
            i += 1
            continue
        if re.fullmatch(r"[-*_]{3,}", line.strip()):
            story.append(HRFlowable(width="100%", color=RULE, thickness=.5,
                                    spaceBefore=10, spaceAfter=10))
            i += 1
            continue
        if line.strip() == "$$":
            i += 1
            math_lines = []
            while i < len(lines) and lines[i].strip() != "$$":
                math_lines.append(lines[i].strip())
                i += 1
            story.append(Paragraph(inline(" ".join(math_lines)), sty["body"]))
            i += 1
            continue
        m = re.match(r"^\s*(?:[-*+] |\d+[.)] )(.+)$", line)
        if m:
            label = line.strip().split(" ", 1)[0]
            mark = "•" if label[0] in "-*+" else label
            story.append(Paragraph(inline(mark + "  " + m.group(1)), sty["bullet"]))
            i += 1
            continue
        if line.startswith(">"):
            story.append(Paragraph(inline(line.lstrip("> ")), sty["note"]))
            i += 1
            continue
        para = [line]
        i += 1
        while i < len(lines) and lines[i].strip() and not re.match(
            r"^(?:#{1,4}\s|```|\s*\||!\[|\s*[-*+] |\s*\d+[.)] |\$\$|>)", lines[i]
        ):
            para.append(lines[i].strip())
            i += 1
        story.append(Paragraph(inline(" ".join(para)), sty["body"]))
    return story


def figure_appendix(sty, manifest_path: Path, strong_manifest_path: Path,
                    interpretation_path: Path = DEFAULT_INTERPRETATIONS,
                    atlas_index_path: Path = DEFAULT_ATLAS_INDEX):
    interpretations = load_interpretations(interpretation_path, atlas_index_path)
    consumed: set[str] = set()
    if not manifest_path.exists():
        raise FileNotFoundError(f"Figure manifest missing: {manifest_path}")
    gallery = manifest_path.with_name("GALLERY.html")
    if not gallery.exists():
        raise FileNotFoundError(f"Figure gallery missing: {gallery}")
    manifest = json.loads(manifest_path.read_text())
    entries = manifest.get("figures", [])
    if manifest.get("figure_count") != 28 or len(entries) != 28:
        raise ValueError("Expected exactly 28 new figures in renderer manifest")
    story = [PageBreak(), heading("Appendix A. New comparative figures", 1, sty),
             Paragraph("All 28 plots in the frozen renderer manifest follow. "
                       "Their PNG files are embedded; companion vector PDFs "
                       "and the HTML gallery remain in the figure directory.",
                       sty["note"])]
    for idx, entry in enumerate(entries, 1):
        if idx > 1:
            story.append(PageBreak())
        pngs = [n for n in entry.get("files", []) if n.endswith(".png")]
        pdfs = [n for n in entry.get("files", []) if n.endswith(".pdf")]
        if len(pngs) != 1 or len(pdfs) != 1:
            raise ValueError(f"Manifest figure {idx} lacks PNG/PDF pair")
        png = manifest_path.parent / pngs[0]
        if not (manifest_path.parent / pdfs[0]).exists():
            raise FileNotFoundError(pdfs[0])
        caption = (f"Figure A.{idx}. {entry['group'].replace('_', ' ').title()} — "
                   f"{entry['kind'].replace('_', ' ')}. "
                   f"Source class: {entry.get('source', 'saved trajectories')}.")
        if entry["group"] == "pi_m":
            caption += (" Original cold family, saved numerical accuracy; "
                        "stronger matched-family experiment follows.")
        story.extend(interpreted_figure(png, caption, sty, interpretations, consumed))

    strong_count = 0
    if strong_manifest_path.exists():
        strong_gallery = strong_manifest_path.with_name("GALLERY.html")
        if not strong_gallery.exists():
            raise FileNotFoundError(f"Strong-Pi_m gallery missing: {strong_gallery}")
        strong = json.loads(strong_manifest_path.read_text())
        strong_entries = strong.get("figures", [])
        if strong.get("figure_count") != 7 or len(strong_entries) != 7:
            raise ValueError("Expected seven strong-Pi_m figures in supplemental manifest")
        story.extend([PageBreak(), heading("Appendix B. Strong matter-stress comparison", 1, sty),
                      Paragraph("Seven supplemental strong-Pi_m panels accompany the "
                                "28-figure base atlas. Their case definitions and "
                                "numerical-control limits remain those in the "
                                "supplemental manifest and gallery.", sty["note"])])
        for idx, entry in enumerate(strong_entries, 1):
            if idx > 1:
                story.append(PageBreak())
            pngs = [n for n in entry.get("files", []) if str(n).endswith(".png")]
            pdfs = [n for n in entry.get("files", []) if str(n).endswith(".pdf")]
            if len(pngs) != 1 or len(pdfs) != 1:
                raise ValueError(f"Strong-Pi_m figure {idx} lacks PNG/PDF pair")
            png = strong_manifest_path.parent / pngs[0]
            if not (strong_manifest_path.parent / pdfs[0]).exists():
                raise FileNotFoundError(pdfs[0])
            label = entry.get("title") or entry.get("kind") or png.stem
            caption = f"Figure B.{idx}. Strong-Pi_m supplement: {label.replace('_', ' ')}."
            story.extend(interpreted_figure(png, caption, sty, interpretations, consumed))
        strong_count = len(strong_entries)

    atomic_letter = "C" if strong_count else "B"
    nuclear_letter = "D" if strong_count else "C"

    atomic = sorted(PRIOR_ATOMIC.glob("*.png")) if PRIOR_ATOMIC.exists() else []
    if atomic and len(atomic) != 13:
        raise ValueError(f"Expected 13 prior atomic figures; found {len(atomic)}")
    if atomic:
        story.extend([PageBreak(), heading(f"Appendix {atomic_letter}. Prior atomic pilot figures", 1, sty),
                      Paragraph("The 13 archived atomic-only pilot plots are reproduced "
                                "for comparison with the conditional nuclear extension.",
                                sty["note"])])
        for idx, path in enumerate(atomic, 1):
            if idx > 1:
                story.append(PageBreak())
            story.extend(interpreted_figure(
                path, f"Figure {atomic_letter}.{idx}. Atomic pilot: "
                f"{path.stem.replace('_', ' ')}.", sty, interpretations, consumed))

    nuclear = [PRIOR_NUCLEAR / name for name in NUCLEAR_FIGURES
               if (PRIOR_NUCLEAR / name).exists()]
    if nuclear and len(nuclear) != len(NUCLEAR_FIGURES):
        raise ValueError("Only part of the prior five-figure nuclear set is available")
    if nuclear:
        story.extend([PageBreak(), heading(f"Appendix {nuclear_letter}. Prior nuclear audit figures", 1, sty),
                      Paragraph("These five historical audit plots document the DD tracer "
                                "and eighteen-family conditional network. Their model "
                                "assumptions and dates are described in the corresponding "
                                "research reports.", sty["note"])])
        for idx, path in enumerate(nuclear, 1):
            if idx > 1:
                story.append(PageBreak())
            story.extend(interpreted_figure(
                path, f"Figure {nuclear_letter}.{idx}. Nuclear audit: "
                f"{path.stem.replace('_', ' ')}.", sty, interpretations, consumed))
    if consumed != set(interpretations):
        raise ValueError(f"Unembedded figure interpretations: {sorted(set(interpretations) - consumed)}")
    return story, strong_count


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--markdown", type=Path, default=DEFAULT_MD)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--strong-manifest", type=Path, default=DEFAULT_STRONG_MANIFEST,
                        help="Optional seven-figure strong-Pi_m supplement; embedded if present")
    parser.add_argument("--interpretations", type=Path, default=DEFAULT_INTERPRETATIONS)
    parser.add_argument("--atlas-index", type=Path, default=DEFAULT_ATLAS_INDEX)
    parser.add_argument("--output", type=Path, default=DEFAULT_PDF)
    args = parser.parse_args()
    if not args.markdown.exists():
        parser.error(f"Authored dossier missing: {args.markdown}")
    register_fonts()
    sty = styles()
    source = args.markdown.read_text(encoding="utf-8")
    match = re.search(r"^#\s+(.+)$", source, re.MULTILINE)
    title = match.group(1).strip() if match else "Reionization research dossier"
    toc = TableOfContents()
    toc.levelStyles = [
        ParagraphStyle("toc0", fontName="Dossier", fontSize=9.4, leading=15,
                       leftIndent=0, firstLineIndent=0, spaceBefore=7),
        ParagraphStyle("toc1", fontName="Dossier", fontSize=8.4, leading=13,
                       leftIndent=18, firstLineIndent=0),
        ParagraphStyle("toc2", fontName="Dossier", fontSize=7.8, leading=11,
                       leftIndent=35, firstLineIndent=0),
    ]
    story = [Spacer(1, 110), Paragraph("REI BIANCHI · SERIES 20261022", sty["cover_kicker"]),
             HRFlowable(width="21%", color=ACCENT, thickness=2.5,
                        hAlign="LEFT", spaceAfter=23),
             Paragraph(inline(title), sty["cover"]),
             Paragraph("Revised scientific dossier · series identifier 20261022", sty["cover_sub"]),
             Spacer(1, 43),
             Paragraph("Preliminary isotope–ion atlas and conditional nuclear kinetics",
                       sty["cover_sub"]),
             PageBreak(), Paragraph("Contents", sty["toc_title"]), toc,
             PageBreak()]
    story += markdown_story(source, sty, args.markdown.parent)
    appendix, strong_count = figure_appendix(sty, args.manifest, args.strong_manifest,
                                             args.interpretations, args.atlas_index)
    story += [NextPageTemplate("atlas")] + appendix
    args.output.parent.mkdir(parents=True, exist_ok=True)
    DossierDoc(args.output, title).multiBuild(story, maxPasses=3)
    print(json.dumps({"pdf": str(args.output), "new_figures": 28,
                      "strong_pi_m_figures": strong_count,
                      "prior_atomic": len(list(PRIOR_ATOMIC.glob('*.png'))),
                      "prior_nuclear": len([p for p in map(lambda n: PRIOR_NUCLEAR / n,
                                                          NUCLEAR_FIGURES) if p.exists()])}))


if __name__ == "__main__":
    main()
