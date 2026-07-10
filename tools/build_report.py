#!/usr/bin/env python3
"""Build the polished DOCX version of docs/EXPERIMENT_REPORT.md."""

from __future__ import annotations

import argparse
import re
from pathlib import Path

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_ALIGN_VERTICAL, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK, WD_TAB_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor


BODY_FONT = "Noto Sans CJK SC"
LATIN_FONT = "Calibri"
CODE_FONT = "Liberation Mono"
NAVY = "203748"
BLUE = "2E74B5"
DARK_BLUE = "1F4D78"
TEXT = "263238"
MUTED = "66727C"
LIGHT_FILL = "F2F4F7"
CODE_FILL = "F5F7FA"
GRID = "D9E0E7"
GOLD = "A87916"
CONTENT_DXA = 9360


def rgb(value: str) -> RGBColor:
    return RGBColor.from_string(value)


def set_run_font(run, *, size=None, bold=None, italic=None, color=None, code=False):
    font = CODE_FONT if code else LATIN_FONT
    run.font.name = font
    run._element.get_or_add_rPr().rFonts.set(qn("w:ascii"), font)
    run._element.get_or_add_rPr().rFonts.set(qn("w:hAnsi"), font)
    run._element.get_or_add_rPr().rFonts.set(qn("w:eastAsia"), BODY_FONT)
    if size is not None:
        run.font.size = Pt(size)
    if bold is not None:
        run.bold = bold
    if italic is not None:
        run.italic = italic
    if color is not None:
        run.font.color.rgb = rgb(color)
    lang = run._element.get_or_add_rPr().find(qn("w:lang"))
    if lang is None:
        lang = OxmlElement("w:lang")
        run._element.get_or_add_rPr().append(lang)
    lang.set(qn("w:val"), "en-US" if code else "zh-CN")
    lang.set(qn("w:eastAsia"), "zh-CN")


def set_style_font(style, *, size, color=TEXT, bold=False):
    style.font.name = LATIN_FONT
    style._element.get_or_add_rPr().rFonts.set(qn("w:ascii"), LATIN_FONT)
    style._element.get_or_add_rPr().rFonts.set(qn("w:hAnsi"), LATIN_FONT)
    style._element.get_or_add_rPr().rFonts.set(qn("w:eastAsia"), BODY_FONT)
    style.font.size = Pt(size)
    style.font.bold = bold
    style.font.color.rgb = rgb(color)


def configure_styles(doc: Document):
    normal = doc.styles["Normal"]
    # Named technical-report density override: 10.5 pt body text keeps long
    # C identifiers intact while remaining comfortably readable.
    set_style_font(normal, size=10.5, color=TEXT)
    normal.paragraph_format.space_before = Pt(0)
    normal.paragraph_format.space_after = Pt(6)
    normal.paragraph_format.line_spacing = 1.10
    # Do not split Latin identifiers such as copy-on-write or page tables in
    # the middle of a word when they appear inside Chinese prose.
    normal_ppr = normal._element.get_or_add_pPr()
    word_wrap = OxmlElement("w:wordWrap")
    word_wrap.set(qn("w:val"), "0")
    normal_ppr.append(word_wrap)

    h1 = doc.styles["Heading 1"]
    set_style_font(h1, size=16, color=BLUE, bold=True)
    h1.paragraph_format.space_before = Pt(16)
    h1.paragraph_format.space_after = Pt(8)
    h1.paragraph_format.keep_with_next = True

    h2 = doc.styles["Heading 2"]
    set_style_font(h2, size=13, color=BLUE, bold=True)
    h2.paragraph_format.space_before = Pt(12)
    h2.paragraph_format.space_after = Pt(6)
    h2.paragraph_format.keep_with_next = True

    h3 = doc.styles["Heading 3"]
    set_style_font(h3, size=12, color=DARK_BLUE, bold=True)
    h3.paragraph_format.space_before = Pt(8)
    h3.paragraph_format.space_after = Pt(4)
    h3.paragraph_format.keep_with_next = True


def configure_page(doc: Document):
    section = doc.sections[0]
    section.page_width = Inches(8.5)
    section.page_height = Inches(11)
    section.top_margin = Inches(1)
    section.right_margin = Inches(1)
    section.bottom_margin = Inches(1)
    section.left_margin = Inches(1)
    section.header_distance = Inches(0.492)
    section.footer_distance = Inches(0.492)
    section.different_first_page_header_footer = True

    # A quiet running header, with no decorative border.
    header = section.header
    p = header.paragraphs[0]
    p.paragraph_format.space_after = Pt(0)
    p.paragraph_format.tab_stops.add_tab_stop(Inches(6.5), WD_TAB_ALIGNMENT.RIGHT)
    run = p.add_run("xv6 Labs 实验报告")
    set_run_font(run, size=8.5, color=MUTED)
    run = p.add_run("\tMIT 6.S081 Fall 2020")
    set_run_font(run, size=8.5, color=MUTED)

    footer = section.footer
    fp = footer.paragraphs[0]
    fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    fp.paragraph_format.space_before = Pt(0)
    run = fp.add_run("—  ")
    set_run_font(run, size=8.5, color=MUTED)
    add_page_field(fp)
    run = fp.add_run("  —")
    set_run_font(run, size=8.5, color=MUTED)

    section.first_page_header.paragraphs[0].text = ""
    section.first_page_footer.paragraphs[0].text = ""


def add_page_field(paragraph):
    run = paragraph.add_run()
    set_run_font(run, size=8.5, color=MUTED)
    begin = OxmlElement("w:fldChar")
    begin.set(qn("w:fldCharType"), "begin")
    instr = OxmlElement("w:instrText")
    instr.set(qn("xml:space"), "preserve")
    instr.text = " PAGE "
    separate = OxmlElement("w:fldChar")
    separate.set(qn("w:fldCharType"), "separate")
    text = OxmlElement("w:t")
    text.text = "1"
    end = OxmlElement("w:fldChar")
    end.set(qn("w:fldCharType"), "end")
    run._r.extend([begin, instr, separate, text, end])


def add_cover(doc: Document):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(86)
    p.paragraph_format.space_after = Pt(14)
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("操作系统课程项目")
    set_run_font(r, size=11, bold=True, color=GOLD)

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(10)
    r = p.add_run("xv6 及 Labs 实验报告")
    set_run_font(r, size=29, bold=True, color=NAVY)

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(12)
    r = p.add_run("MIT 6.S081 Fall 2020 · RISC-V")
    set_run_font(r, size=15, color=DARK_BLUE)

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(78)
    r = p.add_run("11 个实验全部完成｜官方评分全部通过｜独立分支可复现")
    set_run_font(r, size=10.5, bold=True, color=MUTED)

    metadata = [
        ("姓名", "________________"),
        ("学号", "________________"),
        ("班级", "________________"),
        ("项目仓库", "github.com/YoumiaHina/xv6-labs-2020（Private）"),
        ("实验环境", "WSL2 · Ubuntu 24.04 · QEMU 8.2 · RISC-V GCC 13.2"),
        ("完成时间", "2026 年 7 月"),
    ]
    for label, value in metadata:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_after = Pt(4)
        r = p.add_run(f"{label}：")
        set_run_font(r, size=10.5, bold=True, color=NAVY)
        r = p.add_run(value)
        set_run_font(r, size=10.5, color=TEXT)

    doc.add_page_break()


class NumberingManager:
    def __init__(self, doc: Document):
        self.root = doc.part.numbering_part.element
        existing_abs = [
            int(x.get(qn("w:abstractNumId")))
            for x in self.root.findall(qn("w:abstractNum"))
        ]
        existing_num = [
            int(x.get(qn("w:numId"))) for x in self.root.findall(qn("w:num"))
        ]
        self.next_abs = max(existing_abs, default=-1) + 1
        self.next_num = max(existing_num, default=0) + 1
        self.abstract = {
            "bullet": self._add_abstract("bullet"),
            "decimal": self._add_abstract("decimal"),
        }

    def _add_abstract(self, kind: str) -> int:
        aid = self.next_abs
        self.next_abs += 1
        abstract = OxmlElement("w:abstractNum")
        abstract.set(qn("w:abstractNumId"), str(aid))
        multi = OxmlElement("w:multiLevelType")
        multi.set(qn("w:val"), "singleLevel")
        abstract.append(multi)
        lvl = OxmlElement("w:lvl")
        lvl.set(qn("w:ilvl"), "0")
        start = OxmlElement("w:start")
        start.set(qn("w:val"), "1")
        lvl.append(start)
        fmt = OxmlElement("w:numFmt")
        fmt.set(qn("w:val"), kind)
        lvl.append(fmt)
        text = OxmlElement("w:lvlText")
        text.set(qn("w:val"), "•" if kind == "bullet" else "%1.")
        lvl.append(text)
        jc = OxmlElement("w:lvlJc")
        jc.set(qn("w:val"), "left")
        lvl.append(jc)
        ppr = OxmlElement("w:pPr")
        tabs = OxmlElement("w:tabs")
        tab = OxmlElement("w:tab")
        tab.set(qn("w:val"), "num")
        tab.set(qn("w:pos"), "720")
        tabs.append(tab)
        ppr.append(tabs)
        ind = OxmlElement("w:ind")
        ind.set(qn("w:left"), "720")
        ind.set(qn("w:hanging"), "360")
        ppr.append(ind)
        spacing = OxmlElement("w:spacing")
        spacing.set(qn("w:after"), "160")
        spacing.set(qn("w:line"), "280")
        spacing.set(qn("w:lineRule"), "auto")
        ppr.append(spacing)
        lvl.append(ppr)
        abstract.append(lvl)
        self.root.append(abstract)
        return aid

    def new_instance(self, kind: str) -> int:
        num_id = self.next_num
        self.next_num += 1
        num = OxmlElement("w:num")
        num.set(qn("w:numId"), str(num_id))
        ref = OxmlElement("w:abstractNumId")
        ref.set(qn("w:val"), str(self.abstract[kind]))
        num.append(ref)
        if kind == "decimal":
            override = OxmlElement("w:lvlOverride")
            override.set(qn("w:ilvl"), "0")
            start_override = OxmlElement("w:startOverride")
            start_override.set(qn("w:val"), "1")
            override.append(start_override)
            num.append(override)
        self.root.append(num)
        return num_id

    @staticmethod
    def apply(paragraph, num_id: int):
        ppr = paragraph._p.get_or_add_pPr()
        numpr = ppr.find(qn("w:numPr"))
        if numpr is None:
            numpr = OxmlElement("w:numPr")
            ppr.append(numpr)
        ilvl = OxmlElement("w:ilvl")
        ilvl.set(qn("w:val"), "0")
        numid = OxmlElement("w:numId")
        numid.set(qn("w:val"), str(num_id))
        numpr.extend([ilvl, numid])


INLINE_RE = re.compile(r"(`[^`]+`|\*\*[^*]+\*\*|<https?://[^>]+>)")


def add_inline(paragraph, text: str, *, size=10.5, color=TEXT, bold=False):
    pos = 0
    for match in INLINE_RE.finditer(text):
        if match.start() > pos:
            run = paragraph.add_run(text[pos : match.start()])
            set_run_font(run, size=size, color=color, bold=bold)
        token = match.group(0)
        if token.startswith("`"):
            code_text = token[1:-1].replace(" ", "\u00a0")
            run = paragraph.add_run(code_text)
            set_run_font(run, size=size - 0.5, color=DARK_BLUE, code=True)
        elif token.startswith("**"):
            run = paragraph.add_run(token[2:-2])
            set_run_font(run, size=size, color=color, bold=True)
        else:
            run = paragraph.add_run(token[1:-1])
            set_run_font(run, size=size - 0.5, color=BLUE)
            run.underline = True
        pos = match.end()
    if pos < len(text):
        run = paragraph.add_run(text[pos:])
        set_run_font(run, size=size, color=color, bold=bold)


def shade_paragraph(paragraph, fill: str):
    ppr = paragraph._p.get_or_add_pPr()
    shd = ppr.find(qn("w:shd"))
    if shd is None:
        shd = OxmlElement("w:shd")
        ppr.append(shd)
    shd.set(qn("w:fill"), fill)
    p_bdr = OxmlElement("w:pBdr")
    left = OxmlElement("w:left")
    left.set(qn("w:val"), "single")
    left.set(qn("w:sz"), "18")
    left.set(qn("w:space"), "7")
    left.set(qn("w:color"), BLUE)
    p_bdr.append(left)
    ppr.append(p_bdr)


def add_code_block(doc: Document, lines: list[str]):
    p = doc.add_paragraph()
    p.paragraph_format.left_indent = Inches(0.12)
    p.paragraph_format.right_indent = Inches(0.05)
    p.paragraph_format.space_before = Pt(3)
    p.paragraph_format.space_after = Pt(7)
    p.paragraph_format.line_spacing = 1.05
    p.paragraph_format.keep_together = True
    shade_paragraph(p, CODE_FILL)
    run = p.add_run("\n".join(lines))
    set_run_font(run, size=8.5, color=TEXT, code=True)


def set_repeat_header(row):
    trpr = row._tr.get_or_add_trPr()
    tbl_header = OxmlElement("w:tblHeader")
    tbl_header.set(qn("w:val"), "true")
    trpr.append(tbl_header)


def set_cell_margins(cell, top=80, start=120, bottom=80, end=120):
    tcpr = cell._tc.get_or_add_tcPr()
    tc_mar = tcpr.first_child_found_in("w:tcMar")
    if tc_mar is None:
        tc_mar = OxmlElement("w:tcMar")
        tcpr.append(tc_mar)
    for tag, value in (("top", top), ("start", start), ("bottom", bottom), ("end", end)):
        node = tc_mar.find(qn(f"w:{tag}"))
        if node is None:
            node = OxmlElement(f"w:{tag}")
            tc_mar.append(node)
        node.set(qn("w:w"), str(value))
        node.set(qn("w:type"), "dxa")


def table_widths(ncols: int) -> list[int]:
    if ncols == 2:
        return [2600, 6760]
    if ncols == 4:
        return [600, 3300, 3500, 1960]
    base = CONTENT_DXA // ncols
    widths = [base] * ncols
    widths[-1] += CONTENT_DXA - sum(widths)
    return widths


def set_table_geometry(table, widths: list[int]):
    table.autofit = False
    table.alignment = WD_TABLE_ALIGNMENT.LEFT
    tblpr = table._tbl.tblPr
    layout = tblpr.find(qn("w:tblLayout"))
    if layout is None:
        layout = OxmlElement("w:tblLayout")
        tblpr.append(layout)
    layout.set(qn("w:type"), "fixed")
    tblw = tblpr.find(qn("w:tblW"))
    tblw.set(qn("w:w"), str(CONTENT_DXA))
    tblw.set(qn("w:type"), "dxa")
    tblind = tblpr.find(qn("w:tblInd"))
    if tblind is None:
        tblind = OxmlElement("w:tblInd")
        tblpr.append(tblind)
    tblind.set(qn("w:w"), "120")
    tblind.set(qn("w:type"), "dxa")

    borders = tblpr.find(qn("w:tblBorders"))
    if borders is None:
        borders = OxmlElement("w:tblBorders")
        tblpr.append(borders)
    for name in ("top", "left", "bottom", "right", "insideH", "insideV"):
        edge = borders.find(qn(f"w:{name}"))
        if edge is None:
            edge = OxmlElement(f"w:{name}")
            borders.append(edge)
        edge.set(qn("w:val"), "single")
        edge.set(qn("w:sz"), "4")
        edge.set(qn("w:color"), GRID)

    grid = table._tbl.tblGrid
    for child in list(grid):
        grid.remove(child)
    for width in widths:
        col = OxmlElement("w:gridCol")
        col.set(qn("w:w"), str(width))
        grid.append(col)

    for row in table.rows:
        for idx, cell in enumerate(row.cells):
            tcpr = cell._tc.get_or_add_tcPr()
            tcw = tcpr.find(qn("w:tcW"))
            tcw.set(qn("w:w"), str(widths[idx]))
            tcw.set(qn("w:type"), "dxa")
            cell.width = Inches(widths[idx] / 1440)
            set_cell_margins(cell)
            cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER


def add_markdown_table(doc: Document, rows: list[list[str]]):
    table = doc.add_table(rows=len(rows), cols=len(rows[0]))
    widths = table_widths(len(rows[0]))
    for ridx, row in enumerate(rows):
        for cidx, value in enumerate(row):
            cell = table.cell(ridx, cidx)
            p = cell.paragraphs[0]
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(0)
            p.paragraph_format.line_spacing = 1.05
            if cidx == 0 or (len(row) == 4 and cidx == 3):
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            add_inline(p, value, size=9.3, bold=(ridx == 0))
            if ridx == 0:
                tcpr = cell._tc.get_or_add_tcPr()
                shd = OxmlElement("w:shd")
                shd.set(qn("w:fill"), LIGHT_FILL)
                tcpr.append(shd)
    set_repeat_header(table.rows[0])
    set_table_geometry(table, widths)
    spacer = doc.add_paragraph()
    spacer.paragraph_format.space_after = Pt(2)


def parse_table_row(line: str) -> list[str]:
    return [part.strip() for part in line.strip().strip("|").split("|")]


def is_separator_row(line: str) -> bool:
    cells = parse_table_row(line)
    return bool(cells) and all(re.fullmatch(r":?-{3,}:?", c) for c in cells)


def is_special(lines: list[str], i: int) -> bool:
    line = lines[i]
    if not line.strip():
        return True
    if line.startswith(("#", ">", "```", "- ")):
        return True
    if re.match(r"^\d+\.\s+", line):
        return True
    if line.strip().startswith("|"):
        return True
    return False


def add_body_from_markdown(doc: Document, source: Path):
    lines = source.read_text(encoding="utf-8").splitlines()
    numbering = NumberingManager(doc)
    active_kind = None
    active_num = None
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        if not stripped:
            active_kind = None
            active_num = None
            i += 1
            continue
        if line.startswith("# ") or line.startswith(">"):
            i += 1
            continue
        if line.startswith("```"):
            active_kind = None
            active_num = None
            i += 1
            code = []
            while i < len(lines) and not lines[i].startswith("```"):
                code.append(lines[i])
                i += 1
            if i < len(lines):
                i += 1
            add_code_block(doc, code)
            continue
        if stripped.startswith("|") and i + 1 < len(lines) and is_separator_row(lines[i + 1]):
            active_kind = None
            active_num = None
            rows = [parse_table_row(line)]
            i += 2
            while i < len(lines) and lines[i].strip().startswith("|"):
                rows.append(parse_table_row(lines[i]))
                i += 1
            add_markdown_table(doc, rows)
            continue
        if line.startswith("## "):
            active_kind = None
            active_num = None
            text = line[3:].strip()
            p = doc.add_paragraph(style="Heading 1")
            if re.match(r"\d+\. Lab", text) or text.startswith(("13. 综合分析", "16. 参考资料")):
                p.paragraph_format.page_break_before = True
            add_inline(p, text, size=16, color=BLUE, bold=True)
            i += 1
            continue
        if line.startswith("### "):
            active_kind = None
            active_num = None
            text = line[4:].strip()
            p = doc.add_paragraph(style="Heading 2")
            add_inline(p, text, size=13, color=BLUE, bold=True)
            i += 1
            continue
        kind = None
        item = None
        if line.startswith("- "):
            kind = "bullet"
            item = line[2:].strip()
        else:
            match = re.match(r"^\d+\.\s+(.*)$", line)
            if match:
                kind = "decimal"
                item = match.group(1).strip()
        if kind:
            if active_kind != kind:
                active_num = numbering.new_instance(kind)
                active_kind = kind
            i += 1
            continuation = []
            while i < len(lines):
                next_line = lines[i]
                if not next_line.strip() or next_line.startswith(("#", ">", "```", "- ")):
                    break
                if re.match(r"^\d+\.\s+", next_line) or next_line.strip().startswith("|"):
                    break
                continuation.append(next_line.strip())
                i += 1
            if continuation:
                item += " " + " ".join(continuation)
            p = doc.add_paragraph()
            p.paragraph_format.space_after = Pt(8)
            p.paragraph_format.line_spacing = 1.167
            numbering.apply(p, active_num)
            add_inline(p, item)
            continue

        active_kind = None
        active_num = None
        paragraph_lines = [stripped]
        i += 1
        while i < len(lines) and not is_special(lines, i):
            paragraph_lines.append(lines[i].strip())
            i += 1
        p = doc.add_paragraph()
        text = " ".join(paragraph_lines)
        add_inline(p, text)


def set_update_fields(doc: Document):
    settings = doc.settings._element
    node = settings.find(qn("w:updateFields"))
    if node is None:
        node = OxmlElement("w:updateFields")
        settings.append(node)
    node.set(qn("w:val"), "true")


def build(source: Path, output: Path):
    doc = Document()
    doc.core_properties.title = "xv6 及 Labs 课程项目实验报告（MIT 6.S081 Fall 2020）"
    doc.core_properties.subject = "MIT 6.S081 Fall 2020 全部 11 个 xv6 Labs"
    doc.core_properties.author = "YoumiaHina"
    doc.core_properties.keywords = "xv6, MIT 6.S081, RISC-V, operating systems"
    configure_page(doc)
    configure_styles(doc)
    set_update_fields(doc)
    add_cover(doc)
    add_body_from_markdown(doc, source)
    output.parent.mkdir(parents=True, exist_ok=True)
    doc.save(output)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    build(args.source.resolve(), args.output.resolve())
    print(args.output.resolve())


if __name__ == "__main__":
    main()
