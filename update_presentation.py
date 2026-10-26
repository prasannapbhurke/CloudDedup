"""
Update Cloud_File_Deduplication_College_Presentation.pptx:
- Set all fonts to Times New Roman
- Add elegant slide borders on all slides
- Embed live screenshots (Dashboard, My Files, MySQL Workbench)
- Update text content with real MySQL 8.0 schema and 64.74% deduplication metrics
"""

import os
from pathlib import Path
import pptx
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN

BASE_DIR = Path(__file__).resolve().parent
SCREENSHOTS_DIR = BASE_DIR / "docs" / "screenshots"
INPUT_PPTX = BASE_DIR / "Cloud_File_Deduplication_College_Presentation.pptx"
OUTPUT_PPTX = BASE_DIR / "Cloud_File_Deduplication_College_Presentation.pptx"
DOWNLOADS_PPTX = Path("C:/Users/PRASANNA/Downloads/Cloud_File_Deduplication_College_Presentation.pptx")

COLOR_BORDER = RGBColor(26, 54, 93)     # #1A365D Deep Navy
COLOR_SECONDARY = RGBColor(43, 108, 176) # #2B6CB0 Slate Blue

def set_all_fonts_times_new_roman(prs):
    for slide_idx, slide in enumerate(prs.slides):
        for shape in slide.shapes:
            if shape.has_text_frame:
                for paragraph in shape.text_frame.paragraphs:
                    if paragraph.font:
                        paragraph.font.name = "Times New Roman"
                    for run in paragraph.runs:
                        run.font.name = "Times New Roman"
            elif shape.has_table:
                for row in shape.table.rows:
                    for cell in row.cells:
                        for paragraph in cell.text_frame.paragraphs:
                            if paragraph.font:
                                paragraph.font.name = "Times New Roman"
                            for run in paragraph.runs:
                                run.font.name = "Times New Roman"

def add_slide_outer_border(prs):
    slide_width = prs.slide_width
    slide_height = prs.slide_height
    margin = Inches(0.2)
    
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
    prs = Presentation(str(INPUT_PPTX))

    # 1. Update Slide 6: Database Design with MySQL 8.0 & Screenshot
    slide_db = prs.slides[5] # 0-indexed slide 6
    # Remove existing old shapes on right if any, or adjust layout
    print("Updating Slide 6 (Database Design)...")
    # Let's inspect slide 6 title
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

    # Add MySQL Workbench screenshot onto Slide 6
    sw_path = SCREENSHOTS_DIR / "screenshot_mysql_workbench.png"
    if sw_path.exists():
        # Place small preview on slide 6
        pic_db = slide_db.shapes.add_picture(
            str(sw_path),
            Inches(8.5),
            Inches(1.8),
            width=Inches(4.3)
        )
        pic_db.line.color.rgb = COLOR_BORDER
        pic_db.line.width = Pt(1.5)

    # 2. Update Slide 9: User Interface with Live Dashboard Screenshot
    slide_ui = prs.slides[8] # 0-indexed slide 9
    print("Updating Slide 9 (User Interface)...")
    # Replace existing picture if found or overlay fresh screenshot
    s_dash_path = SCREENSHOTS_DIR / "screenshot_dashboard.png"
    if s_dash_path.exists():
        # Let's delete the old shape 5 (placeholder) or overlay precisely
        pic_ui = slide_ui.shapes.add_picture(
            str(s_dash_path),
            Inches(0.8),
            Inches(1.75),
            width=Inches(7.3)
        )
        pic_ui.line.color.rgb = COLOR_BORDER
        pic_ui.line.width = Pt(1.5)

    # Update caption on slide 9
    for shape in slide_ui.shapes:
        if shape.has_text_frame and "Figure 4.1" in shape.text_frame.text:
            shape.text_frame.text = "Figure 4.1: CloudDedup Live Real-Time Storage Optimization Dashboard (Dark Theme)"

    # 3. Update Slide 10: Testing & Results with My Files Screenshot & Real Metrics
    slide_test = prs.slides[9] # 0-indexed slide 10
    print("Updating Slide 10 (Testing & Results)...")
    s_files_path = SCREENSHOTS_DIR / "screenshot_my_files.png"
    if s_files_path.exists():
        pic_test = slide_test.shapes.add_picture(
            str(s_files_path),
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
                    p.text = "64.74% Overall Space Reduction: Total logical volume of 4.8 MB consumed only 1.7 MB in cloud storage (2.84 : 1 compression ratio)."
                elif "Figure 5.1" in p.text:
                    p.text = "Figure 5.1: Live File Catalog Showing 100% Duplicate Detection Badges in Real Time"

    # 4. Set Times New Roman everywhere
    print("Setting all fonts to Times New Roman...")
    set_all_fonts_times_new_roman(prs)

    # 5. Add elegant slide outer borders
    print("Adding slide outer borders...")
    add_slide_outer_border(prs)

    # Save presentation
    prs.save(str(OUTPUT_PPTX))
    try:
        prs.save(str(DOWNLOADS_PPTX))
    except Exception as e:
        print(f"Warning saving to downloads: {e}")

    print(f"[OK] Successfully updated presentation at: {OUTPUT_PPTX}")

if __name__ == "__main__":
    update_presentation()
