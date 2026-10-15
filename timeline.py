"""
Timing scenes to the narration.

Scenes don't contain durations. They say *which words* an animation belongs to:

    self.row("2.5_straight_line", "We know that the car")
    self.at("couldn't possibly be a straight line", Create(line), run_time=1.5)
    self.span("constant speed", "the entire duration", t.animate.set_value(10))

and the time of those words comes from one of two places:

1. A Descript transcript export (narration/transcript.txt), the text with a
   timecode like 00:00:05 in front of the words spoken from that second on.
   Words between two timecodes are spread evenly across that second.
2. If there is no transcript yet, the script text for the part
   (narration/partN.txt), timed at an estimated speaking rate.

So the same scene code renders against estimates today and against the real
recording later, with no edits. The render has no audio; the voice is laid
over the clips in Descript.

The scene's clock starts LEAD_IN seconds before its first spoken word, so a
transcript of the whole video works: each part finds its own first sentence.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from manim import config, logger

HERE = Path(__file__).parent

# Estimated speaking rate, used only when there is no recording yet.
WORDS_PER_MINUTE = 150
SENTENCE_PAUSE = 0.35   # extra seconds after . ? !
PARAGRAPH_PAUSE = 0.8   # extra seconds at a blank line

TIMECODE = re.compile(r"\[?(\d{1,2}):(\d{2}):(\d{2})(?:([.,:])(\d+))?\]?")
WORD = re.compile(r"[a-z0-9]+(?:[.'/][a-z0-9]+)*")


def tokens(text: str) -> list[str]:
    """Lower-case words with punctuation stripped; 'distance-time' -> 2 words."""
    return WORD.findall(text.lower().replace("’", "'"))


def spoken_weight(token: str) -> float:
    """Rough relative length of a token when read aloud."""
    if token == "m/s":
        return 3.0                       # "metres per second"
    if any(c.isdigit() for c in token):
        return 1.0 + 0.6 * len(token.replace(".", ""))  # "eighty four point zero five"
    return 1.0


@dataclass
class Word:
    text: str
    start: float
    end: float


class Narration:
    """A list of timed words with phrase lookup."""

    def __init__(self, words: list[Word], source: str):
        self.words = words
        self.source = source
        self._cursor = 0

    # ---- building ---------------------------------------------------------
    @classmethod
    def from_script(cls, path: Path) -> "Narration":
        sec_per_word = 60 / WORDS_PER_MINUTE
        words, t = [], 0.0
        for paragraph in re.split(r"\n\s*\n", path.read_text()):
            for sentence in re.split(r"(?<=[.?!])\s+", paragraph.strip()):
                for tok in tokens(sentence):
                    d = sec_per_word * spoken_weight(tok)
                    words.append(Word(tok, t, t + d))
                    t += d
                t += SENTENCE_PAUSE
            t += PARAGRAPH_PAUSE
        return cls(words, f"estimated from {path.name} at {WORDS_PER_MINUTE} wpm")

    @classmethod
    def from_descript(cls, path: Path) -> "Narration":
        text = path.read_text()
        marks = list(TIMECODE.finditer(text))
        if not marks:
            raise ValueError(f"No timecodes like 00:00:05 found in {path}")

        def seconds(m):
            h, mnt, s, sep, frac = m.groups()
            t = int(h) * 3600 + int(mnt) * 60 + int(s)
            if frac:
                t += int(frac) / 30 if sep == ":" else float(f"0.{frac}")  # frames or decimals
            return t

        words = []
        for i, m in enumerate(marks):
            t0 = seconds(m)
            chunk = tokens(text[m.end(): marks[i + 1].start() if i + 1 < len(marks) else len(text)])
            if not chunk:
                continue
            weights = [spoken_weight(w) for w in chunk]
            if i + 1 < len(marks):
                t1 = seconds(marks[i + 1])
            else:
                t1 = t0 + sum(weights) * 60 / WORDS_PER_MINUTE
            scale = (t1 - t0) / sum(weights)
            t = t0
            for w, wt in zip(chunk, weights):
                words.append(Word(w, t, t + wt * scale))
                t += wt * scale
        return cls(words, f"Descript transcript {path.name}")

    # ---- lookup -------------------------------------------------------------
    def find(self, phrase: str) -> tuple[int, int]:
        """Index range of the phrase's words, searching forward from the last match."""
        target = tokens(phrase)
        if not target:
            raise ValueError("Empty cue phrase")
        texts = [w.text for w in self.words]
        n = len(target)
        for begin in (self._cursor, 0):
            for i in range(begin, len(texts) - n + 1):
                if texts[i:i + n] == target:
                    self._cursor = i
                    return i, i + n - 1
        raise KeyError(
            f'Cue "{phrase}" not found in the narration ({self.source}). '
            "Check the wording matches the script or transcript."
        )

    def start_of(self, phrase: str) -> float:
        i, _ = self.find(phrase)
        return self.words[i].start

    def end_of(self, phrase: str) -> float:
        _, j = self.find(phrase)
        return self.words[j].end


def load_narration(script: str, transcript: str | None) -> Narration:
    if transcript and (HERE / transcript).exists():
        return Narration.from_descript(HERE / transcript)
    return Narration.from_script(HERE / script)


class TimedScene:
    """
    Mixin for scenes timed to narration. Set on the scene class:

        SCRIPT = "narration/part2.txt"            # required: this part's words
        TRANSCRIPT = "narration/transcript.txt"  # optional: Descript export
    """

    SCRIPT: str = ""
    TRANSCRIPT: str | None = "narration/transcript.txt"
    LEAD_IN = 0.6          # seconds of picture before the first word
    DEFAULT_RUN = 0.8      # run time for at() when none is given

    def setup_timeline(self):
        self.narration = load_narration(self.SCRIPT, self.TRANSCRIPT)
        first_words = " ".join(tokens(Path(HERE / self.SCRIPT).read_text())[:6])
        self._offset = self.narration.start_of(first_words) - self.LEAD_IN
        self._late = []
        logger.info(f"Timing from {self.narration.source}; scene starts at {self._offset:.2f} s")

    # ---- time ---------------------------------------------------------------
    @property
    def now(self) -> float:
        return self.renderer.time

    def when(self, cue, end: bool = False) -> float:
        """Scene time of a cue: a phrase (its start, or its end) or a number of seconds."""
        if isinstance(cue, (int, float)):
            return float(cue)
        t = self.narration.end_of(cue) if end else self.narration.start_of(cue)
        return t - self._offset

    def wait_until(self, cue, end: bool = False):
        target = self.when(cue, end)
        gap = target - self.now
        if gap > 1 / config.frame_rate:
            self.wait(gap)
        elif gap < -0.1:
            self._late.append((cue, -gap))

    # ---- the three things scenes use -------------------------------------------
    def row(self, name: str, first_words: str):
        """Start a storyboard row (a section, one clip with --save_sections) on its first words."""
        self.wait_until(first_words)
        self.next_section(name)

    def at(self, cue, *animations, run_time: float | None = None, **kwargs):
        """Play animations starting when the cue is spoken, at their own fixed length."""
        self.wait_until(cue)
        self.play(*animations, run_time=run_time or self.DEFAULT_RUN, **kwargs)

    def span(self, start_cue, end_cue, *animations, **kwargs):
        """Play animations stretched or squeezed to run from start_cue to the end of end_cue."""
        self.wait_until(start_cue)
        run_time = self.when(end_cue, end=True) - self.now
        if run_time < 0.3:
            self._late.append((end_cue, 0.3 - run_time))
            run_time = 0.3
        self.play(*animations, run_time=run_time, **kwargs)

    def finish(self, last_words: str, tail: float = 1.5):
        """Hold until the last words are over, plus a tail."""
        self.wait_until(self.when(last_words, end=True) + tail)
        for cue, by in self._late:
            logger.warning(f'Animation for "{cue}" started {by:.2f} s late; the previous step runs long.')
