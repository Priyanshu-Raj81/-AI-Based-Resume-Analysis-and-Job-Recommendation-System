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


def _escape_xml(text: str) -> str:
    """
    Escape XML-special characters so raw text (including anything an LLM
    might generate, like `if x<y:`, `a && b`, or `<T>` generics) can never
    be mistaken for markup by ReportLab's paraparser. Must run BEFORE any
    markdown-to-tag conversion below, on the ORIGINAL text only — never on
    text that already contains our own injected <b>/<i>/<font>/<a> tags,
    or those tags would get escaped too and stop rendering as formatting.
    """
    return (
        text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
    )


# Broad Unicode ranges covering emoji / pictographs / dingbats / symbol blocks.
# ReportLab's core fonts (Helvetica etc.) have no glyphs for these — they
# render as a "■" tofu box instead of the intended ✅ 💡 🟢 🟡 🔴 etc.
# Stripped entirely rather than swapped for a fallback glyph, since the
# surrounding text (e.g. "Answer:", "EASY QUESTIONS") already conveys the
# meaning without the icon.
_EMOJI_RE = re.compile(
    "["
    "\U0001F300-\U0001FAFF"   # misc symbols & pictographs, emoticons, transport, supplemental symbols
    "\U00002600-\U000027BF"   # misc symbols, dingbats
    "\U0001F1E6-\U0001F1FF"   # regional indicators (flag letters)
    "\U00002190-\U000021FF"   # arrows (some fonts lack these too)
    "\U0000FE0F"              # variation selector-16 (emoji presentation)
    "]+",
    flags=re.UNICODE,
)


def _strip_unsupported_glyphs(text: str) -> str:
    """Remove emoji/pictographic characters the PDF font can't render."""
    return _EMOJI_RE.sub("", text)


def _clean(line: str) -> str:
    """
    Convert basic markdown to ReportLab-compatible pseudo-XML fragments.

    Strips glyphs the PDF font can't render, escapes raw XML-special
    characters, then layers real <b>/<i>/<font>/<a> tags on top — so
    arbitrary AI-generated text can never produce malformed/unclosed tags
    or "■" tofu boxes.
    """
    line = _strip_unsupported_glyphs(line)
    line = _escape_xml(line)
    line = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', line)
    line = re.sub(r'\*(.*?)\*',     r'<i>\1</i>', line)
    line = re.sub(r'`(.*?)`',       r'<font color="#6366f1">\1</font>', line)
    line = re.sub(
        r'\[([^\]]+)\]\(([^)]+)\)',
        r'<a href="\2"><font color="#6366f1">\1</font></a>',
        line
    )
    return line.strip()


def _safe_paragraph(text: str, style: ParagraphStyle) -> Paragraph:
    """
    Build a Paragraph, falling back to fully stripped plain text if the
    formatted version still fails to parse (e.g. overlapping/crossing
    markdown like "**bold *italic** text*"). Guarantees generate_pdf()
    never crashes on a single bad line — worst case, that line loses its
    bold/italic/link styling but the PDF still generates.
    """
    try:
        return Paragraph(text, style)
    except Exception:
        plain = re.sub(r'<[^>]+>', '', text)
        try:
            return Paragraph(plain, style)
        except Exception:
            return Paragraph("[content omitted — formatting error]", style)


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

    story = [_safe_paragraph(_escape_xml(_strip_unsupported_glyphs(title)), _TITLE)]
    if subtitle:
        story.append(_safe_paragraph(_escape_xml(_strip_unsupported_glyphs(subtitle)), _META))
    story.append(HRFlowable(width="100%", thickness=1, color=_PRIMARY, spaceAfter=10))

    for raw_line in text.split("\n"):
        line = raw_line.rstrip()

        if line.startswith("## "):
            story.append(_safe_paragraph(_clean(line[3:]), _H2))
        elif line.startswith("### "):
            story.append(_safe_paragraph(_clean(line[4:]), _H3))
        elif line.startswith("# "):
            story.append(_safe_paragraph(_clean(line[2:]), _H2))
        elif line.strip().startswith("- ") or line.strip().startswith("* "):
            story.append(_safe_paragraph(_clean(line.strip()[2:]), _BULLET))
        elif line.strip() == "":
            story.append(Spacer(1, 5))
        else:
            story.append(_safe_paragraph(_clean(line), _BODY))

    doc.build(story)
    return buf.getvalue()