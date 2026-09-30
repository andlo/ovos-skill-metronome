"""OCP: "start a metronome" is taken by the OCP pipeline before padatious,
so the skill answers OCP's search and plays via @ocp_play (#4)."""
import threading
from unittest.mock import MagicMock

import pytest
from ovos_utils.ocp import MediaType, PlaybackType

import metronome_skill as mt


@pytest.fixture(autouse=True)
def _no_entity_autoregister(monkeypatch):
    monkeypatch.setattr(mt.Metronome, "_auto_register_entity_files",
                        lambda *a, **k: None, raising=False)


@pytest.mark.parametrize("phrase,bpm", [
    ("a metronome", 120),
    ("the metronome at 90 bpm", 90),
    ("metronome 60 bpm", 60),
])
def test_search_answers_metronome(skill, phrase, bpm):
    [r] = skill.search_metronome(phrase, MediaType.MUSIC)
    assert r.uri == f"/{skill.skill_id}/{bpm}"
    assert r.match_confidence == 100 and r.playback == PlaybackType.SKILL
    assert r.media_type == MediaType.MUSIC


@pytest.mark.parametrize("phrase", [
    "metronome by some band",
    "the metronome at 900 bpm",
    "a rock beat",
    "",
])
def test_search_ignores_other_phrases(skill, phrase):
    assert skill.search_metronome(phrase, MediaType.MUSIC) == []


def test_search_danish(skill, monkeypatch):
    monkeypatch.setattr(mt.Metronome, "lang", "da-dk", raising=False)
    [r] = skill.search_metronome("en metronom på 80 bpm", MediaType.AUDIO)
    assert r.uri.endswith("/80")


def test_ocp_play_path_through_workshop(skill, monkeypatch):
    started = []
    monkeypatch.setattr(skill, "_start", lambda bpm, message=None: started.append(bpm))
    skill._playing, skill._paused = threading.Event(), threading.Event()
    skill._OVOSCommonPlaybackSkill__playback_handler = skill.play_metronome
    msg = MagicMock()
    msg.data = {"uri": f"/{skill.skill_id}/90"}
    skill._OVOSCommonPlaybackSkill__handle_ocp_play(msg)
    msg.data = {"uri": f"/{skill.skill_id}/9999"}
    skill.play_metronome(msg)
    assert started == [90, mt.MAX_BPM]
