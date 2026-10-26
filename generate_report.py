"""
Generate College Project Report for CloudDedup
Preserves the exact original 10-page college report format:
- Times New Roman font throughout
- Double-line page borders on all pages
- Crisp official screenshots (architecture_diagram.png, dashboard_top_cards.png, dashboard_stats_overview.png, college_logo.jpg)
- Comprehensive coverage of Flask, Firebase, MySQL 8.0, SHA-256 CAS, and 64.74% real test metrics
"""

import os
from pathlib import Path
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DOCX = BASE_DIR / "Cloud_File_Deduplication_Project_Report.docx"
DOWNLOADS_DOCX = Path("C:/Users/PRASANNA/Downloads/Cloud_File_Deduplication_Project_Report.docx")
OUTPUT_PDF = BASE_DIR / "Cloud_File_Deduplication_Project_Report.pdf"
DOWNLOADS_PDF = Path("C:/Users/PRASANNA/Downloads/Cloud_File_Deduplication_Project_Report.pdf")

COLOR_PRIMARY = RGBColor(30, 58, 138)    # Deep Navy
COLOR_SECONDARY = RGBColor(71, 85, 105)  # Slate
COLOR_TEXT = RGBColor(30, 41, 59)        # Body text

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{m}')
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def set_cell_background(cell, fill_hex):
    shading_xml = f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>'
    cell._tc.get_or_add_tcPr().append(parse_xml(shading_xml))

def set_cell_borders(cell, top="CBD5E1", bottom="CBD5E1", left="CBD5E1", right="CBD5E1"):
    borders_xml = f'''
    <w:tcBorders {nsdecls("w")}>
        <w:top w:val="single" w:sz="4" w:space="0" w:color="{top}"/>
        <w:left w:val="single" w:sz="4" w:space="0" w:color="{left}"/>
        <w:bottom w:val="single" w:sz="4" w:space="0" w:color="{bottom}"/>
        <w:right w:val="single" w:sz="4" w:space="0" w:color="{right}"/>
    </w:tcBorders>
    '''
    cell._tc.get_or_add_tcPr().append(parse_xml(borders_xml))

def add_page_number(run):
    fldSimple = OxmlElement('w:fldSimple')
    fldSimple.set(qn('w:instr'), 'PAGE')
    run._r.append(fldSimple)

def add_double_page_border(section):
    sectPr = section._sectPr
    pgBorders = parse_xml(
        f'<w:pgBorders {nsdecls("w")} w:offsetFrom="page">'
        f'<w:top w:val="double" w:sz="12" w:space="24" w:color="1E3A8A"/>'
        f'<w:bottom w:val="double" w:sz="12" w:space="24" w:color="1E3A8A"/>'
        f'<w:left w:val="double" w:sz="12" w:space="24" w:color="1E3A8A"/>'
        f'<w:right w:val="double" w:sz="12" w:space="24" w:color="1E3A8A"/>'
        f'</w:pgBorders>'
    )
    sectPr.append(pgBorders)

def set_font_times(run, size_pt=11, bold=False, italic=False, color=None):
    run.font.name = "Times New Roman"
    run.font.size = Pt(size_pt)
    run.bold = bold
    run.italic = italic
    if color:
        run.font.color.rgb = color
    rPr = run._r.get_or_add_rPr()
    rFonts = parse_xml(f'<w:rFonts {nsdecls("w")} w:ascii="Times New Roman" w:hAnsi="Times New Roman" w:cs="Times New Roman"/>')
    rPr.append(rFonts)

def generate_report():
    doc = Document()

    # Base Normal Style setup
    normal_style = doc.styles['Normal']
    normal_font = normal_style.font
    normal_font.name = 'Times New Roman'
    normal_font.size = Pt(11)
    normal_font.color.rgb = COLOR_TEXT
    normal_style.paragraph_format.line_spacing = 1.15
    normal_style.paragraph_format.space_after = Pt(4)

    # Page setup - Margins (Standard 0.8 top/bottom, 1.0 left/right)
    sec1 = doc.sections[0]
    sec1.top_margin = Inches(0.8)
    sec1.bottom_margin = Inches(0.8)
    sec1.left_margin = Inches(1.0)
    sec1.right_margin = Inches(1.0)
    sec1.page_width = Inches(8.5)
    sec1.page_height = Inches(11.0)
    add_double_page_border(sec1)

    # ==========================================
    # PAGE 1: COVER PAGE
    # ==========================================
    p_inst = doc.add_paragraph()
    p_inst.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_inst = p_inst.add_run("D. Y. PATIL COLLEGE OF ENGINEERING AND TECHNOLOGY, KOLHAPUR\n")
    set_font_times(r_inst, size_pt=13, bold=True, color=RGBColor(15, 23, 42))

    r_auto = p_inst.add_run("(An Autonomous Institute)\n")
    set_font_times(r_auto, size_pt=10, bold=True, color=COLOR_SECONDARY)

    r_dept = p_inst.add_run("DEPARTMENT OF COMPUTER SCIENCE AND ENGINEERING")
    set_font_times(r_dept, size_pt=11, bold=True, color=COLOR_TEXT)
    p_inst.paragraph_format.space_after = Pt(6)

    # College Logo
    logo_path = BASE_DIR / "college_logo.jpg"
    if logo_path.exists():
        p_logo = doc.add_paragraph()
        p_logo.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_logo.paragraph_format.space_after = Pt(6)
        r_pic = p_logo.add_run()
        r_pic.add_picture(str(logo_path), width=Inches(1.2))

    p_report_title = doc.add_paragraph()
    p_report_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_rep = p_report_title.add_run("A MINI-PROJECT REPORT ON\n")
    set_font_times(r_rep, size_pt=11, bold=True, color=RGBColor(100, 116, 139))

    r_course = p_report_title.add_run("CLOUD COMPUTING\n")
    set_font_times(r_course, size_pt=12, bold=True, color=COLOR_TEXT)

    r_proj = p_report_title.add_run("CLOUD FILE DEDUPLICATION AND\nSTORAGE OPTIMIZER")
    set_font_times(r_proj, size_pt=15, bold=True, color=COLOR_PRIMARY)
    p_report_title.paragraph_format.space_after = Pt(6)

    p_sub_hdr = doc.add_paragraph()
    p_sub_hdr.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_sh = p_sub_hdr.add_run("Submitted by")
    set_font_times(r_sh, size_pt=11, bold=True)
    p_sub_hdr.paragraph_format.space_after = Pt(4)

    # Students Table
    students = [
        ("144", "Sarthak Sanjay Salokhe"),
        ("149", "Vyanktesh Harishchandra Madhyapgol"),
        ("151", "Manjunath Rajkumar Gavandi"),
        ("152", "Balaji Ramraje Gaikwad"),
        ("155", "Prasanna Pradeep Bhurke")
    ]
    t_students = doc.add_table(rows=6, cols=3)
    t_students.alignment = WD_TABLE_ALIGNMENT.CENTER
    t_students.autofit = False
    col_w = [Inches(0.8), Inches(1.3), Inches(4.2)]
    for r in t_students.rows:
        for i, w in enumerate(col_w):
            r.cells[i].width = w

    headers = ["Sr.", "Roll No.", "Student Name"]
    for i, h in enumerate(headers):
        cell = t_students.cell(0, i)
        set_cell_background(cell, "F1F5F9")
        set_cell_margins(cell, top=50, bottom=50, left=80, right=80)
        set_cell_borders(cell)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER if i < 2 else WD_ALIGN_PARAGRAPH.LEFT
        run = p.add_run(h)
        set_font_times(run, size_pt=9.5, bold=True)

    for idx, (roll, sname) in enumerate(students, 1):
        row = t_students.rows[idx]
        vals = [str(idx), roll, sname]
        for col_idx, val in enumerate(vals):
            cell = row.cells[col_idx]
            set_cell_margins(cell, top=40, bottom=40, left=80, right=80)
            set_cell_borders(cell, top="E2E8F0", bottom="E2E8F0", left="E2E8F0", right="E2E8F0")
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if col_idx < 2 else WD_ALIGN_PARAGRAPH.LEFT
            r = p.add_run(val)
            set_font_times(r, size_pt=9.5)

    doc.add_paragraph().paragraph_format.space_after = Pt(4)

    # Class / Division
    p_div = doc.add_paragraph()
    p_div.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_div = p_div.add_run("T.Y(CSE) Div : C")
    set_font_times(r_div, size_pt=10.5, bold=True)
    p_div.paragraph_format.space_after = Pt(4)

    # Guidance block
    p_guidance = doc.add_paragraph()
    p_guidance.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_guidance.paragraph_format.space_after = Pt(2)
    r_ug = p_guidance.add_run("Under the guidance of\n")
    set_font_times(r_ug, size_pt=10)
    r_gn = p_guidance.add_run("Mrs. Aditee A Salokhe\n")
    set_font_times(r_gn, size_pt=11.5, bold=True)
    r_dp = p_guidance.add_run("Department of Computer Science and Engineering")
    set_font_times(r_dp, size_pt=10.5, bold=True)

    # Academic Year
    p_ay = doc.add_paragraph()
    p_ay.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_ay.paragraph_format.space_before = Pt(6)
    r_ay = p_ay.add_run("Academic Year: 2026-27")
    set_font_times(r_ay, size_pt=10.5, bold=True)

    doc.add_page_break()

    # ==========================================
    # PAGE 2: CERTIFICATE PAGE
    # ==========================================
    p_cert_head = doc.add_paragraph()
    p_cert_head.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r1 = p_cert_head.add_run("D. Y. PATIL COLLEGE OF ENGINEERING AND TECHNOLOGY, KOLHAPUR\n")
    set_font_times(r1, size_pt=13, bold=True)
    r2 = p_cert_head.add_run("Department of Computer Science and Engineering\n")
    set_font_times(r2, size_pt=11, bold=True)
    p_cert_head.paragraph_format.space_after = Pt(6)

    if logo_path.exists():
        p_logo2 = doc.add_paragraph()
        p_logo2.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_logo2.paragraph_format.space_after = Pt(6)
        r_pic2 = p_logo2.add_run()
        r_pic2.add_picture(str(logo_path), width=Inches(1.1))

    p_cert_title = doc.add_paragraph()
    p_cert_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_cert = p_cert_title.add_run("CERTIFICATE")
    set_font_times(r_cert, size_pt=15, bold=True, color=RGBColor(15, 23, 42))
    p_cert_title.paragraph_format.space_after = Pt(6)

    p_cert_body = doc.add_paragraph()
    p_cert_body.paragraph_format.line_spacing = 1.15
    p_cert_body.paragraph_format.space_after = Pt(6)
    r_cb1 = p_cert_body.add_run("This is to certify that the mini-project work entitled ")
    set_font_times(r_cb1, size_pt=10.5)
    r_pname = p_cert_body.add_run('"CLOUD FILE DEDUPLICATION AND STORAGE OPTIMIZER"')
    set_font_times(r_pname, size_pt=10.5, bold=True)
    r_cb2 = p_cert_body.add_run(" has been successfully carried out by the following students of the Department of Computer Science and Engineering, D. Y. Patil College of Engineering and Technology, Kolhapur, during the academic year ")
    set_font_times(r_cb2, size_pt=10.5)
    r_cb3 = p_cert_body.add_run("2026 – 2027:\n")
    set_font_times(r_cb3, size_pt=10.5, bold=True)

    # Student Table on Certificate
    cert_table = doc.add_table(rows=6, cols=3)
    cert_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    cert_table.autofit = False
    for row in cert_table.rows:
        for i, w in enumerate(col_w):
            row.cells[i].width = w

    for i, h in enumerate(headers):
        cell = cert_table.cell(0, i)
        set_cell_background(cell, "F1F5F9")
        set_cell_margins(cell, top=50, bottom=50, left=80, right=80)
        set_cell_borders(cell)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER if i < 2 else WD_ALIGN_PARAGRAPH.LEFT
        run = p.add_run(h)
        set_font_times(run, size_pt=9.5, bold=True)

    for idx, (roll, sname) in enumerate(students, 1):
        row = cert_table.rows[idx]
        vals = [str(idx), roll, sname]
        for col_idx, val in enumerate(vals):
            cell = row.cells[col_idx]
            set_cell_margins(cell, top=35, bottom=35, left=80, right=80)
            set_cell_borders(cell, top="E2E8F0", bottom="E2E8F0", left="E2E8F0", right="E2E8F0")
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if col_idx < 2 else WD_ALIGN_PARAGRAPH.LEFT
            r = p.add_run(val)
            set_font_times(r, size_pt=9.5)

    doc.add_paragraph().paragraph_format.space_after = Pt(4)

    p_fulfil = doc.add_paragraph()
    p_fulfil.paragraph_format.line_spacing = 1.15
    p_fulfil.paragraph_format.space_after = Pt(14)
    r_ful = p_fulfil.add_run(
        "The mini-project report is submitted in partial fulfilment of the requirements for the "
        "Cloud Computing course and has been reviewed and approved for internal assessment."
    )
    set_font_times(r_ful, size_pt=10.5)

    sig_table = doc.add_table(rows=2, cols=3)
    sig_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    sig_table.autofit = False
    col_w_sig = [Inches(2.15), Inches(2.15), Inches(2.2)]
    for row in sig_table.rows:
        for i, w in enumerate(col_w_sig):
            row.cells[i].width = w

    c_sig1 = sig_table.cell(0, 0)
    p_s1 = c_sig1.paragraphs[0]
    p_s1.alignment = WD_ALIGN_PARAGRAPH.LEFT
    r_l1 = p_s1.add_run("_________________________\n")
    set_font_times(r_l1, size_pt=9.5, bold=True)
    r_n1 = p_s1.add_run("Mrs. Aditee A. Salokhe\n")
    set_font_times(r_n1, size_pt=9.5, bold=True)
    r_d1 = p_s1.add_run("Course Coordinator / Guide\nDepartment of CSE")
    set_font_times(r_d1, size_pt=9.5)

    c_sig2 = sig_table.cell(0, 1)
    p_s2 = c_sig2.paragraphs[0]
    p_s2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_l2 = p_s2.add_run("_________________________\n")
    set_font_times(r_l2, size_pt=9.5, bold=True)
    r_n2 = p_s2.add_run("Dr. R. J. Dhanal\n")
    set_font_times(r_n2, size_pt=9.5, bold=True)
    r_d2 = p_s2.add_run("Head of the Department\nDepartment of CSE")
    set_font_times(r_d2, size_pt=9.5)

    c_sig3 = sig_table.cell(0, 2)
    p_s3 = c_sig3.paragraphs[0]
    p_s3.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    r_l3 = p_s3.add_run("_________________________\n")
    set_font_times(r_l3, size_pt=9.5, bold=True)
    r_n3 = p_s3.add_run("Dr. Sanjay S. Pawar\n")
    set_font_times(r_n3, size_pt=9.5, bold=True)
    r_d3 = p_s3.add_run("Principal\nD. Y. Patil College of Engineering\nand Technology, Kolhapur")
    set_font_times(r_d3, size_pt=9.5)

    c_meta = sig_table.cell(1, 0)
    p_sm = c_meta.paragraphs[0]
    p_sm.alignment = WD_ALIGN_PARAGRAPH.LEFT
    r_m = p_sm.add_run("\nDate: ____________________\nPlace: Kolhapur")
    set_font_times(r_m, size_pt=9.5)

    for row in sig_table.rows:
        for cell in row.cells:
            set_cell_borders(cell, top="FFFFFF", bottom="FFFFFF", left="FFFFFF", right="FFFFFF")

    doc.add_page_break()

    # ==========================================
    # PAGE 3: TABLE OF CONTENTS & LIST OF FIGURES
    # ==========================================
    p_toc_head = doc.add_paragraph()
    p_toc_head.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_toc = p_toc_head.add_run("TABLE OF CONTENTS")
    set_font_times(r_toc, size_pt=15, bold=True, color=RGBColor(15, 23, 42))
    p_toc_head.paragraph_format.space_after = Pt(8)

    toc_table = doc.add_table(rows=8, cols=3)
    toc_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    toc_table.columns[0].width = Inches(1.0)
    toc_table.columns[1].width = Inches(4.4)
    toc_table.columns[2].width = Inches(1.1)

    toc_headers = ["Chapter", "Topic / Title", "Page No."]
    for i, h in enumerate(toc_headers):
        cell = toc_table.cell(0, i)
        set_cell_background(cell, "E2E8F0")
        set_cell_margins(cell, top=50, bottom=50, left=80, right=80)
        set_cell_borders(cell)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER if i != 1 else WD_ALIGN_PARAGRAPH.LEFT
        r = p.add_run(h)
        set_font_times(r, size_pt=9.5, bold=True)

    toc_rows = [
        ("1", "Introduction & Background", "4"),
        ("2", "Problem Definition, Scope & Objectives", "5"),
        ("3", "Cloud-Based Design & System Architecture", "6"),
        ("4", "Implementation & User Interface", "7"),
        ("5", "Testing, Results & Experimental Evaluation", "8"),
        ("6", "Conclusion & Future Scope", "9"),
        ("7", "References & Technical Appendix", "10")
    ]

    for idx, (ch, name, page) in enumerate(toc_rows, 1):
        row = toc_table.rows[idx]
        for col_idx, val in enumerate([ch, name, page]):
            cell = row.cells[col_idx]
            set_cell_margins(cell, top=45, bottom=45, left=80, right=80)
            set_cell_borders(cell, top="E2E8F0", bottom="E2E8F0", left="E2E8F0", right="E2E8F0")
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if col_idx != 1 else WD_ALIGN_PARAGRAPH.LEFT
            r = p.add_run(val)
            set_font_times(r, size_pt=9.5, bold=(col_idx == 1))

    p_lof = doc.add_paragraph()
    p_lof.paragraph_format.space_before = Pt(14)
    p_lof.paragraph_format.space_after = Pt(4)
    r_lof = p_lof.add_run("LIST OF FIGURES AND TABLES")
    set_font_times(r_lof, size_pt=12, bold=True, color=RGBColor(15, 23, 42))

    lof_items = [
        ("Figure 3.1", "System Architecture & Deduplication Pipeline", "Page 6"),
        ("Table 3.1", "Relational Metadata Catalog Schema Specification (MySQL 8.0 & SQLite)", "Page 6"),
        ("Figure 4.1", "Live Web Dashboard with Real-Time Storage Analytics & Upload Area", "Page 7"),
        ("Figure 5.1", "Live Storage Optimization Overview & 100% Deduplication Metrics", "Page 8"),
        ("Table 5.1", "Experimental Deduplication Test Results & Storage Accounting", "Page 8")
    ]
    for tag, desc, pg in lof_items:
        p_item = doc.add_paragraph()
        p_item.paragraph_format.space_after = Pt(2)
        r_t = p_item.add_run(f"• {tag}: ")
        set_font_times(r_t, size_pt=10, bold=True)
        r_d = p_item.add_run(f"{desc} ")
        set_font_times(r_d, size_pt=10)
        r_p = p_item.add_run(f"({pg})")
        set_font_times(r_p, size_pt=10, color=RGBColor(100, 116, 139))

    doc.add_page_break()

    # Section 2 for Chapters 1-7 (Running Header/Footer)
    sec2 = doc.add_section()
    sec2.top_margin = Inches(0.8)
    sec2.bottom_margin = Inches(0.8)
    sec2.left_margin = Inches(1.0)
    sec2.right_margin = Inches(1.0)
    sec2.page_width = Inches(8.5)
    sec2.page_height = Inches(11.0)
    sec2.header.is_linked_to_previous = False
    sec2.footer.is_linked_to_previous = False
    add_double_page_border(sec2)

    header_p = sec2.header.paragraphs[0]
    header_p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    r_hdr = header_p.add_run("Cloud File Deduplication & Storage Optimizer | DYPCET CSE")
    set_font_times(r_hdr, size_pt=8.5, italic=True, color=RGBColor(148, 163, 184))

    footer_p = sec2.footer.paragraphs[0]
    footer_p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    r_ftr = footer_p.add_run("Page ")
    set_font_times(r_ftr, size_pt=9, color=RGBColor(100, 116, 139))
    add_page_number(footer_p.add_run())

    # ==========================================
    # PAGE 4: CHAPTER 1: INTRODUCTION
    # ==========================================
    p_ch1 = doc.add_paragraph()
    r_c1 = p_ch1.add_run("1. INTRODUCTION")
    set_font_times(r_c1, size_pt=14, bold=True, color=COLOR_PRIMARY)
    p_ch1.paragraph_format.space_after = Pt(4)

    p_1_1 = doc.add_paragraph()
    r_1_1_h = p_1_1.add_run("1.1 Background and Practical Need\n")
    set_font_times(r_1_1_h, size_pt=11, bold=True)
    r_1_1_b = p_1_1.add_run(
        "Today, multi-tenant cloud storage services like Google Drive, Dropbox, and Microsoft Azure are essential for universities and enterprises. "
        "In colleges, offices, and institutions, users routinely upload the exact same files under different names—such as identical syllabus copies, "
        "assignment PDFs, lecture materials, and software archives. In traditional cloud architectures, files are indexed strictly by bucket paths "
        "and user filenames. Each copy is stored as a completely new physical object on cloud disks, wasting massive amounts of storage space, "
        "wasting internet bandwidth, and rapidly exhausting cloud quotas."
    )
    set_font_times(r_1_1_b, size_pt=10.5)

    p_1_2 = doc.add_paragraph()
    r_1_2_h = p_1_2.add_run("1.2 What is Content-Addressable Storage (CAS)?\n")
    set_font_times(r_1_2_h, size_pt=11, bold=True)
    r_1_2_b = p_1_2.add_run(
        "Content-Addressable Storage (CAS) and data deduplication solve this challenge by addressing data by what it contains rather than where "
        "it is stored or what name it was given. Using cryptographic SHA-256 binary fingerprinting, files are uniquely identified. When an identical "
        "file is uploaded, the cloud does not save a second copy; instead, it increments a reference counter and creates a lightweight virtual pointer "
        "in MySQL. Users see their files listed normally, but physical cloud storage is consumed exactly once."
    )
    set_font_times(r_1_2_b, size_pt=10.5)

    p_1_3 = doc.add_paragraph()
    r_1_3_h = p_1_3.add_run("1.3 Whole-File vs. Chunk-Level Deduplication\n")
    set_font_times(r_1_3_h, size_pt=11, bold=True)
    r_1_3_b = p_1_3.add_run(
        "CloudDedup implements hybrid Content-Addressable Storage supporting both whole-file SHA-256 fingerprinting and 64 KB binary chunking. "
        "Whole-file hashing achieves instant O(1) detection for exact file duplicates, while 64 KB block chunking isolates modifications inside "
        "partially edited documents so that only changed blocks are written to physical storage. This saves 50% to 75% of cloud storage space."
    )
    set_font_times(r_1_3_b, size_pt=10.5)

    p_1_4 = doc.add_paragraph()
    r_1_4_h = p_1_4.add_run("1.4 Real-World Benefits\n")
    set_font_times(r_1_4_h, size_pt=11, bold=True)
    r_1_4_b = p_1_4.add_run(
        "By eliminating redundant physical storage, institutions achieve zero-write duplicate detection, drastically reduced cloud bills, "
        "instantaneous uploads for recurring documents, and complete user privacy isolation across personal file listings."
    )
    set_font_times(r_1_4_b, size_pt=10.5)

    doc.add_page_break()

    # ==========================================
    # PAGE 5: CHAPTER 2: PROBLEM DEFINITION & OBJECTIVES
    # ==========================================
    p_ch2 = doc.add_paragraph()
    r_c2 = p_ch2.add_run("2. PROBLEM DEFINITION & OBJECTIVES")
    set_font_times(r_c2, size_pt=14, bold=True, color=COLOR_PRIMARY)
    p_ch2.paragraph_format.space_after = Pt(4)

    p_2_1 = doc.add_paragraph()
    r_2_1_h = p_2_1.add_run("2.1 Problem Definition\n")
    set_font_times(r_2_1_h, size_pt=11, bold=True)
    r_2_1_b = p_2_1.add_run(
        "Standard cloud systems do not inspect binary content. If 50 students submit the same 20 MB textbook or project template, 1,000 MB (1 GB) "
        "is physically stored. Existing deduplication prototypes also suffer from common production drawbacks:\n"
        "• Severe server RAM exhaustion when reconstructing large files in memory during download.\n"
        "• Inability to track multi-user ownership and safe deletion without risking data corruption for other users.\n"
        "• Lack of production database integration and lack of live public access."
    )
    set_font_times(r_2_1_b, size_pt=10.5)

    p_2_2 = doc.add_paragraph()
    r_2_2_h = p_2_2.add_run("2.2 Project Objectives\n")
    set_font_times(r_2_2_h, size_pt=11, bold=True)
    r_2_2_b = p_2_2.add_run(
        "Our project builds an enterprise-grade cloud file deduplication and storage optimizer with the following concrete objectives:\n"
        "1. SHA-256 Cryptographic Fingerprinting: Generate 256-bit unique fingerprints to detect identical binary content with zero collision probability.\n"
        "2. Zero-Redundancy Cloud Storage: Write unique objects to cloud storage once (objects/<sha256_hash>) and skip duplicate network transmissions.\n"
        "3. Dual Relational Metadata Catalog: Maintain ACID-compliant catalog in MySQL 8.0 (with SQLite fallback) linking users, stored files, and file references.\n"
        "4. Safe Reference-Counted Deletion: Increment ref_count on duplicate upload; only delete physical cloud blocks when ref_count drops to zero.\n"
        "5. Low-RAM Streaming Download: Stream binary chunks using Python generators, keeping backend server memory below 1 MB regardless of file size.\n"
        "6. Live Cloud Deployment: Expose the complete frontend, backend, and MySQL database to the public Internet via Cloudflare Tunnel."
    )
    set_font_times(r_2_2_b, size_pt=10.5)

    p_2_3 = doc.add_paragraph()
    r_2_3_h = p_2_3.add_run("2.3 Mathematical Model of Storage Savings\n")
    set_font_times(r_2_3_h, size_pt=11, bold=True)
    r_2_3_b = p_2_3.add_run(
        "• Total Logical Storage (S_logical): Sum of sizes across all user-uploaded file references: S_logical = Sum(FileReference.file_size)\n"
        "• Total Physical Storage (S_physical): Actual space taken by unique objects on cloud storage: S_physical = Sum(StoredFile.file_size)\n"
        "• Total Space Saved (S_saved): S_saved = S_logical - S_physical\n"
        "• Deduplication Ratio (R_dedup): R_dedup = S_logical / S_physical  (e.g., 2.84 : 1 indicates virtual storage is 2.84x larger than physical disk)\n"
        "• Storage Reduction Percentage (P_reduction): P_reduction = (S_saved / S_logical) × 100%"
    )
    set_font_times(r_2_3_b, size_pt=10.5)

    doc.add_page_break()

    # ==========================================
    # PAGE 6: CHAPTER 3: CLOUD-BASED DESIGN & ARCHITECTURE
    # ==========================================
    p_ch3 = doc.add_paragraph()
    r_c3 = p_ch3.add_run("3. CLOUD-BASED DESIGN & ARCHITECTURE")
    set_font_times(r_c3, size_pt=14, bold=True, color=COLOR_PRIMARY)
    p_ch3.paragraph_format.space_after = Pt(4)

    p_3_1 = doc.add_paragraph()
    r_3_1_h = p_3_1.add_run("3.1 System Architecture Overview\n")
    set_font_times(r_3_1_h, size_pt=11, bold=True)
    r_3_1_b = p_3_1.add_run(
        "CloudDedup implements a decoupled, modern cloud computing architecture: a responsive Bootstrap 5.3 + Chart.js web frontend, "
        "a modular Python Flask REST API, Firebase Authentication with JWT verification, a normalized MySQL 8.0 relational metadata database, "
        "and Firebase Cloud Storage / GCP Bucket serving as the immutable Content-Addressable Storage layer."
    )
    set_font_times(r_3_1_b, size_pt=10.5)

    arch_img_path = BASE_DIR / "architecture_diagram.png"
    if arch_img_path.exists():
        p_diag = doc.add_paragraph()
        p_diag.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_diag.paragraph_format.space_before = Pt(2)
        p_diag.paragraph_format.space_after = Pt(2)
        r_apic = p_diag.add_run()
        r_apic.add_picture(str(arch_img_path), width=Inches(5.4))

        p_cap = doc.add_paragraph()
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap.paragraph_format.space_after = Pt(4)
        r_c = p_cap.add_run("Figure 3.1: System Architecture & Deduplication Pipeline")
        set_font_times(r_c, size_pt=8.5, bold=True, color=COLOR_SECONDARY)

    p_3_2 = doc.add_paragraph()
    r_3_2_h = p_3_2.add_run("3.2 Relational Database Schema Design (MySQL 8.0 & SQLite)\n")
    set_font_times(r_3_2_h, size_pt=11, bold=True)
    r_3_2_b = p_3_2.add_run(
        "The relational metadata catalog (clouddedup_db) models multi-user file ownership, CAS content addressing, and audit history:"
    )
    set_font_times(r_3_2_b, size_pt=10.5)

    schema_table = doc.add_table(rows=5, cols=3)
    schema_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    schema_table.columns[0].width = Inches(1.3)
    schema_table.columns[1].width = Inches(1.8)
    schema_table.columns[2].width = Inches(3.4)

    s_headers = ["Table Name", "Primary / Foreign Keys", "Columns & Purpose in Production System"]
    for i, h in enumerate(s_headers):
        cell = schema_table.cell(0, i)
        set_cell_background(cell, "F1F5F9")
        set_cell_margins(cell, top=45, bottom=45, left=70, right=70)
        set_cell_borders(cell)
        p = cell.paragraphs[0]
        r = p.add_run(h)
        set_font_times(r, size_pt=9, bold=True)

    s_data = [
        ("users", "id (PK AUTO_INCREMENT)\nfirebase_uid (UNIQUE)", "Stores user profiles, email addresses, Firebase authentication tokens, and registration timestamps."),
        ("stored_files", "id (PK AUTO_INCREMENT)\nsha256_hash (UNIQUE, Index)", "Unique physical objects stored once in cloud storage at objects/<hash>. Stores byte size and reference_count."),
        ("file_references", "id (PK AUTO_INCREMENT)\nFK: user_id -> users(id)\nFK: stored_file_id -> stored_files", "User-facing file catalogue. Maps user filenames to stored physical objects and sets the is_duplicate badge flag."),
        ("upload_events", "id (PK AUTO_INCREMENT)\nFK: user_id -> users(id)", "Audit trail logging every upload event (new_upload vs duplicate_detected), file size, and bandwidth saved.")
    ]
    for row_idx, (tname, keys, desc) in enumerate(s_data, 1):
        row = schema_table.rows[row_idx]
        for col_idx, val in enumerate([tname, keys, desc]):
            cell = row.cells[col_idx]
            set_cell_margins(cell, top=35, bottom=35, left=70, right=70)
            set_cell_borders(cell, top="E2E8F0", bottom="E2E8F0", left="E2E8F0", right="E2E8F0")
            p = cell.paragraphs[0]
            r = p.add_run(val)
            set_font_times(r, size_pt=8.5, bold=(col_idx == 0))

    p_tcap = doc.add_paragraph()
    p_tcap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_tcap.paragraph_format.space_before = Pt(2)
    r_tc = p_tcap.add_run("Table 3.1: Relational Metadata Catalog Schema Specification (MySQL 8.0 & SQLite)")
    set_font_times(r_tc, size_pt=8.5, bold=True, color=COLOR_SECONDARY)

    doc.add_page_break()

    # ==========================================
    # PAGE 7: CHAPTER 4: IMPLEMENTATION & USER INTERFACE
    # ==========================================
    p_ch4 = doc.add_paragraph()
    r_c4 = p_ch4.add_run("4. IMPLEMENTATION & USER INTERFACE")
    set_font_times(r_c4, size_pt=14, bold=True, color=COLOR_PRIMARY)
    p_ch4.paragraph_format.space_after = Pt(4)

    p_4_1 = doc.add_paragraph()
    r_4_1_h = p_4_1.add_run("4.1 How Upload and Deduplication Works\n")
    set_font_times(r_4_1_h, size_pt=11, bold=True)
    r_4_1_b = p_4_1.add_run(
        "When a user selects a file on the web dashboard and clicks upload, the system executes a high-speed deduplication pipeline:\n"
        "1. Binary Ingress & Fingerprinting: The file stream is processed in 64 KB binary chunks while hashlib.sha256 computes the deterministic hash.\n"
        "2. Catalog Lookup: The backend queries stored_files in MySQL. If the sha256_hash already exists, cloud upload is skipped (0 bytes uploaded!). "
        "Its reference_count increments by +1, and an is_duplicate=TRUE reference is recorded for the user.\n"
        "3. New Content Storage: If new, the binary is streamed to Firebase Cloud Storage at objects/<sha256_hash> and registered in stored_files."
    )
    set_font_times(r_4_1_b, size_pt=10.5)

    dash_top_path = BASE_DIR / "dashboard_top_cards.png"
    if not dash_top_path.exists():
        dash_top_path = BASE_DIR / "dashboard_screenshot.png"

    if dash_top_path.exists():
        p_sc1 = doc.add_paragraph()
        p_sc1.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_sc1.paragraph_format.space_before = Pt(2)
        p_sc1.paragraph_format.space_after = Pt(2)
        r_dpic = p_sc1.add_run()
        r_dpic.add_picture(str(dash_top_path), width=Inches(5.6))

        p_scap1 = doc.add_paragraph()
        p_scap1.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_scap1.paragraph_format.space_after = Pt(4)
        r_sc1 = p_scap1.add_run("Figure 4.1: Live Web Dashboard with Real-Time Storage Analytics & Upload Area")
        set_font_times(r_sc1, size_pt=8.5, bold=True, color=COLOR_SECONDARY)

    p_4_2 = doc.add_paragraph()
    r_4_2_h = p_4_2.add_run("4.2 Low-Memory File Streaming Download\n")
    set_font_times(r_4_2_h, size_pt=11, bold=True)
    r_4_2_b = p_4_2.add_run(
        "To prevent server crashes, the system streams files using Python generators (`yield`). It reads one 64 KB block at a time from cloud storage "
        "and pipes it directly to the user's browser, maintaining server RAM usage strictly below 1 MB regardless of whether a file is 10 MB or 500 MB."
    )
    set_font_times(r_4_2_b, size_pt=10.5)

    p_4_3 = doc.add_paragraph()
    r_4_3_h = p_4_3.add_run("4.3 Safe Deletion & Reference Counting\n")
    set_font_times(r_4_3_h, size_pt=11, bold=True)
    r_4_3_b = p_4_3.add_run(
        "When a user deletes a file, only their row in file_references is removed, and stored_files.reference_count is decremented by 1. "
        "Only when reference_count reaches 0 is the physical binary deleted from cloud storage, guaranteeing that shared files are never corrupted."
    )
    set_font_times(r_4_3_b, size_pt=10.5)

    doc.add_page_break()

    # ==========================================
    # PAGE 8: CHAPTER 5: TESTING & RESULTS
    # ==========================================
    p_ch5 = doc.add_paragraph()
    r_c5 = p_ch5.add_run("5. TESTING, RESULTS & EXPERIMENTAL EVALUATION")
    set_font_times(r_c5, size_pt=14, bold=True, color=COLOR_PRIMARY)
    p_ch5.paragraph_format.space_after = Pt(4)

    p_5_1 = doc.add_paragraph()
    r_5_1_h = p_5_1.add_run("5.1 Experimental Testing Setup\n")
    set_font_times(r_5_1_h, size_pt=11, bold=True)
    r_5_1_b = p_5_1.add_run(
        "We validated the deduplication platform across automated pytest unit suites and live empirical testing with real-world document workloads:"
    )
    set_font_times(r_5_1_b, size_pt=10.5)

    test_table = doc.add_table(rows=6, cols=6)
    test_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    test_table.columns[0].width = Inches(0.9)
    test_table.columns[1].width = Inches(1.8)
    test_table.columns[2].width = Inches(0.6)
    test_table.columns[3].width = Inches(0.6)
    test_table.columns[4].width = Inches(1.3)
    test_table.columns[5].width = Inches(1.3)

    t_headers = ["Test Case", "Workload Description", "Total", "Dedup", "Physical Written", "Space Saved"]
    for i, h in enumerate(t_headers):
        cell = test_table.cell(0, i)
        set_cell_background(cell, "F1F5F9")
        set_cell_margins(cell, top=40, bottom=40, left=50, right=50)
        set_cell_borders(cell)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(h)
        set_font_times(r, size_pt=8.5, bold=True)

    test_data = [
        ("Test 1", "Unique Document Ingestion", "5", "0", "1.76 MB", "0 B (0%)"),
        ("Test 2", "Exact Duplicate Submissions", "7", "7", "0 B (Zero-write)", "3.24 MB (100%)"),
        ("Test 3", "Multi-User Sharing", "9 Users", "Shared", "Shared Blocks", "Multi-Tenant Savings"),
        ("Test 4", "Pytest Suite (11 Tests)", "11 Passed", "100%", "Verified", "1.45s Runtime"),
        ("Overall", "Live Production Total", "12", "7", "1.76 MB", "3.24 MB (64.74%)")
    ]
    for row_idx, r_data in enumerate(test_data, 1):
        row = test_table.rows[row_idx]
        for col_idx, val in enumerate(r_data):
            cell = row.cells[col_idx]
            set_cell_margins(cell, top=35, bottom=35, left=50, right=50)
            set_cell_borders(cell, top="E2E8F0", bottom="E2E8F0", left="E2E8F0", right="E2E8F0")
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if col_idx != 1 else WD_ALIGN_PARAGRAPH.LEFT
            r = p.add_run(val)
            set_font_times(r, size_pt=8.5, bold=(row_idx == 5))

    p_ttitle = doc.add_paragraph()
    p_ttitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_ttitle.paragraph_format.space_before = Pt(2)
    p_ttitle.paragraph_format.space_after = Pt(2)
    r_tt = p_ttitle.add_run("Table 5.1: Experimental Deduplication Test Results & Storage Accounting")
    set_font_times(r_tt, size_pt=8.5, bold=True, color=COLOR_SECONDARY)

    stat_img_path = BASE_DIR / "dashboard_stats_overview.png"
    if not stat_img_path.exists():
        stat_img_path = BASE_DIR / "savings_chart.png"

    if stat_img_path.exists():
        p_sc2 = doc.add_paragraph()
        p_sc2.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_sc2.paragraph_format.space_before = Pt(2)
        p_sc2.paragraph_format.space_after = Pt(2)
        r_spic = p_sc2.add_run()
        r_spic.add_picture(str(stat_img_path), width=Inches(5.6))

        p_scap2 = doc.add_paragraph()
        p_scap2.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_scap2.paragraph_format.space_after = Pt(4)
        r_sc2 = p_scap2.add_run("Figure 5.1: Live Storage Optimization Overview & 100% Deduplication Metrics")
        set_font_times(r_sc2, size_pt=8.5, bold=True, color=COLOR_SECONDARY)

    p_5_2 = doc.add_paragraph()
    r_5_2_h = p_5_2.add_run("5.2 Summary of Findings\n")
    set_font_times(r_5_2_h, size_pt=11, bold=True)
    r_5_2_b = p_5_2.add_run(
        "• 100% Duplicate Detection: In Test 2, duplicate documents uploaded under different names were detected instantly with 0 physical bytes written.\n"
        "• Proven 64.74% Space Reduction: 5,009,947 bytes (4.8 MB) of user files were stored in just 1,766,586 bytes (1.7 MB), saving 3.1 MB with a 2.84 : 1 ratio.\n"
        "• Zero Data Corruption: Downloaded files verified byte-by-byte with SHA-256 matched the originals with 100% cryptographic accuracy.\n"
        "• Live Public Accessibility: The system is deployed via Cloudflare Tunnel (https://advocate-vision-agencies-valuable.trycloudflare.com)."
    )
    set_font_times(r_5_2_b, size_pt=10.5)

    doc.add_page_break()

    # ==========================================
    # PAGE 9: CHAPTER 6: CONCLUSION & FUTURE SCOPE
    # ==========================================
    p_ch6 = doc.add_paragraph()
    r_c6 = p_ch6.add_run("6. CONCLUSION & FUTURE SCOPE")
    set_font_times(r_c6, size_pt=14, bold=True, color=COLOR_PRIMARY)
    p_ch6.paragraph_format.space_after = Pt(6)

    p_6_1 = doc.add_paragraph()
    r_6_1_h = p_6_1.add_run("6.1 Conclusion\n")
    set_font_times(r_6_1_h, size_pt=11, bold=True)
    r_6_1_b = p_6_1.add_run(
        "The Cloud File Deduplication and Storage Optimizer project successfully proves that Content-Addressable Storage (CAS) and cryptographic "
        "SHA-256 fingerprinting can dramatically lower cloud storage costs. By decoupling logical user file references from underlying immutable "
        "cloud objects, our system avoids duplicate writes on identical files and achieves substantial cloud storage savings.\n\n"
        "Main achievements of the project:\n"
        "• Zero physical writes on duplicate uploads (0 bytes written to cloud object storage).\n"
        "• Proven storage savings of 64.74% and a 2.84 : 1 deduplication compression ratio in testing.\n"
        "• Full production database integration with MySQL 8.0 server and SQLite fallback.\n"
        "• Safe reference counting so deleting a file never damages shared blocks belonging to other users.\n"
        "• Memory-efficient streaming downloads that keep server RAM usage under 1 MB.\n"
        "• Live public cloud access through Cloudflare Tunnel with full HTTPS transport security."
    )
    set_font_times(r_6_1_b, size_pt=10.5)

    p_6_2 = doc.add_paragraph()
    r_6_2_h = p_6_2.add_run("6.2 Future Improvements\n")
    set_font_times(r_6_2_h, size_pt=11, bold=True)
    r_6_2_b = p_6_2.add_run(
        "1. Variable-Size Chunking (FastCDC): Using dynamic chunk boundaries instead of fixed 64 KB blocks to handle cases where adding text "
        "at the beginning of a document shifts the remaining blocks.\n\n"
        "2. Client-Side Deduplication: Computing SHA-256 hashes directly in the user's web browser before upload. If the server already has the block, "
        "the upload is skipped, saving user internet bandwidth and upload time.\n\n"
        "3. Convergent Encryption: Using content-derived encryption keys so that files can be deduplicated securely on public clouds while remaining "
        "fully encrypted and private for users.\n\n"
        "4. Cloud Storage Tiering: Automatically moving cold, rarely-used chunks to low-cost archival storage like AWS S3 Glacier to save further costs."
    )
    set_font_times(r_6_2_b, size_pt=10.5)

    doc.add_page_break()

    # ==========================================
    # PAGE 10: CHAPTER 7: REFERENCES & APPENDIX
    # ==========================================
    p_ch7 = doc.add_paragraph()
    r_c7 = p_ch7.add_run("7. REFERENCES & TECHNICAL APPENDIX")
    set_font_times(r_c7, size_pt=14, bold=True, color=COLOR_PRIMARY)
    p_ch7.paragraph_format.space_after = Pt(6)

    p_7_1 = doc.add_paragraph()
    r_7_1_h = p_7_1.add_run("7.1 References\n")
    set_font_times(r_7_1_h, size_pt=11, bold=True)

    refs = [
        "[1] D. T. Meyer and W. J. Bolosky, \"A Study of Practical Deduplication,\" ACM Transactions on Storage (TOS), vol. 7, no. 4, pp. 1-20, 2012.",
        "[2] P. Nath, M. A. Kozuch, D. R. O'Hallaron, J. Harkes, M. Satyanarayanan, N. Tolia, and M. Kaminsky, \"Design Tradeoffs in Applying Content Addressable Storage to Enterprise-Scale Systems,\" in Proc. USENIX FAST, 2008.",
        "[3] M. Lillibridge, K. Eshghi, D. Bhagwat, V. Deolalikar, G. Trezise, and P. Camble, \"Sparse Indexing: Large Scale, Inline Deduplication Using Sampling and Locality,\" in Proc. 7th USENIX FAST, 2009.",
        "[4] J. R. Douceur, A. Adya, W. J. Bolosky, D. Simon, and M. Theimer, \"Reclaiming Space from Duplicate Files in a Serverless Distributed File System,\" in Proc. 22nd ICDCS, 2002.",
        "[5] National Institute of Standards and Technology (NIST), \"Secure Hash Standard (SHS),\" FIPS PUB 180-4, Aug. 2015.",
        "[6] A. Tridgell and P. Mackerras, \"The rsync algorithm,\" Technical Report TR-CS-96-05, Australian National University, 1996."
    ]
    for r in refs:
        p_ref = doc.add_paragraph()
        p_ref.paragraph_format.line_spacing = 1.15
        p_ref.paragraph_format.space_after = Pt(3)
        r_run = p_ref.add_run(r)
        set_font_times(r_run, size_pt=10)

    p_7_2 = doc.add_paragraph()
    p_7_2.paragraph_format.space_before = Pt(6)
    r_7_2_h = p_7_2.add_run("7.2 Appendix: Core Relational Database Schema (MySQL 8.0 / SQLite)\n")
    set_font_times(r_7_2_h, size_pt=11, bold=True)

    ddl_code = (
        "-- Table 1: Unique Physical Cloud Objects (CAS)\n"
        "CREATE TABLE stored_files (\n"
        "    id INT AUTO_INCREMENT PRIMARY KEY,\n"
        "    sha256_hash VARCHAR(64) NOT NULL UNIQUE,\n"
        "    file_size BIGINT NOT NULL,\n"
        "    storage_path VARCHAR(512) NOT NULL, -- objects/<sha256_hash>\n"
        "    reference_count INT NOT NULL DEFAULT 1\n"
        ");\n\n"
        "-- Table 2: User File References (Decoupled Catalog)\n"
        "CREATE TABLE file_references (\n"
        "    id INT AUTO_INCREMENT PRIMARY KEY,\n"
        "    user_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,\n"
        "    stored_file_id INT NOT NULL REFERENCES stored_files(id),\n"
        "    display_name VARCHAR(255) NOT NULL, is_duplicate BOOLEAN NOT NULL DEFAULT FALSE\n"
        ");"
    )
    p_code = doc.add_paragraph()
    p_code.paragraph_format.space_after = Pt(2)
    r_code = p_code.add_run(ddl_code)
    r_code.font.name = 'Courier New'
    r_code.font.size = Pt(8.5)
    r_code.font.color.rgb = COLOR_TEXT

    doc.save(OUTPUT_DOCX)
    try:
        doc.save(DOWNLOADS_DOCX)
    except Exception as e:
        print(f"Warning saving to downloads: {e}")

    print(f"[OK] Generated report: {OUTPUT_DOCX}")
    return OUTPUT_DOCX

if __name__ == "__main__":
    generate_report()
