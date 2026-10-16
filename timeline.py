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

from manim import config, logger, VMobject, DL, UR

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
                    if begin == 0 and self._cursor > 0:
                        logger.warning(f'Cue "{phrase}" found only before the previous cue; check the order.')
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
    # Where this part's clip starts and where the next part's clip starts. Either the first
    # words of the part (the clip starts LEAD_IN before them), or (phrase, seconds): that many
    # seconds after the phrase ends, for parts that hand over without a pause in the speech.
    START = None        # default: the first words of SCRIPT
    NEXT_START = None   # this clip ends where the next one begins; None for the last part
    LEAD_IN = 0.6          # seconds of picture before the first word
    DEFAULT_RUN = 0.8      # run time for at() when none is given

    def setup_timeline(self):
        self.narration = load_narration(self.SCRIPT, self.TRANSCRIPT)
        first_words = " ".join(tokens(Path(HERE / self.SCRIPT).read_text())[:6])
        # Clips placed back to back from 0:00 line up with the whole recording.
        self._offset = self.anchor(self.START or first_words)
        self._late = []
        self._offscreen = []
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

    # ---- off-screen check ----------------------------------------------------------
    def check_bounds(self, where: str):
        """Warn about anything visible that sticks out of the frame (text that clips, lines that overrun)."""
        frame = getattr(self.camera, "frame", None)
        cx, cy = (frame.get_center()[:2] if frame is not None else (0, 0))
        hw = (frame.width if frame is not None else config.frame_width) / 2 - 0.05
        hh = (frame.height if frame is not None else config.frame_height) / 2 - 0.05
        seen = set()
        for top in self.mobjects:
            for m in top.get_family():
                if not isinstance(m, VMobject) or m.get_num_points() == 0 or id(m) in seen:
                    continue
                if max(m.get_stroke_opacity(), m.get_fill_opacity()) < 0.05:
                    continue
                (x0, y0, _), (x1, y1, _) = m.get_critical_point(DL), m.get_critical_point(UR)
                if x0 < cx - hw or x1 > cx + hw or y0 < cy - hh or y1 > cy + hh:
                    seen.add(id(m))
                    name = getattr(m, "text", None) or getattr(m, "tex_string", None) or type(m).__name__
                    owner = getattr(top, "text", None) or getattr(top, "tex_string", None) or type(top).__name__
                    self._offscreen.append((where, str(name)[:40], str(owner)[:40]))

    # ---- the three things scenes use -------------------------------------------
    def row(self, name: str, first_words: str):
        """Start a storyboard row (a section, one clip with --save_sections) on its first words.

        The first row of a scene starts at frame 0, so its clip includes the lead-in
        instead of leaving it in a separate 'autocreated' clip.
        """
        if hasattr(self, "_current_row"):
            self.check_bounds(f"end of {self._current_row}")
        self._current_row = name
        if not getattr(self, "_first_row_done", False):
            self._first_row_done = True
            self.next_section(name)
            self.wait_until(first_words)
            return
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

    def anchor(self, spec) -> float:
        """Recording time where a clip starts, from a START / NEXT_START spec."""
        if isinstance(spec, tuple):
            phrase, delta = spec
            return self.narration.end_of(phrase) + delta
        return max(0.0, self.narration.start_of(spec) - self.LEAD_IN)

    def clip_end(self) -> float | None:
        """Scene time where the next part's clip starts, or None for the last part."""
        if not self.NEXT_START:
            return None
        return self.anchor(self.NEXT_START) - self._offset

    def finish(self, last_words: str, tail: float = 1.5):
        """Hold until the next part's clip starts (or, for the last part, the last words plus a tail)."""
        end = self.clip_end()
        if end is None:
            self.wait_until(self.when(last_words, end=True) + tail)
        else:
            if self.now > end + 0.05:
                logger.warning(f"This part runs {self.now - end:.2f} s past the start of the next part.")
            self.wait_until(end)
        self.check_bounds(f"end of {getattr(self, '_current_row', 'scene')}")
        reported = set()
        for where, name, owner in self._offscreen:
            if (name, owner) not in reported:
                reported.add((name, owner))
                logger.warning(f"OFFSCREEN at {where}: {name} (in {owner})")
        for cue, by in self._late:
            logger.warning(f'Animation for "{cue}" started {by:.2f} s late; the previous step runs long.')
