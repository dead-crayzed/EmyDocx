"""AppState — минимальный, но должен вести себя предсказуемо."""
from emydocx.config import DEFAULT_FILE_LABEL
from emydocx.state import AppState


def test_initial_state():
    s = AppState()
    assert s.current_path is None
    assert s.document_name == DEFAULT_FILE_LABEL


def test_set_document():
    s = AppState()
    s.set_document("/tmp/a.md", "a.md")
    assert s.current_path == "/tmp/a.md"
    assert s.document_name == "a.md"


def test_set_document_none_path():
    s = AppState()
    s.set_document(None, "New")
    assert s.current_path is None
    assert s.document_name == "New"


def test_reset():
    s = AppState()
    s.set_document("/tmp/a.md", "a.md")
    s.reset()
    assert s.current_path is None
    assert s.document_name == DEFAULT_FILE_LABEL