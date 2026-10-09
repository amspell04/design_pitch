"""Deterministic tools for pitchy. The model decides content; this code renders it."""

import re
from datetime import date
from pathlib import Path
from xml.sax.saxutils import escape


import hashlib
from pathlib import Path

from google.genai import types
from PIL import Image as PILImage
from PIL import ImageStat

from PIL import Image as PILImage
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    HRFlowable,
    Image,
    KeepTogether,
    ListFlowable,
    ListItem,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

INPUT_DIR = Path(__file__).parent / "inputs"
_EXT = {"image/png": ".png", "image/jpeg": ".jpg", "image/webp": ".webp", "image/gif": ".gif"}

MIN_FULL_WIDTH_PX = 1200  # roughly 150 dpi across a letter-width page

OUTPUT_DIR = Path(__file__).parent / "output"

# doc_type -> (label shown on the cover, accent colour)
DOC_TYPES = {
    "pitch": ("Executive Pitch", colors.HexColor("#1F4E79")),
    "user_story": ("User Story", colors.HexColor("#2E7D5B")),
}

BLOCK_FIELDS = {
    "heading": {"text"},
    "paragraph": {"text"},
    "bullets": {"items"},
    "image": {"path"},
    "callout": {"text"},
}

PAGE_W, PAGE_H = LETTER
MARGIN = 0.9 * inch
FRAME_W = PAGE_W - 2 * MARGIN
MAX_IMG_H = 4.2 * inch


def _inline(text: str) -> str:
    """Escape text for ReportLab markup, then allow **bold** and *italic*."""
    out = escape(str(text))
    out = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", out)
    out = re.sub(r"(?<!\*)\*(?!\s)(.+?)(?<!\s)\*(?!\*)", r"<i>\1</i>", out)
    return out


def _styles(accent):
    body = ParagraphStyle("body", fontName="Helvetica", fontSize=10.5, leading=15, spaceAfter=8)
    return {
        "body": body,
        "h1": ParagraphStyle("h1", parent=body, fontName="Helvetica-Bold", fontSize=18, leading=22,
                             textColor=accent, spaceBefore=14, spaceAfter=8, keepWithNext=1),
        "h2": ParagraphStyle("h2", parent=body, fontName="Helvetica-Bold", fontSize=13, leading=17,
                             textColor=colors.HexColor("#333333"), spaceBefore=10, spaceAfter=6, keepWithNext=1),
        "caption": ParagraphStyle("caption", parent=body, fontName="Helvetica-Oblique", fontSize=9, leading=12,
                                  textColor=colors.HexColor("#666666"), alignment=TA_CENTER, spaceAfter=12),
        "callout": ParagraphStyle("callout", parent=body, fontSize=11, leading=16, spaceAfter=0),
        "callout_title": ParagraphStyle("callout_title", parent=body, fontName="Helvetica-Bold", fontSize=10,
                                        textColor=accent, spaceAfter=3),
        "cover_label": ParagraphStyle("cover_label", parent=body, fontName="Helvetica-Bold", fontSize=11,
                                      textColor=accent, spaceAfter=10),
        "cover_title": ParagraphStyle("cover_title", parent=body, fontName="Helvetica-Bold", fontSize=32,
                                      leading=38, spaceAfter=12),
        "cover_sub": ParagraphStyle("cover_sub", parent=body, fontSize=14, leading=20,
                                    textColor=colors.HexColor("#555555")),
        "meta": ParagraphStyle("meta", parent=body, fontSize=9, textColor=colors.HexColor("#888888")),
    }


def _validate(blocks) -> list[str]:
    """Return a list of human-readable problems; empty means the blocks are renderable."""
    if not isinstance(blocks, list) or not blocks:
        return ["blocks must be a non-empty list"]
    problems = []
    for i, b in enumerate(blocks):
        where = f"blocks[{i}]"
        if not isinstance(b, dict) or b.get("type") not in BLOCK_FIELDS:
            problems.append(f"{where}: needs a 'type' of {sorted(BLOCK_FIELDS)}")
            continue
        for field in BLOCK_FIELDS[b["type"]]:
            if not b.get(field):
                problems.append(f"{where} ({b['type']}): missing '{field}'")
        if b["type"] == "bullets" and not isinstance(b.get("items"), list):
            problems.append(f"{where} (bullets): 'items' must be a list of strings")
        if b["type"] == "image" and b.get("path") and not Path(b["path"]).expanduser().is_file():
            problems.append(f"{where} (image): file not found: {b['path']}")
    return problems


def _image(block, styles):
    path = Path(block["path"]).expanduser()
    with PILImage.open(path) as im:
        w, h = im.size
    scale = min(FRAME_W / w, MAX_IMG_H / h, 1.0)
    img = Image(str(path), width=w * scale, height=h * scale)
    parts = [img]
    if block.get("caption"):
        parts.append(Spacer(1, 4))
        parts.append(Paragraph(_inline(block["caption"]), styles["caption"]))
    else:
        parts.append(Spacer(1, 12))
    return KeepTogether(parts)


def _callout(block, styles, accent):
    inner = []
    if block.get("title"):
        inner.append(Paragraph(_inline(block["title"]), styles["callout_title"]))
    inner.append(Paragraph(_inline(block["text"]), styles["callout"]))
    table = Table([[inner]], colWidths=[FRAME_W])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F3F6F9")),
        ("LINEBEFORE", (0, 0), (0, -1), 3, accent),
        ("LEFTPADDING", (0, 0), (-1, -1), 12),
        ("RIGHTPADDING", (0, 0), (-1, -1), 12),
        ("TOPPADDING", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
    ]))
    return [table, Spacer(1, 12)]


def _flowables(block, styles, accent):
    kind = block["type"]
    if kind == "heading":
        style = styles["h2"] if block.get("level") == 2 else styles["h1"]
        return [Paragraph(_inline(block["text"]), style)]
    if kind == "paragraph":
        return [Paragraph(_inline(block["text"]), styles["body"])]
    if kind == "bullets":
        items = [ListItem(Paragraph(_inline(t), styles["body"]), leftIndent=14) for t in block["items"]]
        return [ListFlowable(items, bulletType="bullet", start="•", leftIndent=14, bulletColor=accent),
                Spacer(1, 6)]
    if kind == "image":
        return [_image(block, styles)]
    return _callout(block, styles, accent)


def build_pdf(
    title: str,
    doc_type: str,
    blocks: list[dict],
    output_name: str,
    subtitle: str = "",
    author: str = "",
) -> dict:
    """Render a branded PDF document from structured content blocks.

    Call this once the document content is final. Nothing is written if any block is invalid;
    the returned errors say what to fix, so correct them and call again.

    Args:
        title: Document title, shown on the cover page.
        doc_type: "pitch" for an executive pitch, or "user_story" for a user story document.
        blocks: Ordered content blocks. Each block is a dict with a "type":
            - {"type": "heading", "text": "...", "level": 1 or 2}  (level defaults to 1)
            - {"type": "paragraph", "text": "..."}   (**bold** and *italic* are supported)
            - {"type": "bullets", "items": ["...", "..."]}
            - {"type": "image", "path": "/path/to/file.png", "caption": "..."}  (caption optional;
              path must be an existing image file the user provided)
            - {"type": "callout", "text": "...", "title": "..."}  (title optional; use for the key
              message, the ask, or the story statement)
        output_name: File name for the PDF, without extension (e.g. "q3_brand_pitch").
        subtitle: Optional one-line subtitle for the cover page.
        author: Optional author or team name for the cover page.

    Returns:
        On success {"status": "ok", "path": str, "pages": int}.
        On failure {"status": "error", "errors": [str, ...]}.
    """
    if doc_type not in DOC_TYPES:
        return {"status": "error", "errors": [f"doc_type must be one of {sorted(DOC_TYPES)}"]}
    if not title or not title.strip():
        return {"status": "error", "errors": ["title is required"]}
    errors = _validate(blocks)
    if errors:
        return {"status": "error", "errors": errors}

    label, accent = DOC_TYPES[doc_type]
    styles = _styles(accent)
    stem = re.sub(r"[^A-Za-z0-9_-]+", "_", output_name.strip()).strip("_") or "document"
    OUTPUT_DIR.mkdir(exist_ok=True)
    out_path = OUTPUT_DIR / f"{stem}.pdf"

    story = [
        Spacer(1, 2.2 * inch),
        Paragraph(label.upper(), styles["cover_label"]),
        Paragraph(_inline(title), styles["cover_title"]),
        HRFlowable(width="30%", thickness=3, color=accent, hAlign="LEFT", spaceAfter=14),
    ]
    if subtitle:
        story.append(Paragraph(_inline(subtitle), styles["cover_sub"]))
    story.append(Spacer(1, 0.4 * inch))
    meta = " · ".join(p for p in (author, date.today().strftime("%B %d, %Y")) if p)
    story.append(Paragraph(escape(meta), styles["meta"]))
    story.append(PageBreak())
    for block in blocks:
        story.extend(_flowables(block, styles, accent))

    def footer(canvas, doc):
        canvas.saveState()
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(colors.HexColor("#888888"))
        canvas.drawString(MARGIN, 0.5 * inch, title[:80])
        canvas.drawRightString(PAGE_W - MARGIN, 0.5 * inch, str(doc.page))
        canvas.restoreState()

    doc = SimpleDocTemplate(
        str(out_path), pagesize=LETTER, leftMargin=MARGIN, rightMargin=MARGIN,
        topMargin=MARGIN, bottomMargin=MARGIN, title=title, author=author,
    )
    # Cover page has no footer; content pages do.
    doc.build(story, onFirstPage=lambda c, d: None, onLaterPages=footer)
    return {"status": "ok", "path": str(out_path), "pages": doc.page}


def image_info(path: str) -> dict:
    """Measure an image file. Use this alongside looking at the image when critiquing it.

    Gives exact facts a visual read can't: resolution, aspect ratio, brightness, contrast,
    dominant colours, and warnings about whether it will look sharp in a PDF.

    Args:
        path: Path to an image file the user provided.

    Returns:
        {"status": "ok", "width", "height", "format", "aspect_ratio", "file_kb", "brightness" (0-255),
        "contrast" (0-128, std dev of luminance), "dominant_colors": ["#rrggbb", ...],
        "warnings": [str, ...]} or {"status": "error", "errors": [str]}.
    """
    p = Path(path).expanduser()
    if not p.is_file():
        return {"status": "error", "errors": [f"file not found: {path}"]}
    try:
        with PILImage.open(p) as im:
            fmt, (w, h) = im.format, im.size
            rgb = im.convert("RGB")
    except Exception as e:  # unreadable or not an image
        return {"status": "error", "errors": [f"could not read image: {e}"]}

    stat = ImageStat.Stat(rgb.convert("L"))
    brightness, contrast = round(stat.mean[0]), round(stat.stddev[0])
    small = rgb.copy()
    small.thumbnail((200, 200))
    palette = small.quantize(colors=5).convert("RGB").getcolors(maxcolors=5) or []
    dominant = ["#%02x%02x%02x" % c for _, c in sorted(palette, reverse=True)]

    warnings = []
    if w < MIN_FULL_WIDTH_PX:
        warnings.append(f"{w}px wide: may look soft if shown full-width in a PDF (aim for {MIN_FULL_WIDTH_PX}px+)")
    if brightness < 40:
        warnings.append("very dark overall")
    elif brightness > 220:
        warnings.append("very bright overall; may wash out against the white page")
    if contrast < 25:
        warnings.append("low contrast; details may be hard to read")
    if max(w, h) / min(w, h) > 3:
        warnings.append("extreme aspect ratio; it will be scaled small to fit the page")

    return {
        "status": "ok", "width": w, "height": h, "format": fmt,
        "aspect_ratio": round(w / h, 2), "file_kb": round(p.stat().st_size / 1024),
        "brightness": brightness, "contrast": contrast,
        "dominant_colors": dominant, "warnings": warnings,
    }


def save_uploaded_images(callback_context, llm_request):
    """before_model_callback: write images attached in chat to disk and tell the model the path.

    A vision model sees attached images as raw bytes with no filename, but build_pdf and
    image_info need a path. The note is re-added on every request, so it stays in context.
    """
    INPUT_DIR.mkdir(exist_ok=True)
    for content in llm_request.contents:
        if content.role != "user":
            continue
        notes = []
        for part in content.parts or []:
            blob = part.inline_data
            if not blob or blob.mime_type not in _EXT or not blob.data:
                continue
            digest = hashlib.sha256(blob.data).hexdigest()[:12]
            path = INPUT_DIR / f"upload_{digest}{_EXT[blob.mime_type]}"
            if not path.exists():
                path.write_bytes(blob.data)
            note = f"[Attached image saved at {path}]"
            if not any(p.text == note for p in content.parts):
                notes.append(note)
        for note in notes:
            content.parts.append(types.Part(text=note))
    return None
