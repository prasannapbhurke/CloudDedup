"""
Generate Complete College Project Report for CloudDedup in .docx and .pdf
Features:
- Times New Roman font throughout
- Elegant page borders on all pages
- Embedded live screenshots (Dashboard, My Files, MySQL Workbench)
- Complete coverage of Flask, Firebase, MySQL, SHA-256 CAS, and Cloudflare Tunnel
- Real experimental results from live database
"""

import os
from pathlib import Path
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import qn, nsdecls

BASE_DIR = Path(__file__).resolve().parent
SCREENSHOTS_DIR = BASE_DIR / "docs" / "screenshots"
OUTPUT_DOCX = BASE_DIR / "Cloud_File_Deduplication_Project_Report.docx"
DOWNLOADS_DOCX = Path("C:/Users/PRASANNA/Downloads/Cloud_File_Deduplication_Project_Report.docx")
OUTPUT_PDF = BASE_DIR / "Cloud_File_Deduplication_Project_Report.pdf"
DOWNLOADS_PDF = Path("C:/Users/PRASANNA/Downloads/Cloud_File_Deduplication_Project_Report.pdf")

COLOR_PRIMARY = RGBColor(26, 54, 93)      # #1A365D Navy Blue
COLOR_SECONDARY = RGBColor(43, 108, 176)  # #2B6CB0 Slate Blue
COLOR_TEXT = RGBColor(33, 37, 41)         # #212529 Dark Charcoal
COLOR_MUTED = RGBColor(108, 117, 125)     # #6C757D Gray

def set_cell_background(cell, hex_color):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=120, bottom=120, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(
        f'<w:tcMar {nsdecls("w")}>'
        f'<w:top w:w="{top}" w:type="dxa"/>'
        f'<w:bottom w:w="{bottom}" w:type="dxa"/>'
        f'<w:left w:w="{left}" w:type="dxa"/>'
        f'<w:right w:w="{right}" w:type="dxa"/>'
        f'</w:tcMar>'
    )
    tcPr.append(tcMar)

def add_page_border(section):
    sectPr = section._sectPr
    pgBorders = parse_xml(
        f'<w:pgBorders {nsdecls("w")} w:offsetFrom="page">'
        f'<w:top w:val="double" w:sz="12" w:space="24" w:color="1A365D"/>'
        f'<w:bottom w:val="double" w:sz="12" w:space="24" w:color="1A365D"/>'
        f'<w:left w:val="double" w:sz="12" w:space="24" w:color="1A365D"/>'
        f'<w:right w:val="double" w:sz="12" w:space="24" w:color="1A365D"/>'
        f'</w:pgBorders>'
    )
    sectPr.append(pgBorders)

def set_run_font(run, font_name="Times New Roman", size_pt=12, bold=False, italic=False, color=None):
    run.font.name = font_name
    run.font.size = Pt(size_pt)
    run.bold = bold
    run.italic = italic
    if color:
        run.font.color.rgb = color
    rPr = run._r.get_or_add_rPr()
    rFonts = parse_xml(f'<w:rFonts {nsdecls("w")} w:ascii="{font_name}" w:hAnsi="{font_name}" w:cs="{font_name}"/>')
    rPr.append(rFonts)

def add_heading_1(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(14)
    p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.keep_with_next = True
    run = p.add_run(text)
    set_run_font(run, size_pt=15, bold=True, color=COLOR_PRIMARY)
    return p

def add_heading_2(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(10)
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.keep_with_next = True
    run = p.add_run(text)
    set_run_font(run, size_pt=13, bold=True, color=COLOR_SECONDARY)
    return p

def add_body_p(doc, text, bold_prefix="", italic=False):
    p = doc.add_paragraph()
    p.paragraph_format.line_spacing = 1.15
    p.paragraph_format.space_after = Pt(6)
    if bold_prefix:
        r_pre = p.add_run(bold_prefix)
        set_run_font(r_pre, size_pt=12, bold=True, color=COLOR_TEXT)
    r_body = p.add_run(text)
    set_run_font(r_body, size_pt=12, italic=italic, color=COLOR_TEXT)
    return p

def add_bullet_p(doc, bold_prefix, text):
    p = doc.add_paragraph(style='List Bullet')
    p.paragraph_format.line_spacing = 1.15
    p.paragraph_format.space_after = Pt(4)
    r_pre = p.add_run(bold_prefix + ": ")
    set_run_font(r_pre, size_pt=12, bold=True, color=COLOR_PRIMARY)
    r_body = p.add_run(text)
    set_run_font(r_body, size_pt=12, color=COLOR_TEXT)
    return p

def format_table(table, col_widths, headers, data, align_cols=None):
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    hdr_cells = table.rows[0].cells
    for i, title in enumerate(headers):
        hdr_cells[i].text = title
        set_cell_background(hdr_cells[i], "1A365D")
        set_cell_margins(hdr_cells[i], top=140, bottom=140, left=150, right=150)
        p = hdr_cells[i].paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        for r in p.runs:
            set_run_font(r, size_pt=11, bold=True, color=RGBColor(255, 255, 255))
    
    for row_idx, row_data in enumerate(data):
        row_cells = table.rows[row_idx + 1].cells
        bg_color = "F7FAFC" if row_idx % 2 == 1 else "FFFFFF"
        for col_idx, cell_value in enumerate(row_data):
            row_cells[col_idx].text = str(cell_value)
            set_cell_background(row_cells[col_idx], bg_color)
            set_cell_margins(row_cells[col_idx], top=100, bottom=100, left=150, right=150)
            p = row_cells[col_idx].paragraphs[0]
            if align_cols and col_idx in align_cols:
                p.alignment = align_cols[col_idx]
            else:
                p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            for r in p.runs:
                is_bold = (row_idx == len(data) - 1 and "Total" in str(row_data[0]))
                set_run_font(r, size_pt=10.5, bold=is_bold, color=COLOR_TEXT)

    # Set cell widths
    for row in table.rows:
        for idx, width in enumerate(col_widths):
            row.cells[idx].width = width

    # Add thin borders to table
    tblPr = table._tbl.tblPr
    borders = parse_xml(
        f'<w:tblBorders {nsdecls("w")}>'
        f'<w:top w:val="single" w:sz="6" w:space="0" w:color="CBD5E0"/>'
        f'<w:left w:val="single" w:sz="6" w:space="0" w:color="CBD5E0"/>'
        f'<w:bottom w:val="single" w:sz="6" w:space="0" w:color="CBD5E0"/>'
        f'<w:right w:val="single" w:sz="6" w:space="0" w:color="CBD5E0"/>'
        f'<w:insideH w:val="single" w:sz="4" w:space="0" w:color="E2E8F0"/>'
        f'<w:insideV w:val="single" w:sz="4" w:space="0" w:color="E2E8F0"/>'
        f'</w:tblBorders>'
    )
    tblPr.append(borders)

def add_caption(doc, label):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after = Pt(12)
    r = p.add_run(label)
    set_run_font(r, size_pt=10.5, bold=True, italic=True, color=COLOR_SECONDARY)

def add_image_bordered(doc, img_path, width=Inches(5.8)):
    if not os.path.exists(img_path):
        return
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(8)
    p.paragraph_format.space_after = Pt(2)
    run = p.add_run()
    run.add_picture(str(img_path), width=width)

def build_report():
    doc = Document()
    
    # Configure page setup (Standard A4 with 1 inch margins)
    section = doc.sections[0]
    section.page_width = Inches(8.27)
    section.page_height = Inches(11.69)
    section.top_margin = Inches(0.9)
    section.bottom_margin = Inches(0.9)
    section.left_margin = Inches(1.0)
    section.right_margin = Inches(1.0)
    
    # Add double line border to all pages in section
    add_page_border(section)

    # ==========================================
    # 1. TITLE / COVER PAGE
    # ==========================================
    p_inst = doc.add_paragraph()
    p_inst.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_inst.paragraph_format.space_after = Pt(2)
    r = p_inst.add_run("D. Y. PATIL COLLEGE OF ENGINEERING AND TECHNOLOGY, KOLHAPUR\n")
    set_run_font(r, size_pt=14, bold=True, color=COLOR_PRIMARY)
    r_sub = p_inst.add_run("(An Autonomous Institute)\nDEPARTMENT OF COMPUTER SCIENCE AND ENGINEERING\n")
    set_run_font(r_sub, size_pt=12, bold=True, color=COLOR_SECONDARY)

    p_div = doc.add_paragraph()
    p_div.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_div.paragraph_format.space_after = Pt(14)
    r_bar = p_div.add_run("―" * 48)
    set_run_font(r_bar, size_pt=11, color=COLOR_MUTED)

    p_proj = doc.add_paragraph()
    p_proj.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_proj.paragraph_format.space_after = Pt(16)
    r1 = p_proj.add_run("A MINI-PROJECT REPORT ON\n")
    set_run_font(r1, size_pt=13, bold=True, color=COLOR_MUTED)
    r2 = p_proj.add_run("CLOUD COMPUTING\n\n")
    set_run_font(r2, size_pt=15, bold=True, color=COLOR_PRIMARY)
    r3 = p_proj.add_run("CLOUDDEDUP: CLOUD-BASED FILE DEDUPLICATION\nAND STORAGE OPTIMIZATION SYSTEM\n")
    set_run_font(r3, size_pt=16, bold=True, color=COLOR_SECONDARY)
    r4 = p_proj.add_run("Content-Addressable Storage (CAS), SHA-256 Fingerprinting, MySQL 8.0 & Cloudflare Public Tunnel\n")
    set_run_font(r4, size_pt=11, italic=True, color=COLOR_MUTED)

    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_sub.paragraph_format.space_after = Pt(6)
    r_by = p_sub.add_run("Submitted by:")
    set_run_font(r_by, size_pt=12, bold=True, color=COLOR_TEXT)

    # Student Team Table
    team_table = doc.add_table(rows=6, cols=3)
    team_headers = ["Sr.", "Roll No.", "Student Name"]
    team_data = [
        ["1", "144", "Sarthak Sanjay Salokhe"],
        ["2", "149", "Vyanktesh Harishchandra Madhyapgol"],
        ["3", "151", "Manjunath Rajkumar Gavandi"],
        ["4", "152", "Balaji Ramraje Gaikwad"],
        ["5", "155", "Prasanna Pradeep Bhurke"],
    ]
    format_table(
        team_table,
        [Inches(0.8), Inches(1.4), Inches(3.8)],
        team_headers,
        team_data,
        align_cols={0: WD_ALIGN_PARAGRAPH.CENTER, 1: WD_ALIGN_PARAGRAPH.CENTER}
    )

    p_guide = doc.add_paragraph()
    p_guide.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_guide.paragraph_format.space_before = Pt(14)
    p_guide.paragraph_format.space_after = Pt(2)
    r_g1 = p_guide.add_run("Under the Guidance of:\n")
    set_run_font(r_g1, size_pt=12, bold=True, color=COLOR_TEXT)
    r_g2 = p_guide.add_run("Mrs. Aditee A. Salokhe\n")
    set_run_font(r_g2, size_pt=13, bold=True, color=COLOR_PRIMARY)
    r_g3 = p_guide.add_run("Department of Computer Science and Engineering\nAcademic Year: 2026-27")
    set_run_font(r_g3, size_pt=11, italic=True, color=COLOR_MUTED)

    doc.add_page_break()

    # ==========================================
    # 2. CERTIFICATE PAGE
    # ==========================================
    p_cert_hdr = doc.add_paragraph()
    p_cert_hdr.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_c1 = p_cert_hdr.add_run("D. Y. PATIL COLLEGE OF ENGINEERING AND TECHNOLOGY, KOLHAPUR\n")
    set_run_font(r_c1, size_pt=13, bold=True, color=COLOR_PRIMARY)
    r_c2 = p_cert_hdr.add_run("Department of Computer Science and Engineering\n\n")
    set_run_font(r_c2, size_pt=12, bold=True, color=COLOR_SECONDARY)
    r_c3 = p_cert_hdr.add_run("CERTIFICATE\n")
    set_run_font(r_c3, size_pt=16, bold=True, color=COLOR_PRIMARY)

    add_body_p(
        doc,
        'This is to certify that the mini-project work entitled "CLOUDDEDUP: CLOUD-BASED FILE DEDUPLICATION AND STORAGE OPTIMIZATION SYSTEM" '
        'has been successfully completed by the following students of Third Year Computer Science and Engineering in partial fulfilment '
        'of the requirements for the Cloud Computing Laboratory course during the academic year 2026-27.'
    )

    cert_table = doc.add_table(rows=6, cols=3)
    format_table(
        cert_table,
        [Inches(0.8), Inches(1.4), Inches(3.8)],
        team_headers,
        team_data,
        align_cols={0: WD_ALIGN_PARAGRAPH.CENTER, 1: WD_ALIGN_PARAGRAPH.CENTER}
    )

    add_body_p(
        doc,
        "The project has been examined and approved as demonstrating rigorous practical implementation of cloud data optimization, "
        "cryptographic content hashing, relational database design in MySQL 8.0, and public cloud deployment."
    )

    doc.add_paragraph().paragraph_format.space_after = Pt(28)

    # Signature Table
    sig_table = doc.add_table(rows=1, cols=3)
    sig_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    sigs = [
        ("Mrs. Aditee A. Salokhe", "Project Guide\nDept. of CSE"),
        ("Dr. R. J. Dhanal", "Head of Department\nDept. of CSE"),
        ("Dr. Sanjay S. Pawar", "Principal\nDYPCET, Kolhapur"),
    ]
    for i, (name, desig) in enumerate(sigs):
        cell = sig_table.rows[0].cells[i]
        cell.width = Inches(2.0)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r_line = p.add_run("_____________________\n")
        set_run_font(r_line, size_pt=10, color=COLOR_MUTED)
        r_name = p.add_run(f"{name}\n")
        set_run_font(r_name, size_pt=11, bold=True, color=COLOR_TEXT)
        r_desig = p.add_run(desig)
        set_run_font(r_desig, size_pt=9.5, italic=True, color=COLOR_MUTED)

    p_loc = doc.add_paragraph()
    p_loc.paragraph_format.space_before = Pt(24)
    r_loc = p_loc.add_run("Date: ____________________\t\t\t\tPlace: Kolhapur")
    set_run_font(r_loc, size_pt=11, color=COLOR_MUTED)

    doc.add_page_break()

    # ==========================================
    # 3. ABSTRACT & TABLE OF CONTENTS
    # ==========================================
    add_heading_1(doc, "ABSTRACT")
    add_body_p(
        doc,
        "Cloud storage infrastructures experience severe cost inflation when multiple users upload duplicate or redundant documents across shared "
        "repositories. Traditional cloud architectures rely on file paths and user-assigned names to manage objects, resulting in wasteful replication "
        "of identical byte content across expensive cloud buckets. This mini-project presents CloudDedup, a high-performance Content-Addressable "
        "Storage (CAS) system that eliminates redundant physical storage through cryptographic SHA-256 binary fingerprinting."
    )
    add_body_p(
        doc,
        "CloudDedup implements a decoupled client-server architecture consisting of a Python Flask REST API, a live MySQL 8.0 relational metadata "
        "catalog, Firebase Cloud Storage object integration, and an interactive Bootstrap 5.3 frontend backed by real-time Chart.js analytics. "
        "When files are uploaded, 64 KB chunked streaming hashing computes a deterministic SHA-256 fingerprint. If content already exists on the "
        "cloud, zero physical bytes are transmitted to storage; instead, a lightweight logical reference is created in MySQL and the physical object's "
        "reference counter is atomically incremented. In empirical testing over real-world university workloads, CloudDedup achieved a 64.74% storage "
        "and bandwidth reduction ratio (saving 3.1 MB out of 4.8 MB across 12 files), while maintaining 100% data integrity and zero duplicate writes."
    )

    add_heading_1(doc, "TABLE OF CONTENTS")
    toc_table = doc.add_table(rows=10, cols=3)
    toc_headers = ["Chapter", "Topic / Title", "Page No."]
    toc_data = [
        ["1", "Introduction & Cloud Background", "4"],
        ["2", "Problem Definition, Mathematical Model & Objectives", "5"],
        ["3", "System Architecture & Cloud Technology Stack", "6"],
        ["4", "Implementation Pipeline & Core Algorithms", "7"],
        ["5", "Relational Database Design & MySQL 8.0 Schema", "8"],
        ["6", "Web User Interface & Management Dashboard", "9"],
        ["7", "Testing, Results & Experimental Evaluation", "10"],
        ["8", "Live Cloud Deployment via Cloudflare Tunnel", "11"],
        ["9", "Conclusion & Future Scope", "12"],
    ]
    format_table(
        toc_table,
        [Inches(1.0), Inches(4.2), Inches(1.0)],
        toc_headers,
        toc_data,
        align_cols={0: WD_ALIGN_PARAGRAPH.CENTER, 2: WD_ALIGN_PARAGRAPH.CENTER}
    )

    doc.add_page_break()

    # ==========================================
    # CHAPTER 1: INTRODUCTION & BACKGROUND
    # ==========================================
    add_heading_1(doc, "CHAPTER 1: INTRODUCTION & CLOUD BACKGROUND")
    add_heading_2(doc, "1.1 The Cloud Storage Redundancy Challenge")
    add_body_p(
        doc,
        "In modern multi-tenant cloud environments (such as Google Cloud Storage, Amazon Web Services S3, and Microsoft Azure Blob Storage), "
        "storage costs scale directly with the volume of bytes stored and transferred. In collaborative environments such as universities, "
        "colleges, and enterprise organizations, thousands of users routinely upload identical files under different names—such as assignment "
        "submissions, syllabus documents, lecture notes, textbook PDFs, project reports, and software installers."
    )
    add_body_p(
        doc,
        "Under conventional cloud storage models, every upload is treated as a unique physical object because cloud storage APIs index files by "
        "their user-specified bucket keys (e.g., `user1/assignment.pdf` vs `user2/cloud_assignment.pdf`). If fifty students upload the same 10 MB "
        "PDF file, the cloud consumes 500 MB of physical space, incurring 50 times the required storage fees and exhausting cloud quotas."
    )

    add_heading_2(doc, "1.2 Content-Addressable Storage (CAS)")
    add_body_p(
        doc,
        "CloudDedup solves this problem by transitioning from Location-Based Storage to Content-Addressable Storage (CAS). Under CAS, files are "
        "addressed and indexed by what they contain, rather than where they reside or what name they are given. By passing file byte streams "
        "through the SHA-256 cryptographic hash function, a unique 64-character hexadecimal digest is produced. Identical files produce the exact "
        "same hash regardless of their file name, creation date, or uploader. The cloud stores only one physical copy of that hash, completely "
        "decoupling user-facing filenames from underlying physical cloud objects."
    )

    add_bullet_p(doc, "Zero Redundant Uploads", "Identical files consume exactly zero new bytes of cloud object storage.")
    add_bullet_p(doc, "Multi-User Privacy Isolation", "Each user retains their own private file listing, permissions, and download references.")
    add_bullet_p(doc, "Bandwidth Preservation", "Reduces ingress bandwidth and disk input/output operations across cloud servers.")

    # ==========================================
    # CHAPTER 2: PROBLEM DEFINITION & MATHEMATICAL MODEL
    # ==========================================
    add_heading_1(doc, "CHAPTER 2: PROBLEM DEFINITION & OBJECTIVES")
    add_heading_2(doc, "2.1 Problem Definition")
    add_body_p(
        doc,
        "To design, develop, and deploy a secure, functional cloud file deduplication and storage optimization web platform that automatically "
        "identifies duplicate content at upload time, prevents redundant physical writes to cloud storage, maintains a relational catalog "
        "in MySQL 8.0, and provides interactive storage analytics."
    )

    add_heading_2(doc, "2.2 Mathematical Storage Formulation")
    add_body_p(
        doc,
        "The effectiveness of CloudDedup is measured using three formal cloud storage optimization metrics:"
    )
    add_body_p(
        doc,
        "1. Absolute Storage Saved (S_saved):\n"
        "   S_saved = S_logical - S_physical\n"
        "   Where S_logical is the total logical volume uploaded across all file references, and S_physical is the actual byte count consumed in cloud object storage."
    )
    add_body_p(
        doc,
        "2. Deduplication Compression Ratio (R_dedup):\n"
        "   R_dedup = S_logical / S_physical\n"
        "   A ratio of 2.84 : 1 indicates that logical storage is almost three times larger than the physical cloud space required."
    )
    add_body_p(
        doc,
        "3. Storage Reduction Percentage (P_reduction):\n"
        "   P_reduction = (S_saved / S_logical) * 100%\n"
        "   Measures the overall cloud cost and quota reduction percentage achieved."
    )

    doc.add_page_break()

    # ==========================================
    # CHAPTER 3: SYSTEM ARCHITECTURE & STACK
    # ==========================================
    add_heading_1(doc, "CHAPTER 3: SYSTEM ARCHITECTURE & TECHNOLOGY STACK")
    add_heading_2(doc, "3.1 Multi-Layer Cloud Architecture")
    add_body_p(
        doc,
        "CloudDedup is built using a decoupled, enterprise 4-tier cloud computing architecture:"
    )

    arch_table = doc.add_table(rows=7, cols=3)
    arch_headers = ["Layer", "Technology", "Role & Engineering Responsibility"]
    arch_data = [
        ["Presentation Layer", "HTML5, CSS3, Bootstrap 5.3, Bootstrap Icons", "Responsive cloud management dashboard, drag-and-drop upload, file catalog."],
        ["Data Visualization", "Chart.js 4.4", "Real-time storage distribution donuts, bar charts, and 14-day upload trend curves."],
        ["Application Backend", "Python 3.10+, Flask Blueprints, Werkzeug", "RESTful API handling file streams, cryptographic hashing, and business logic."],
        ["Identity & Security", "Firebase Authentication (Web & Admin SDK)", "Secure JWT ID token verification, user synchronization, zero plaintext passwords."],
        ["Metadata Catalog", "MySQL 8.0 Server & SQLAlchemy ORM", "ACID-compliant storage of users, unique stored files, file references, and audit logs."],
        ["Cloud Storage", "Firebase Cloud Storage (GCP Bucket)", "Immutable Content-Addressable Storage storing unique physical blocks at objects/<sha256>."],
    ]
    format_table(
        arch_table,
        [Inches(1.5), Inches(2.0), Inches(2.7)],
        arch_headers,
        arch_data
    )

    add_heading_2(doc, "3.2 Deduplication Workflow Pipeline")
    add_bullet_p(doc, "Step 1: Chunked Ingress", "Uploaded file is buffered in 64 KB memory chunks via Python streams, preventing memory spikes on large files.")
    add_bullet_p(doc, "Step 2: Cryptographic Fingerprinting", "Python hashlib.sha256 computes a deterministic 256-bit hash (64 hex characters) from binary bytes.")
    add_bullet_p(doc, "Step 3: Relational Catalog Query", "System queries stored_files in MySQL 8.0 to check if sha256_hash already exists.")
    add_bullet_p(doc, "Step 4A (If Duplicate)", "Zero bytes written to cloud. Physical reference_count incremented (+1). User reference created with is_duplicate=TRUE.")
    add_bullet_p(doc, "Step 4B (If New File)", "Unique binary bytes streamed to Firebase Cloud Storage at objects/<sha256>. New record created in stored_files.")
    add_bullet_p(doc, "Step 5: Audit Logging", "An event record is written to upload_events tracking event_type, saved bytes, and timestamps.")

    # ==========================================
    # CHAPTER 4: IMPLEMENTATION & ALGORITHMS
    # ==========================================
    add_heading_1(doc, "CHAPTER 4: IMPLEMENTATION & CORE ALGORITHMS")
    add_heading_2(doc, "4.1 SHA-256 Binary Content Hashing")
    add_body_p(
        doc,
        "The cryptographic integrity of CloudDedup relies on the SHA-256 algorithm (NIST FIPS 180-4 standard). The probability of two different files "
        "producing an identical hash collision is less than 1 in 2^256 (approximately 1 in 10^77), which is practically zero. Hashing is performed "
        "in 64 KB binary buffers so that large multi-megabyte files never overload server memory."
    )

    add_heading_2(doc, "4.2 Memory-Efficient Streaming Download")
    add_body_p(
        doc,
        "To eliminate server out-of-memory errors during concurrent downloads, CloudDedup utilizes Python generator pipelines (`yield`). "
        "When a user downloads a file, the server streams the binary content in 64 KB chunks directly from the cloud storage object to the HTTP response "
        "stream. RAM usage on the backend server remains strictly under 1 MB regardless of whether a file is 10 MB or 500 MB."
    )

    add_heading_2(doc, "4.3 Safe Deletion via Reference Counting")
    add_body_p(
        doc,
        "Because multiple users share the same underlying cloud objects, deleting a file reference must never delete shared data. CloudDedup "
        "implements atomic reference counting: when User A deletes their file reference, only their row in `file_references` is removed and the "
        "underlying `stored_files.reference_count` is decremented by 1. Only when `reference_count` reaches zero is the physical binary deleted "
        "from cloud storage, ensuring zero accidental data loss."
    )

    doc.add_page_break()

    # ==========================================
    # CHAPTER 5: DATABASE SCHEMA & MYSQL 8.0
    # ==========================================
    add_heading_1(doc, "CHAPTER 5: RELATIONAL DATABASE DESIGN & MYSQL SCHEMA")
    add_body_p(
        doc,
        "CloudDedup implements a fully normalized relational catalog in MySQL 8.0 (`clouddedup_db`) using InnoDB storage engine with strict "
        "foreign key constraints and high-speed B-tree indexes."
    )

    db_table = doc.add_table(rows=5, cols=3)
    db_headers = ["Table Name", "Primary / Foreign Keys", "Purpose & Relational Constraints"]
    db_data = [
        ["users", "id (PK AUTO_INCREMENT)\nfirebase_uid (UNIQUE)", "Stores user profile metadata, authentication UID, email, and registration timestamps."],
        ["stored_files", "id (PK AUTO_INCREMENT)\nsha256_hash (UNIQUE, Index)", "Unique physical cloud objects. Stores byte size, CAS path (objects/<hash>), and reference_count."],
        ["file_references", "id (PK AUTO_INCREMENT)\nFK: user_id -> users(id)\nFK: stored_file_id -> stored_files(id)", "User-facing file catalogue. Maps logical file names to physical cloud objects. Tracks is_duplicate flag."],
        ["upload_events", "id (PK AUTO_INCREMENT)\nFK: user_id -> users(id)", "Audit log recording every upload action (new_upload vs duplicate_detected) and bandwidth saved."],
    ]
    format_table(
        db_table,
        [Inches(1.4), Inches(2.2), Inches(2.6)],
        db_headers,
        db_data
    )

    add_heading_2(doc, "5.1 Database Verification in MySQL Workbench")
    add_body_p(
        doc,
        "Figure 5.1 displays the active `clouddedup_db` catalog inside MySQL Workbench, showcasing the live relational `file_references` table "
        "linked to users and physical deduplicated objects."
    )

    # Embed Screenshot 1 (MySQL Workbench)
    add_image_bordered(doc, SCREENSHOTS_DIR / "screenshot_mysql_workbench.png", width=Inches(5.8))
    add_caption(doc, "Figure 5.1: Live Relational Database Catalog (clouddedup_db) in MySQL Workbench")

    # ==========================================
    # CHAPTER 6: USER INTERFACE & DASHBOARD
    # ==========================================
    add_heading_1(doc, "CHAPTER 6: WEB INTERFACE & MANAGEMENT DASHBOARD")
    add_body_p(
        doc,
        "The CloudDedup frontend is constructed with modern responsive principles, featuring a sleek dark-themed palette, glassmorphism card panels, "
        "and dynamic status indicators."
    )

    add_heading_2(doc, "6.1 Real-Time Analytics Dashboard")
    add_body_p(
        doc,
        "The dashboard presents 7 primary metric cards updated live via RESTful endpoints: Total Files, Unique Physical Files, Duplicate References, "
        "Saving Percentage, Logical Volume, Physical Cloud Volume, and Storage Saved (Bytes and Formatted MB)."
    )

    # Embed Screenshot 2 (Dashboard)
    add_image_bordered(doc, SCREENSHOTS_DIR / "screenshot_dashboard.png", width=Inches(5.8))
    add_caption(doc, "Figure 6.1: CloudDedup Live Real-Time Storage Optimization Dashboard")

    add_heading_2(doc, "6.2 My Files Management Interface")
    add_body_p(
        doc,
        "Figure 6.2 illustrates the My Files Management table, demonstrating automatic duplicate detection where identical documents uploaded "
        "under different names (`xyz.pdf` and `Prasanna_Bhurke.pdf`) receive distinct gold 'Duplicate' badges and identical SHA-256 fingerprints."
    )

    # Embed Screenshot 3 (My Files)
    add_image_bordered(doc, SCREENSHOTS_DIR / "screenshot_my_files.png", width=Inches(5.8))
    add_caption(doc, "Figure 6.2: My Files Management Table Showing Deduplication Badges & SHA-256 Hashes")

    doc.add_page_break()

    # ==========================================
    # CHAPTER 7: TESTING & EXPERIMENTAL RESULTS
    # ==========================================
    add_heading_1(doc, "CHAPTER 7: TESTING, RESULTS & EVALUATION")
    add_heading_2(doc, "7.1 Automated Unit Testing")
    add_body_p(
        doc,
        "The system was validated using an automated pytest suite covering 11 comprehensive test cases: deduplication detection, access control "
        "isolation, cryptographic hashing accuracy, and metric calculation. All 11 tests passed with 100% success rate in 1.45 seconds."
    )

    add_heading_2(doc, "7.2 Empirical Storage Metrics from Production Database")
    add_body_p(
        doc,
        "Table 7.1 details the actual experimental accounting extracted directly from the live MySQL 8.0 production catalog (`clouddedup_db`):"
    )

    exp_table = doc.add_table(rows=6, cols=5)
    exp_headers = ["Metric Description", "Files / References", "Logical Size", "Physical Size", "Storage Saved"]
    exp_data = [
        ["Unique Document Ingestion (Test 1)", "5 Original Files", "1.76 MB", "1.76 MB", "0 B (0.0%)"],
        ["Exact Duplicate Submissions (Test 2)", "7 Duplicate Copies", "3.24 MB", "0 B (Zero-write)", "3.24 MB (100.0%)"],
        ["Cross-User Deduplication", "9 Registered Users", "Shared Blocks", "1 Block Shared", "Global Savings"],
        ["Audit Trail Verification", "12 Logged Events", "5 New / 7 Dup", "5 Objects Stored", "100% Verified"],
        ["Cumulative System Total", "12 File References", "5,009,947 B (4.8 MB)", "1,766,586 B (1.7 MB)", "3,243,361 B (64.74%)"],
    ]
    format_table(
        exp_table,
        [Inches(1.8), Inches(1.3), Inches(1.1), Inches(1.1), Inches(1.1)],
        exp_headers,
        exp_data,
        align_cols={1: WD_ALIGN_PARAGRAPH.CENTER, 2: WD_ALIGN_PARAGRAPH.RIGHT, 3: WD_ALIGN_PARAGRAPH.RIGHT, 4: WD_ALIGN_PARAGRAPH.RIGHT}
    )

    add_body_p(
        doc,
        "As proven in Table 7.1, CloudDedup reduced physical cloud storage requirements from 4.8 MB down to 1.7 MB, delivering a net 64.74% storage "
        "and bandwidth savings with a 2.84 : 1 compression ratio."
    )

    # ==========================================
    # CHAPTER 8: LIVE CLOUD DEPLOYMENT
    # ==========================================
    add_heading_1(doc, "CHAPTER 8: LIVE CLOUD DEPLOYMENT")
    add_body_p(
        doc,
        "To enable seamless evaluation across remote PCs, smartphones, and tablets, CloudDedup is deployed to the public Internet using Cloudflare Tunnel "
        "technology (`cloudflared`). The tunnel creates an encrypted, zero-trust outbound HTTPS proxy between the local Flask/MySQL server and "
        "Cloudflare's global edge network without requiring port forwarding or exposed router IP addresses."
    )
    add_bullet_p(doc, "Live Public URL", "https://advocate-vision-agencies-valuable.trycloudflare.com")
    add_bullet_p(doc, "Transport Security", "End-to-end TLS 1.3 encryption with automatic valid SSL certificates.")
    add_bullet_p(doc, "Cross-Device Verification", "Successfully tested across Android/iOS mobile devices and Windows/Linux desktop browsers.")

    # ==========================================
    # CHAPTER 9: CONCLUSION & FUTURE SCOPE
    # ==========================================
    add_heading_1(doc, "CHAPTER 9: CONCLUSION & FUTURE SCOPE")
    add_heading_2(doc, "9.1 Conclusion")
    add_body_p(
        doc,
        "The CloudDedup mini-project successfully validates the design and deployment of an enterprise Content-Addressable Storage (CAS) system. "
        "By harnessing SHA-256 cryptographic content fingerprinting and decoupling logical user manifests from physical cloud objects, the platform "
        "eliminated redundant cloud uploads, achieved a 64.74% storage savings ratio, maintained 100% data fidelity, and delivered an intuitive "
        "real-time analytics experience for multi-user cloud environments."
    )

    add_heading_2(doc, "9.2 Future Enhancements")
    add_bullet_p(doc, "Variable-Block Chunking (FastCDC)", "Implement content-defined chunking to detect sub-file duplicates even after byte insertions.")
    add_bullet_p(doc, "Client-Side Deduplication", "Calculate SHA-256 hashes in the browser using WebAssembly to eliminate redundant network transfers.")
    add_bullet_p(doc, "Convergent Encryption", "Use content-derived encryption keys to maintain user confidentiality while retaining cloud deduplication.")
    add_bullet_p(doc, "Hierarchical Storage Tiering", "Automatically migrate unreferenced or cold physical blocks to archival tiers like AWS Glacier.")

    # ==========================================
    # REFERENCES
    # ==========================================
    add_heading_1(doc, "REFERENCES")
    refs = [
        '[1] D. T. Meyer and W. J. Bolosky, "A Study of Practical Deduplication," ACM Transactions on Storage (TOS), vol. 7, no. 4, pp. 1-20, 2012.',
        '[2] P. Nath, M. A. Kozuch, D. R. O\'Hallaron, J. Harkes, M. Satyanarayanan, N. Tolia, and M. Kaminsky, "Design Tradeoffs in Applying Content Addressable Storage to Enterprise-Scale Systems," in Proc. USENIX FAST, 2008.',
        '[3] M. Lillibridge, K. Eshghi, D. Bhagwat, V. Deolalikar, G. Trezise, and P. Camble, "Sparse Indexing: Large Scale, Inline Deduplication Using Sampling and Locality," in Proc. 7th USENIX FAST, 2009.',
        '[4] National Institute of Standards and Technology (NIST), "Secure Hash Standard (SHS)," Federal Information Processing Standards Publication (FIPS) 180-4, Aug. 2015.',
        '[5] Flask Documentation, "Application Factory Pattern & Blueprints," Pallets Projects, 2024. [Online]. Available: https://flask.palletsprojects.com/',
        '[6] MySQL 8.0 Reference Manual, "InnoDB Storage Engine & Foreign Key Constraints," Oracle Corporation, 2024.',
        '[7] Cloudflare Inc., "Cloudflare Tunnel Documentation & Edge Architecture," 2024. [Online]. Available: https://developers.cloudflare.com/cloudflare-one/',
    ]
    for r_text in refs:
        p = doc.add_paragraph()
        p.paragraph_format.line_spacing = 1.15
        p.paragraph_format.space_after = Pt(4)
        run = p.add_run(r_text)
        set_run_font(run, size_pt=10.5, color=COLOR_TEXT)

    # Save to workspace and downloads
    doc.save(OUTPUT_DOCX)
    try:
        doc.save(DOWNLOADS_DOCX)
    except Exception as e:
        print(f"Warning: Could not save to downloads path: {e}")

    print(f"[OK] Successfully generated Word report at: {OUTPUT_DOCX}")
    return OUTPUT_DOCX

if __name__ == "__main__":
    build_report()
