# Development

## Setup
```bash
git clone https://github.com/andlo/ovos-skill-metronome.git
cd ovos-skill-metronome
python3 -m venv .venv && source .venv/bin/activate
pip install -e .
pip install -r requirements-test.txt
```

## Running tests
```bash
pytest tests/ -v
```
These run real threads with real (short) `time.sleep()` calls, not
mocked timing - `test_metronome.py` starts an actual click loop at a
fast tempo (240-600 bpm) for a fraction of a second and checks the
real sequence of accent/regular clicks, not just the logic in
isolation.

## Regenerating the click sounds
```bash
python3 scripts/generate_clicks.py
```
Overwrites `sounds/accent.wav` and `sounds/click.wav`. Both are
generated sine-wave bursts with an exponential-decay envelope (see
the script) - no external source, nothing to license or credit.
Tweak frequency/duration/volume directly in the script if a different
click character is wanted.

## Adding time signature support

Currently fixed at 4/4 (`BEATS_PER_MEASURE` in `__init__.py`). To add
a real "set metronome to 3/4 time" feature:
1. Add an intent slot for the time signature (e.g. `{beats} {note_value}`).
2. Pass `beats_per_measure` through to `_start()` - the parameter
   already exists on `_click_loop()`/`_start()`, just not wired to an
   intent yet.
3. Decide what to do with the *note value* (the "4" in "3/4") -
   this skill doesn't currently distinguish 3/4 from 3/8 (both would
   just mean "accent every 3rd click"), which may or may not be
   correct depending on how literally you want time-signature
   semantics honored. Worth a second opinion before implementing.

## Versioning

`version.py` follows `VERSION_MAJOR.VERSION_MINOR.VERSION_BUILD[aVERSION_ALPHA]`.
Stays on **0.0.x** until time signature support (or a deliberate
decision not to add it) is settled.

## Releasing

Releases are tag-triggered (`v*`):
```bash
git add version.py
git commit -m "chore: bump version to 0.0.X"
git tag vX.Y.Z
git push && git push --tags
```
Triggers `.github/workflows/test.yml` then `.github/workflows/publish.yml`
(PyPI via trusted publishing - see `ovos-skill-convert`'s
DEVELOPMENT.md for the one-time PyPI setup needed before the first
tagged release).

## Style / conventions

- License: GPL-3.0-or-later (matches the other `andlo` skill repos).
- `locale/<lang-code>/` layout, `skill.json` inside each locale folder.
- Present design changes (new intents, timing behavior changes) for
  review before implementing - same process as `ovos-skill-convert`
  and `ovos-skill-sound-like`.
