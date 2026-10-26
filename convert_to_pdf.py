import os
import sys
from pathlib import Path
import win32com.client
import pypdf

BASE_DIR = Path(__file__).resolve().parent
DOCX_PATH = BASE_DIR / "Cloud_File_Deduplication_Project_Report.docx"
PDF_PATH = BASE_DIR / "Cloud_File_Deduplication_Project_Report.pdf"
DOWNLOADS_PDF = Path("C:/Users/PRASANNA/Downloads/Cloud_File_Deduplication_Project_Report.pdf")
DOWNLOADS_DOCX = Path("C:/Users/PRASANNA/Downloads/Cloud_File_Deduplication_Project_Report.docx")

def convert_docx_to_pdf():
    print(f"Opening Word to convert {DOCX_PATH} -> {PDF_PATH}...")
    word = win32com.client.DispatchEx("Word.Application")
    word.Visible = False
    word.DisplayAlerts = 0  # wdAlertsNone

    try:
        doc = word.Documents.Open(str(DOCX_PATH), ReadOnly=True)
        # wdFormatPDF = 17
        doc.SaveAs(str(PDF_PATH), FileFormat=17)
        doc.Close(SaveChanges=False)
        print("[OK] Converted DOCX to PDF successfully.")
    except Exception as e:
        print(f"[ERROR] Conversion failed: {e}")
        raise
    finally:
        word.Quit()

    # Check page count
    reader = pypdf.PdfReader(str(PDF_PATH))
    page_count = len(reader.pages)
    print(f"[OK] Total PDF Pages: {page_count}")

    # Copy to downloads
    try:
        import shutil
        shutil.copyfile(str(PDF_PATH), str(DOWNLOADS_PDF))
        shutil.copyfile(str(DOCX_PATH), str(DOWNLOADS_DOCX))
        print(f"[OK] Copied latest PDF and DOCX to {DOWNLOADS_PDF.parent}")
    except Exception as e:
        print(f"Warning copying to downloads: {e}")

if __name__ == "__main__":
    convert_docx_to_pdf()
