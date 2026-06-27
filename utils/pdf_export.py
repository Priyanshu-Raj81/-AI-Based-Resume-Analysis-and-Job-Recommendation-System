"""
utils/pdf_export.py
-------------------
Shared PDF generation utility for Resumatch AI.
Converts plain text / markdown content to a styled PDF using ReportLab.
Called by: views/learning.py, views/interview.py, views/analyzer.py
"""

import re
import io

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from reportlab.lib.enums import TA_CENTER

# ── Brand colors ──────────────────────────────────────────────────────────────
_PRIMARY   = colors.HexColor("#4f46e5")
_SECONDARY = colors.HexColor("#7c3aed")
_TEXT      = colors.HexColor("#1a1a2e")
_MUTED     = colors.HexColor("#555577")

# ── Paragraph styles ──────────────────────────────────────────────────────────
_TITLE  = ParagraphStyle("rm_title",  fontSize=18, textColor=_PRIMARY,
                         fontName="Helvetica-Bold", alignment=TA_CENTER, spaceAfter=6)
_H2     = ParagraphStyle("rm_h2",     fontSize=14, textColor=_PRIMARY,
                         fontName="Helvetica-Bold", spaceBefore=14, spaceAfter=4)
_H3     = ParagraphStyle("rm_h3",     fontSize=11, textColor=_SECONDARY,
                         fontName="Helvetica-Bold", spaceBefore=8,  spaceAfter=3)
_BODY   = ParagraphStyle("rm_body",   fontSize=10, textColor=_TEXT,
                         fontName="Helvetica",      leading=15,     spaceAfter=2)
_BULLET = ParagraphStyle("rm_bullet", fontSize=10, textColor=_TEXT,
                         fontName="Helvetica",      leading=14,     spaceAfter=2,
                         leftIndent=14, bulletIndent=4, bulletText="\u2022")
_META   = ParagraphStyle("rm_meta",   fontSize=9,  textColor=_MUTED,
                         fontName="Helvetica",      alignment=TA_CENTER, spaceAfter=10)


def _clean(line: str) -> str:
    """Convert basic markdown to ReportLab-compatible HTML fragments."""
    line = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', line)
    line = re.sub(r'\*(.*?)\*',     r'<i>\1</i>', line)
    line = re.sub(r'`(.*?)`',       r'<font color="#6366f1">\1</font>', line)
    line = re.sub(
        r'\[([^\]]+)\]\(([^)]+)\)',
        r'<a href="\2"><font color="#6366f1">\1</font></a>',
        line
    )
    return line.strip()


def generate_pdf(text: str, title: str, subtitle: str = "") -> bytes:
    """
    Convert markdown/plain text to a styled PDF.

    Args:
        text:     The content to render (supports ## ### - * ** `` [text](url))
        title:    Main heading shown at the top of the PDF
        subtitle: Optional second line under the title (role · level etc.)

    Returns:
        PDF as raw bytes — pass directly to st.download_button(data=...)
    """
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=A4,
        leftMargin=22*mm, rightMargin=22*mm,
        topMargin=18*mm,  bottomMargin=18*mm,
    )

    story = [Paragraph(title, _TITLE)]
    if subtitle:
        story.append(Paragraph(subtitle, _META))
    story.append(HRFlowable(width="100%", thickness=1, color=_PRIMARY, spaceAfter=10))

    for raw_line in text.split("\n"):
        line = raw_line.rstrip()

        if line.startswith("## "):
            story.append(Paragraph(_clean(line[3:]), _H2))
        elif line.startswith("### "):
            story.append(Paragraph(_clean(line[4:]), _H3))
        elif line.startswith("# "):
            story.append(Paragraph(_clean(line[2:]), _H2))
        elif line.strip().startswith("- ") or line.strip().startswith("* "):
            story.append(Paragraph(_clean(line.strip()[2:]), _BULLET))
        elif line.strip() == "":
            story.append(Spacer(1, 5))
        else:
            story.append(Paragraph(_clean(line), _BODY))

    doc.build(story)
    return buf.getvalue()