"""Image helpers: measurable facts about images, and saving chat uploads to disk."""

import hashlib
from pathlib import Path

from google.genai import types
from PIL import Image as PILImage
from PIL import ImageStat

INPUT_DIR = Path(__file__).parent / "inputs"
_EXT = {"image/png": ".png", "image/jpeg": ".jpg", "image/webp": ".webp", "image/gif": ".gif"}

MIN_FULL_WIDTH_PX = 1200  # roughly 150 dpi across a letter-width page


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
