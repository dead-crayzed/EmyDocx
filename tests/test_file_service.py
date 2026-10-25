"""FileService с замоканным FilePicker."""
import asyncio
from types import SimpleNamespace

import pytest

from emydocx.services.file_service import FileService


class FakePicker:
    """Простой фейк вместо ft.FilePicker."""

    def __init__(self, pick_result=None, save_result=None):
        self.pick_result = pick_result
        self.save_result = save_result
        self.pick_calls = []
        self.save_calls = []

    async def pick_files(self, **kwargs):
        self.pick_calls.append(kwargs)
        return self.pick_result

    async def save_file(self, **kwargs):
        self.save_calls.append(kwargs)
        return self.save_result


class TestOpenMarkdown:
    def test_returns_none_when_cancelled(self):
        picker = FakePicker(pick_result=[])
        service = FileService(picker)
        assert asyncio.run(service.open_markdown()) is None

    def test_reads_bytes(self):
        picker = FakePicker(pick_result=[
            SimpleNamespace(name="a.md", bytes=b"# hi", path=None),
        ])
        service = FileService(picker)
        result = asyncio.run(service.open_markdown())
        assert result.name == "a.md"
        assert result.content == "# hi"
        assert result.path is None

    def test_reads_from_path(self, tmp_path):
        f = tmp_path / "doc.md"
        f.write_text("# hello", encoding="utf-8")
        picker = FakePicker(pick_result=[
            SimpleNamespace(name="doc.md", bytes=None, path=str(f)),
        ])
        service = FileService(picker)
        result = asyncio.run(service.open_markdown())
        assert result.content == "# hello"
        assert result.path == str(f)

    def test_raises_when_no_content(self):
        picker = FakePicker(pick_result=[
            SimpleNamespace(name="x.md", bytes=None, path=None),
        ])
        service = FileService(picker)
        with pytest.raises(RuntimeError):
            asyncio.run(service.open_markdown())

    def test_utf8_bom_stripped(self, tmp_path):
        f = tmp_path / "bom.md"
        f.write_bytes(b"\xef\xbb\xbf# bom")
        picker = FakePicker(pick_result=[
            SimpleNamespace(name="bom.md", bytes=None, path=str(f)),
        ])
        service = FileService(picker)
        assert asyncio.run(service.open_markdown()).content == "# bom"


class TestSaveMarkdown:
    def test_returns_path(self):
        picker = FakePicker(save_result="/out/doc.md")
        service = FileService(picker)
        result = asyncio.run(service.save_markdown("# x", "doc.md"))
        assert result == "/out/doc.md"

    def test_passes_encoded_bytes(self):
        picker = FakePicker(save_result="/out/doc.md")
        service = FileService(picker)
        asyncio.run(service.save_markdown("# Текст", "doc.md"))
        assert picker.save_calls[0]["src_bytes"] == "# Текст".encode("utf-8")

    def test_none_content_becomes_empty(self):
        picker = FakePicker(save_result="/out/doc.md")
        service = FileService(picker)
        asyncio.run(service.save_markdown(None, "doc.md"))
        assert picker.save_calls[0]["src_bytes"] == b""


class TestExportDocx:
    def test_returns_path(self):
        picker = FakePicker(save_result="/out/doc.docx")
        service = FileService(picker)
        result = asyncio.run(service.export_docx(b"PK..", "doc.docx"))
        assert result == "/out/doc.docx"

    def test_passes_bytes_untouched(self):
        picker = FakePicker(save_result="/out/doc.docx")
        service = FileService(picker)
        asyncio.run(service.export_docx(b"PK\x03\x04stuff", "doc.docx"))
        assert picker.save_calls[0]["src_bytes"] == b"PK\x03\x04stuff"