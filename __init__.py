"""
skill OVOS Metronome
Copyright (C) 2026  Andreas Lorensen

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

---

A metronome - fully deterministic, no cloud dependency, no external
audio samples. The two click sounds (sounds/accent.wav, a higher-
pitched downbeat, and sounds/click.wav, a lower-pitched regular beat)
are short generated sine-wave bursts with an exponential-decay
envelope (see scripts/generate_clicks.py) - not recordings, so there's
nothing to source, license, or credit.

TIMING
------
Runs in a background thread (_click_loop) that plays a click, then
sleeps until the NEXT scheduled beat time (computed from a fixed
`next_time` accumulator, not just "sleep 60/bpm every iteration") -
this avoids drift from the small overhead of each play_audio() call
accumulating over a long session. If a beat is ever late (the accumulator
falls behind wall-clock time - can happen on slow calls), the loop
resyncs to the current time rather than firing a burst of
back-to-back catch-up clicks.

Only one metronome runs at a time per skill instance - starting a new
tempo stops any existing one first. A daemon thread is used so the
skill shuts down cleanly even if stop() isn't called for any reason.
"""

import threading
import time
from pathlib import Path

from ovos_workshop.skills import OVOSSkill
from ovos_workshop.decorators import intent_handler
from ovos_number_parser import extract_number

SOUNDS_DIR = Path(__file__).resolve().parent / "sounds"
ACCENT_SOUND = str(SOUNDS_DIR / "accent.wav")
CLICK_SOUND = str(SOUNDS_DIR / "click.wav")

DEFAULT_BPM = 120
MIN_BPM = 20
MAX_BPM = 300
BEATS_PER_MEASURE = 4  # accent every 4th beat - fixed for now, see README


class Metronome(OVOSSkill):

    def initialize(self):
        self._stop_event = threading.Event()
        self._thread = None
        self._last_bpm = None  # remembered so bare "start the metronome" can resume it

    def _click_loop(self, bpm, beats_per_measure, message=None):
        # `message` (the utterance that started the metronome) is kept as
        # a positional argument on purpose: play_audio() finds its session
        # via dig_for_message(), which searches the call stack's
        # positional arguments for a Message. Without it every click
        # logged "No session context in message" and wasn't tied to the
        # session (e.g. a HiveMind client) that started the metronome.
        interval = 60.0 / bpm
        beat = 0
        next_time = time.monotonic()
        while not self._stop_event.is_set():
            sound = ACCENT_SOUND if beat % beats_per_measure == 0 else CLICK_SOUND
            self.play_audio(sound, instant=True)
            beat += 1
            next_time += interval
            sleep_time = next_time - time.monotonic()
            if sleep_time > 0:
                self._stop_event.wait(sleep_time)
            else:
                # fell behind (slow call, system hiccup, etc) - resync
                # rather than firing a burst of catch-up clicks
                next_time = time.monotonic()

    def _start(self, bpm, beats_per_measure=BEATS_PER_MEASURE, message=None):
        self._stop()
        self._last_bpm = bpm
        self._stop_event.clear()
        self._thread = threading.Thread(
            target=self._click_loop, args=(bpm, beats_per_measure, message), daemon=True)
        self._thread.start()

    def _stop(self):
        self._stop_event.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2)
        self._thread = None

    def _is_running(self):
        return self._thread is not None and self._thread.is_alive()

    def shutdown(self):
        self._stop()

    # Global "stop" support. ovos-core's stop pipeline asks every skill
    # can_stop() and calls stop() on those that say yes - without these,
    # plain "stop" never reached the metronome, only its own
    # "stop the metronome" intent did. ovos-workshop requires can_stop()
    # whenever stop() is implemented.
    def can_stop(self, message):
        return self._is_running()

    def stop(self):
        if not self._is_running():
            return False
        self._stop()
        return True

    @intent_handler("set_metronome.intent")
    def handle_set_metronome(self, message):
        bpm_raw = message.data.get("bpm")
        bpm = extract_number(bpm_raw, lang=self.lang) if bpm_raw else None
        if bpm is False or bpm is None:
            self.speak_dialog("bpm_not_understood")
            return
        bpm = int(round(bpm))
        if not (MIN_BPM <= bpm <= MAX_BPM):
            self.speak_dialog("bpm_out_of_range", {"min": MIN_BPM, "max": MAX_BPM})
            return
        self._start(bpm, message=message)
        self.speak_dialog("metronome_started", {"bpm": bpm})

    @intent_handler("start_metronome.intent")
    def handle_start_metronome(self, message):
        bpm = self._last_bpm or DEFAULT_BPM
        self._start(bpm, message=message)
        self.speak_dialog("metronome_started", {"bpm": bpm})

    @intent_handler("stop_metronome.intent")
    def handle_stop_metronome(self, message):
        if not self._is_running():
            self.speak_dialog("metronome_not_running")
            return
        self._stop()
        self.speak_dialog("metronome_stopped")
