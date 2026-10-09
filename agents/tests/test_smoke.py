"""Smoke tests that need no model: renderer, image measurement, agent wiring."""

from PIL import Image

from pitchy.agent import root_agent
from pitchy.image_tools import image_info
from pitchy import tools


def _png(tmp_path, size=(1400, 800)):
    path = tmp_path / "mock.png"
    Image.new("RGB", size, "#d9e4f0").save(path)
    return str(path)


def test_agent_wiring():
    assert root_agent.name == "pitchy"
    assert len(root_agent.tools) == 3


def test_build_pdf_ok(tmp_path, monkeypatch):
    monkeypatch.setattr(tools, "OUTPUT_DIR", tmp_path)
    blocks = [
        {"type": "heading", "text": "Situation"},
        {"type": "paragraph", "text": "**Bold** & <odd> text"},
        {"type": "bullets", "items": ["a", "b"]},
        {"type": "image", "path": _png(tmp_path), "caption": "Mock"},
        {"type": "callout", "title": "Ask", "text": "Approve"},
    ]
    for doc_type in ("pitch", "user_story"):
        result = tools.build_pdf("Title", doc_type, blocks, f"out_{doc_type}")
        assert result["status"] == "ok", result
        assert (tmp_path / f"out_{doc_type}.pdf").stat().st_size > 1000


def test_build_pdf_rejects_bad_input(tmp_path, monkeypatch):
    monkeypatch.setattr(tools, "OUTPUT_DIR", tmp_path)
    result = tools.build_pdf("T", "pitch", [{"type": "image", "path": "/nope.png"}, {"type": "x"}], "bad")
    assert result["status"] == "error" and len(result["errors"]) == 2
    assert not list(tmp_path.glob("*.pdf"))
    assert tools.build_pdf("T", "slides", [{"type": "paragraph", "text": "x"}], "bad")["status"] == "error"


def test_image_info(tmp_path):
    info = image_info(_png(tmp_path))
    assert info["status"] == "ok" and (info["width"], info["height"]) == (1400, 800)
    assert image_info(_png(tmp_path, (300, 200)))["warnings"]
    assert image_info("/nope.png")["status"] == "error"
