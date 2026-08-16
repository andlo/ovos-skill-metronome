"""Shared pytest fixtures for the metronome skill test suite."""
import importlib.util
import sys
import threading
from pathlib import Path
from unittest.mock import MagicMock

import pytest

_INIT_PATH = Path(__file__).resolve().parents[1] / "__init__.py"
_spec = importlib.util.spec_from_file_location("metronome_skill", _INIT_PATH)
_module = importlib.util.module_from_spec(_spec)
sys.modules["metronome_skill"] = _module
_spec.loader.exec_module(_module)

Metronome = _module.Metronome


@pytest.fixture
def skill(monkeypatch):
    s = Metronome.__new__(Metronome)
    s.log = MagicMock()
    s.skill_id = "ovos-skill-metronome.test"
    s.status = MagicMock()
    s._bus = MagicMock()
    monkeypatch.setattr(Metronome, "lang", "en-us", raising=False)
    s.res_dir = str(Path(__file__).resolve().parents[1])
    s._lang_resources = {}
    s._stop_event = threading.Event()
    s._thread = None
    s._last_bpm = None
    yield s
    s._stop()  # always clean up any thread a test may have started
