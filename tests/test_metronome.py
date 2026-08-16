"""Tests for the metronome's start/stop/bpm-validation logic and its
actual timing behavior (real threads, real time.sleep - these run for
real wall-clock fractions of a second, not mocked)."""
import time
from unittest.mock import MagicMock

import pytest


def test_start_and_stop(skill):
    skill.play_audio = MagicMock()
    skill._start(240)  # fast tempo so the test doesn't take long
    assert skill._is_running()
    time.sleep(0.15)
    skill._stop()
    assert not skill._is_running()
    assert skill.play_audio.call_count >= 1


def test_first_beat_is_accent(skill):
    skill.play_audio = MagicMock()
    skill._start(240)
    time.sleep(0.05)
    skill._stop()
    first_call_args = skill.play_audio.call_args_list[0]
    from metronome_skill import ACCENT_SOUND
    assert first_call_args[0][0] == ACCENT_SOUND


def test_fourth_beat_is_accent_again(skill):
    """BEATS_PER_MEASURE=4 - the 5th call overall (index 4, 0-based)
    should be the next accent."""
    skill.play_audio = MagicMock()
    skill._start(600)  # very fast so 5 beats happen quickly
    time.sleep(0.6)
    skill._stop()
    from metronome_skill import ACCENT_SOUND, CLICK_SOUND
    calls = [c[0][0] for c in skill.play_audio.call_args_list]
    assert len(calls) >= 5
    assert calls[0] == ACCENT_SOUND
    assert calls[1] == CLICK_SOUND
    assert calls[2] == CLICK_SOUND
    assert calls[3] == CLICK_SOUND
    assert calls[4] == ACCENT_SOUND


def test_starting_new_tempo_stops_old_one(skill):
    skill.play_audio = MagicMock()
    skill._start(240)
    first_thread = skill._thread
    skill._start(180)
    assert skill._thread is not first_thread
    assert skill._is_running()
    skill._stop()


def test_handle_set_metronome_valid_bpm(skill):
    skill.play_audio = MagicMock()
    skill.speak_dialog = MagicMock()
    message = MagicMock()
    message.data = {"bpm": "120"}
    skill.handle_set_metronome(message)
    assert skill._is_running()
    assert skill._last_bpm == 120
    skill.speak_dialog.assert_called_once_with("metronome_started", {"bpm": 120})


def test_handle_set_metronome_out_of_range(skill):
    skill.play_audio = MagicMock()
    skill.speak_dialog = MagicMock()
    message = MagicMock()
    message.data = {"bpm": "1000"}
    skill.handle_set_metronome(message)
    assert not skill._is_running()
    skill.speak_dialog.assert_called_once_with("bpm_out_of_range", {"min": 20, "max": 300})


def test_handle_set_metronome_unparseable_bpm(skill):
    skill.play_audio = MagicMock()
    skill.speak_dialog = MagicMock()
    message = MagicMock()
    message.data = {"bpm": "banana"}
    skill.handle_set_metronome(message)
    assert not skill._is_running()
    skill.speak_dialog.assert_called_once_with("bpm_not_understood")


def test_handle_start_metronome_uses_default_when_no_prior_tempo(skill):
    skill.play_audio = MagicMock()
    skill.speak_dialog = MagicMock()
    message = MagicMock()
    skill.handle_start_metronome(message)
    from metronome_skill import DEFAULT_BPM
    assert skill._last_bpm == DEFAULT_BPM
    skill.speak_dialog.assert_called_once_with("metronome_started", {"bpm": DEFAULT_BPM})


def test_handle_start_metronome_resumes_last_tempo(skill):
    skill.play_audio = MagicMock()
    skill.speak_dialog = MagicMock()
    skill._last_bpm = 90
    message = MagicMock()
    skill.handle_start_metronome(message)
    skill.speak_dialog.assert_called_once_with("metronome_started", {"bpm": 90})


def test_handle_stop_metronome_when_not_running(skill):
    skill.speak_dialog = MagicMock()
    message = MagicMock()
    skill.handle_stop_metronome(message)
    skill.speak_dialog.assert_called_once_with("metronome_not_running")


def test_handle_stop_metronome_when_running(skill):
    skill.play_audio = MagicMock()
    skill.speak_dialog = MagicMock()
    skill._start(240)
    message = MagicMock()
    skill.handle_stop_metronome(message)
    assert not skill._is_running()
    skill.speak_dialog.assert_called_once_with("metronome_stopped")


def test_sound_files_actually_exist(skill):
    from metronome_skill import ACCENT_SOUND, CLICK_SOUND
    from pathlib import Path
    assert Path(ACCENT_SOUND).exists()
    assert Path(CLICK_SOUND).exists()
