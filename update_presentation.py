"""
Update Cloud_File_Deduplication_College_Presentation.pptx:
- Times New Roman font across all slides
- Clean slide borders
- High-res crisp project screenshots (dashboard_screenshot.png, dashboard_stats_overview.png)
- Full project details: Flask, MySQL 8.0 schema, Firebase CAS, and 64.74% live test metrics
"""

import os
from pathlib import Path
import shutil
import pptx
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE

BASE_DIR = Path(__file__).resolve().parent
CLEAN_ORIGINAL = Path("C:/Users/PRASANNA/Desktop/Cloud_File_Deduplication_Project/Cloud_File_Deduplication_College_Presentation.pptx")
TARGET_PPTX = BASE_DIR / "Cloud_File_Deduplication_College_Presentation.pptx"
DOWNLOADS_PPTX = Path("C:/Users/PRASANNA/Downloads/Cloud_File_Deduplication_College_Presentation.pptx")

COLOR_BORDER = RGBColor(30, 58, 138)     # Navy
COLOR_SECONDARY = RGBColor(71, 85, 105)  # Slate

def set_all_fonts_times_new_roman(prs):
    for slide in prs.slides:
        for shape in slide.shapes:
            if shape.has_text_frame:
                for paragraph in shape.text_frame.paragraphs:
                    paragraph.font.name = "Times New Roman"
                    for run in paragraph.runs:
                        run.font.name = "Times New Roman"
            elif shape.has_table:
                for row in shape.table.rows:
                    for cell in row.cells:
                        for paragraph in cell.text_frame.paragraphs:
                            paragraph.font.name = "Times New Roman"
                            for run in paragraph.runs:
                                run.font.name = "Times New Roman"

def add_slide_outer_border(prs):
    slide_width = prs.slide_width
    slide_height = prs.slide_height
    margin = Inches(0.18)
    
    for slide in prs.slides:
        border_shape = slide.shapes.add_shape(
            MSO_SHAPE.RECTANGLE,
            margin,
            margin,
            slide_width - (2 * margin),
            slide_height - (2 * margin)
        )
        border_shape.fill.background()
        border_shape.line.color.rgb = COLOR_BORDER
        border_shape.line.width = Pt(2.0)

def update_presentation():
    # If clean original exists, start fresh to prevent duplicate overlays
    if CLEAN_ORIGINAL.exists():
        print(f"Loading clean base from {CLEAN_ORIGINAL}...")
        prs = Presentation(str(CLEAN_ORIGINAL))
    else:
        prs = Presentation(str(TARGET_PPTX))

    # Slide 6: Database Design -> Modernize to MySQL 8.0 & SQLite
    slide_db = prs.slides[5]
    print("Updating Slide 6 (Database Design)...")
    for shape in slide_db.shapes:
        if shape.has_text_frame:
            for p in shape.text_frame.paragraphs:
                if "Table: chunks" in p.text:
                    p.text = "Table: stored_files"
                elif "Stores Unique Physical Blocks" in p.text:
                    p.text = "Unique Physical Cloud Objects (CAS)"
                elif "chunk_hash" in p.text and "Primary Key" in p.text:
                    p.text = "Primary Key: id | UNIQUE: sha256_hash\nColumns: file_size, storage_path, reference_count, mime_type"
                elif "Table: user_files" in p.text:
                    p.text = "Table: file_references"
                elif "Stores Virtual File Records" in p.text:
                    p.text = "User File Catalogue & Deduplication Flags"
                elif "filename (TEXT)" in p.text:
                    p.text = "Foreign Keys: user_id -> users(id), stored_file_id -> stored_files(id)\nColumns: display_name, is_duplicate, uploaded_at"
                elif "Table: file_chunks" in p.text:
                    p.text = "Tables: users & upload_events"
                elif "The Recipe Map" in p.text:
                    p.text = "Auth Sync & Deduplication Audit Trail"
                elif "Composite Primary Key" in p.text:
                    p.text = "users: firebase_uid, email, name\nupload_events: user_id, event_type, saved_bytes, timestamp"

    # Slide 9: User Interface -> Embed crisp dashboard_screenshot.png
    slide_ui = prs.slides[8]
    print("Updating Slide 9 (User Interface)...")
    dash_img = BASE_DIR / "dashboard_screenshot.png"
    if dash_img.exists():
        pic_ui = slide_ui.shapes.add_picture(
            str(dash_img),
            Inches(0.8),
            Inches(1.75),
            width=Inches(7.3)
        )
        pic_ui.line.color.rgb = COLOR_BORDER
        pic_ui.line.width = Pt(1.5)

    for shape in slide_ui.shapes:
        if shape.has_text_frame and "Figure 4.1" in shape.text_frame.text:
            shape.text_frame.text = "Figure 4.1: CloudDedup Live Real-Time Storage Optimization Dashboard"

    # Slide 10: Testing & Results -> Embed crisp dashboard_stats_overview.png
    slide_test = prs.slides[9]
    print("Updating Slide 10 (Testing & Results)...")
    stats_img = BASE_DIR / "dashboard_stats_overview.png"
    if not stats_img.exists():
        stats_img = BASE_DIR / "savings_chart.png"

    if stats_img.exists():
        pic_test = slide_test.shapes.add_picture(
            str(stats_img),
            Inches(7.85),
            Inches(1.72),
            width=Inches(4.8)
        )
        pic_test.line.color.rgb = COLOR_BORDER
        pic_test.line.width = Pt(1.5)

    for shape in slide_test.shapes:
        if shape.has_text_frame:
            for p in shape.text_frame.paragraphs:
                if "63.3% Overall Space Reduction" in p.text:
                    p.text = "64.74% Overall Space Reduction: Total logical volume of 4.8 MB consumed only 1.7 MB on cloud storage (2.84 : 1 compression ratio)."
                elif "Figure 5.1" in p.text:
                    p.text = "Figure 5.1: Live Storage Optimization Overview & 100% Deduplication Metrics"

    # Apply Times New Roman across all slides
    print("Applying Times New Roman font to all text runs...")
    set_all_fonts_times_new_roman(prs)

    # Add outer slide framing borders
    print("Adding slide outer borders...")
    add_slide_outer_border(prs)

    prs.save(str(TARGET_PPTX))
    try:
        prs.save(str(DOWNLOADS_PPTX))
    except Exception as e:
        print(f"Warning saving to downloads: {e}")

    print(f"[OK] Successfully saved updated presentation to: {TARGET_PPTX}")

if __name__ == "__main__":
    update_presentation()
