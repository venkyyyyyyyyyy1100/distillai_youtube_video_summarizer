"""
utils/pdf_export.py
-------------------
Generates a styled, downloadable PDF from the AI-generated summary.

The PDF includes:
  - A branded orange header with title and generation date
  - A highlighted source video URL box
  - Section headings, bullet points, and body paragraphs
  - A footer crediting the tool and Gemini
"""

import io
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer,
    HRFlowable, Table, TableStyle
)

# ---------- BRAND COLOURS ----------
ORANGE = colors.HexColor("#FF6B35")
DARK   = colors.HexColor("#3D2B1F")
MUTED  = colors.HexColor("#7A5C48")

# Emoji characters that mark the start of a section heading in the summary
SECTION_EMOJIS = {"🎯", "📝", "🔑", "💡", "🔄"}


def _build_styles() -> dict:
    """
    Create and return a dictionary of ReportLab ParagraphStyle objects
    used throughout the PDF.

    Returns:
        Dict mapping style name → ParagraphStyle instance.
    """
    return {
        "title": ParagraphStyle(
            "DocTitle",
            fontName="Helvetica-Bold",
            fontSize=22,
            textColor=colors.white,
            leading=28,
            alignment=TA_CENTER,
            spaceAfter=4,
        ),
        "subtitle": ParagraphStyle(
            "DocSubtitle",
            fontName="Helvetica",
            fontSize=10,
            textColor=colors.HexColor("#FFD166"),
            leading=14,
            alignment=TA_CENTER,
            spaceAfter=0,
        ),
        "url_label": ParagraphStyle(
            "UrlLabel",
            fontName="Helvetica-Bold",
            fontSize=9,
            textColor=MUTED,
            leading=12,
            spaceAfter=2,
        ),
        "url": ParagraphStyle(
            "Url",
            fontName="Helvetica",
            fontSize=9,
            textColor=ORANGE,
            leading=12,
            spaceAfter=0,
        ),
        "section_heading": ParagraphStyle(
            "SectionHeading",
            fontName="Helvetica-Bold",
            fontSize=12,
            textColor=ORANGE,
            leading=16,
            spaceBefore=14,
            spaceAfter=5,
        ),
        "body": ParagraphStyle(
            "Body",
            fontName="Helvetica",
            fontSize=10,
            textColor=DARK,
            leading=16,
            spaceAfter=6,
        ),
        "bullet": ParagraphStyle(
            "Bullet",
            fontName="Helvetica",
            fontSize=10,
            textColor=DARK,
            leading=16,
            leftIndent=12,
            spaceAfter=4,
        ),
        "footer": ParagraphStyle(
            "Footer",
            fontName="Helvetica",
            fontSize=8,
            textColor=MUTED,
            alignment=TA_CENTER,
        ),
    }


def _build_header(styles: dict) -> Table:
    """
    Build the orange branded header table for the top of the PDF.

    Args:
        styles: Style dictionary from _build_styles().

    Returns:
        A ReportLab Table element with orange background.
    """
    header_content = [
        [Paragraph("YouTube Video Summary", styles["title"])],
        [Paragraph(f"Generated on {datetime.now().strftime('%B %d, %Y')}", styles["subtitle"])],
    ]
    table = Table(header_content, colWidths=[170 * mm])
    table.setStyle(TableStyle([
        ("BACKGROUND",     (0, 0), (-1, -1), ORANGE),
        ("ROUNDEDCORNERS", [10]),
        ("TOPPADDING",     (0, 0), (-1, 0),  18),
        ("BOTTOMPADDING",  (0, -1), (-1, -1), 18),
        ("LEFTPADDING",    (0, 0), (-1, -1), 16),
        ("RIGHTPADDING",   (0, 0), (-1, -1), 16),
    ]))
    return table


def _build_url_box(youtube_url: str, styles: dict) -> Table:
    """
    Build the source URL info box placed below the header.

    Args:
        youtube_url : The original YouTube video URL string.
        styles      : Style dictionary from _build_styles().

    Returns:
        A ReportLab Table element with a light orange background.
    """
    url_content = [
        [Paragraph("Source Video:", styles["url_label"])],
        [Paragraph(youtube_url,     styles["url"])],
    ]
    table = Table(url_content, colWidths=[170 * mm])
    table.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), colors.HexColor("#FFF3E8")),
        ("ROUNDEDCORNERS", [8]),
        ("TOPPADDING",    (0, 0), (-1, 0),  8),
        ("BOTTOMPADDING", (0, -1), (-1, -1), 8),
        ("LEFTPADDING",   (0, 0), (-1, -1), 12),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 12),
        ("LINEBELOW",     (0, 0), (-1, 0),  0.5, colors.HexColor("#E8D5C4")),
    ]))
    return table


def _parse_summary_to_story(summary_text: str, styles: dict) -> list:
    """
    Parse the plain-text summary produced by Gemini into a list of
    ReportLab Flowable elements (headings, bullets, body paragraphs).

    Args:
        summary_text : The full summary string from Gemini.
        styles       : Style dictionary from _build_styles().

    Returns:
        List of ReportLab Flowable objects ready to be added to the story.
    """
    story_elements = []

    for line in summary_text.split("\n"):
        stripped = line.strip()

        if not stripped:
            story_elements.append(Spacer(1, 3))
            continue

        is_heading = any(stripped.startswith(e) for e in SECTION_EMOJIS)

        if is_heading:
            clean = stripped.replace("**", "")
            story_elements.append(Paragraph(clean, styles["section_heading"]))

        elif stripped.startswith("- ") or stripped.startswith("• "):
            story_elements.append(Paragraph(f"  • {stripped[2:]}", styles["bullet"]))

        else:
            clean = stripped.replace("**", "")
            story_elements.append(Paragraph(clean, styles["body"]))

    return story_elements


# ---------- PUBLIC ENTRY POINT ----------
def build_pdf(summary_text: str, youtube_url: str) -> bytes:
    """
    Build and return a complete styled PDF as raw bytes.

    Args:
        summary_text : The AI-generated summary string.
        youtube_url  : The source YouTube video URL to embed in the PDF.

    Returns:
        PDF file contents as a bytes object (ready for st.download_button).
    """
    buffer = io.BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=20 * mm,
        leftMargin=20 * mm,
        topMargin=20 * mm,
        bottomMargin=20 * mm,
    )

    styles = _build_styles()
    story  = []

    # Header
    story.append(_build_header(styles))
    story.append(Spacer(1, 10 * mm))

    # Source URL box
    story.append(_build_url_box(youtube_url, styles))
    story.append(Spacer(1, 8 * mm))
    story.append(HRFlowable(width="100%", thickness=1.5, color=ORANGE, spaceAfter=8))

    # Summary body
    story.extend(_parse_summary_to_story(summary_text, styles))

    # Footer
    story.append(Spacer(1, 10 * mm))
    story.append(HRFlowable(
        width="100%", thickness=0.8,
        color=colors.HexColor("#E8D5C4"), spaceAfter=6
    ))
    story.append(Paragraph(
        "Generated by YouTube Summarizer · Powered by Google Gemini",
        styles["footer"]
    ))

    doc.build(story)
    return buffer.getvalue()