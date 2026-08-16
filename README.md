# <img src='icon.png' card_color='#DBA940' width='50' height='50' style='vertical-align:bottom'/> Metronome

A metronome for OVOS - set a tempo in beats per minute, get an
audible click track with an accented downbeat. Fully deterministic,
fully offline: the two click sounds are generated sine-wave bursts
(see `scripts/generate_clicks.py`), not recordings, so there's
nothing to source, license, or credit.

[![Tests](https://github.com/andlo/ovos-skill-metronome/actions/workflows/test.yml/badge.svg)](https://github.com/andlo/ovos-skill-metronome/actions/workflows/test.yml)
[![PyPI version](https://img.shields.io/pypi/v/ovos-skill-metronome.svg)](https://pypi.org/project/ovos-skill-metronome/)

> **Early 0.0.x release.** Fixed 4/4 time signature only - see
> "Not yet implemented" below.

## Usage
```
"set a metronome to 120 bpm"
"start a metronome"
"stop the metronome"
"sæt en metronom til 120 bpm"    (Danish)
"stop metronomen"                (Danish)
```

Saying "start a metronome" with no tempo resumes the last one used
this session, or 120 bpm if none has been set yet. Valid range is
20-300 bpm.

## Timing accuracy

Runs a background thread that computes each beat's *scheduled* time
from a fixed accumulator, rather than repeatedly sleeping
`60/bpm` seconds - this avoids the small overhead of each click
(`play_audio()` call, thread wake-up, etc) accumulating into
noticeable drift over a long session. If a beat ever comes in late,
the loop resyncs to wall-clock time rather than firing a burst of
back-to-back catch-up clicks.

## Not yet implemented

- **Time signature is fixed at 4/4** (accent every 4th beat). A
  "set the metronome to 3/4 time" waltz mode is a natural next
  addition - flagged here rather than built speculatively.
- No visual/GUI beat indicator, audio only.

## Install
```bash
pip install ovos-skill-metronome
```

## Development

See [DEVELOPMENT.md](DEVELOPMENT.md).

## Category
**Utility**

## Tags
#music #metronome #tempo #practice
