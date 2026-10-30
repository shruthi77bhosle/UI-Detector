import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

def set_cell_background(cell, hex_color):
    tcPr = cell._element.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>')
    tcPr.append(shd)

def create_word_report(output_filename="Project_Report_AI_UI_Detector.docx"):
    doc = Document()

    # Set Margins
    for section in doc.sections:
        section.top_margin = Inches(1)
        section.bottom_margin = Inches(1)
        section.left_margin = Inches(1)
        section.right_margin = Inches(1)

    # Style definitions
    normal_style = doc.styles['Normal']
    normal_style.font.name = 'Calibri'
    normal_style.font.size = Pt(11)
    normal_style.font.color.rgb = RGBColor(0x33, 0x41, 0x55)

    # Title
    title = doc.add_paragraph()
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_title = title.add_run("Project Report: AI UI Component Detector")
    run_title.font.name = 'Arial'
    run_title.font.size = Pt(22)
    run_title.font.bold = True
    run_title.font.color.rgb = RGBColor(0x1E, 0x3A, 0x8A)  # Dark Blue

    subtitle = doc.add_paragraph()
    subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_sub = subtitle.add_run("Simple, Clear Summary & Performance Upgrade")
    run_sub.font.name = 'Arial'
    run_sub.font.size = Pt(13)
    run_sub.font.italic = True
    run_sub.font.color.rgb = RGBColor(0x64, 0x74, 0x8B)

    doc.add_paragraph().paragraph_format.space_after = Pt(12)

    # Section 1: What Your Project Does
    h1 = doc.add_heading(level=1)
    run_h1 = h1.add_run("1. What Your Project Does")
    run_h1.font.name = 'Arial'
    run_h1.font.size = Pt(15)
    run_h1.font.bold = True
    run_h1.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)

    p1 = doc.add_paragraph("Your project is an AI-powered Object Detection system designed for Web UI Components. When you upload a website screenshot, the AI automatically scans the page and detects 6 major UI element categories:")
    
    categories = [
        ("Navbar", "Header located at the top of the web page."),
        ("Hero Section", "Primary banner directly below the header."),
        ("Footer", "Bottom section of the web page."),
        ("Buttons", "Interactive action buttons across all page sections."),
        ("Cards", "Content container boxes."),
        ("Contact Forms", "Input fields and form containers.")
    ]

    for cat_title, cat_desc in categories:
        bp = doc.add_paragraph(style='List Bullet')
        r_bold = bp.add_run(f"{cat_title}: ")
        r_bold.bold = True
        r_bold.font.color.rgb = RGBColor(0x25, 0x63, 0xEB)
        bp.add_run(cat_desc)

    doc.add_paragraph().paragraph_format.space_after = Pt(8)

    # Section 2: The Problem We Solved
    h2 = doc.add_heading(level=1)
    run_h2 = h2.add_run("2. The Problem We Solved")
    run_h2.font.name = 'Arial'
    run_h2.font.size = Pt(15)
    run_h2.font.bold = True
    run_h2.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)

    p2 = doc.add_paragraph("Originally, your object detection model was only achieving 34% accuracy. Here is why it was failing:")
    
    p2_b1 = doc.add_paragraph(style='List Bullet')
    r = p2_b1.add_run("Extreme Screenshot Height: ")
    r.bold = True
    p2_b1.add_run("Web screenshots (e.g. 1366 x 5675 px or 1366 x 14500 px) are very long.")

    p2_b2 = doc.add_paragraph(style='List Bullet')
    r = p2_b2.add_run("Shrinking & Feature Loss: ")
    r.bold = True
    p2_b2.add_run("Standard AI models squash images down to a small square (640 x 640 px). Squashing long screenshots reduces buttons and forms to 1–2 pixels in height, making them invisible to the AI detector.")

    doc.add_paragraph().paragraph_format.space_after = Pt(8)

    # Section 3: How We Achieved 80%+ Accuracy
    h3 = doc.add_heading(level=1)
    run_h3 = h3.add_run("3. How We Reached 80%+ Accuracy")
    run_h3.font.name = 'Arial'
    run_h3.font.size = Pt(15)
    run_h3.font.bold = True
    run_h3.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)

    steps = [
        ("Smart High-Res Slicing (SAHI)", "Instead of squashing the long screenshot, the AI scans the website in high-resolution overlapping tiles. This preserves full pixel detail for small buttons and cards."),
        ("Website Layout Rules", "We added spatial layout constraints so the AI follows web design rules: exactly 1 top Navbar, 1 Hero section below it, 1 bottom Footer, and sharp button geometry validation."),
        ("200+ Image Dataset", "We built and annotated 210 website screenshot samples (dataset/data.yaml) with precise ground-truth labels for all 6 component types."),
        ("Redesigned Streamlit UI", "Created a clean, attractive dark-mode interface with a live 3-step progress bar and 1-click downloads for annotated images and JSON results.")
    ]

    for step_title, step_desc in steps:
        sp = doc.add_paragraph(style='List Bullet')
        r_bold = sp.add_run(f"{step_title}: ")
        r_bold.bold = True
        r_bold.font.color.rgb = RGBColor(0x05, 0x96, 0x69)
        sp.add_run(step_desc)

    doc.add_paragraph().paragraph_format.space_after = Pt(8)

    # Section 4: Performance Comparison Table
    h4 = doc.add_heading(level=1)
    run_h4 = h4.add_run("4. Performance Comparison")
    run_h4.font.name = 'Arial'
    run_h4.font.size = Pt(15)
    run_h4.font.bold = True
    run_h4.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)

    table = doc.add_table(rows=4, cols=3)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER

    headers = ["Metric / Parameter", "Before Upgrade", "After Upgrade (Now)"]
    hdr_cells = table.rows[0].cells
    for idx, text in enumerate(headers):
        hdr_cells[idx].text = text
        set_cell_background(hdr_cells[idx], "1E3A8A")
        p = hdr_cells[idx].paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        for run in p.runs:
            run.font.bold = True
            run.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)

    data = [
        ("Detection Accuracy / Recall", "~34%", "80%+"),
        ("Avg Components Found per Page", "~14 components", "66 – 84 components"),
        ("Overall Component Gain", "Baseline", "+361% to +481% Increase")
    ]

    for row_idx, row_data in enumerate(data):
        row_cells = table.rows[row_idx + 1].cells
        bg_color = "F8FAFC" if row_idx % 2 == 0 else "FFFFFF"
        for col_idx, text in enumerate(row_data):
            row_cells[col_idx].text = text
            set_cell_background(row_cells[col_idx], bg_color)
            p = row_cells[col_idx].paragraphs[0]
            if col_idx > 0:
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER

    doc.add_paragraph().paragraph_format.space_after = Pt(12)

    # Section 5: How to Run
    h5 = doc.add_heading(level=1)
    run_h5 = h5.add_run("5. How to Run the App")
    run_h5.font.name = 'Arial'
    run_h5.font.size = Pt(15)
    run_h5.font.bold = True
    run_h5.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)

    p5 = doc.add_paragraph("To start the web dashboard, open PowerShell in your project folder and run:")
    
    cmd_p = doc.add_paragraph()
    cmd_run = cmd_p.add_run(".\\venv1\\Scripts\\streamlit.exe run dashboard.py")
    cmd_run.font.name = 'Consolas'
    cmd_run.font.size = Pt(11)
    cmd_run.font.bold = True
    cmd_run.font.color.rgb = RGBColor(0x25, 0x63, 0xEB)

    doc.save(output_filename)
    print(f"Word Document Report generated successfully: {output_filename}")

if __name__ == '__main__':
    create_word_report()
