# Why your speedometer needs calculus

Manim source for the Mathspace sample video. Scene numbers match the storyboard rows.

## Files

- `style.py`: palette, type sizes, layout positions, the car's motion, and the
  components every part reuses (road, car, clock, axes, `CurveTracker`,
  speedometer, `fraction`, `dotted`).
- `timeline.py`: times scenes to the narration. Scenes name words, not seconds.
- `narration/part2.txt`: the script text for part 2, used for estimated timing
  until there's a recording.
- `narration/transcript.txt`: the Descript transcript export, once you have one
  (not there yet).
- `part2_question.py`: part 2, one method per storyboard row.
- `renders/`: rendered clips.

## Rendering

    .venv/bin/manim -pql part2_question.py Part2                          # quick preview
    .venv/bin/manim -qh --fps 30 --save_sections part2_question.py Part2  # final, one clip per row

Per-row clips land in `media/videos/part2_question/1080p30/sections/`. No audio
is rendered; the voice goes on top in Descript.

## Timing to the voice

Every step in a scene is tied to words in the narration:

    self.row("2.5_not_a_straight_line", "We know that the car")   # new row/clip starts on these words
    self.at("couldn't possibly be a straight line", Create(line), run_time=1.5)
    self.span("a constant speed", "the entire duration", self.drive_to(10))

- `row(name, words)`: starts a storyboard row (a separate clip) when the words are spoken.
- `at(words, *animations, run_time=...)`: plays when the words start, at a fixed length.
- `span(start_words, end_words, *animations)`: stretched or squeezed to run from
  the start of the first phrase to the end of the second.
- `finish(words)`: holds until the last words are over.

Gaps between steps are filled automatically.

Where the times come from:

1. **No recording yet:** estimated from `narration/part2.txt` at 150 words per
   minute (`WORDS_PER_MINUTE` in `timeline.py`).
2. **After recording:** export the transcript from Descript with timecodes and
   save it as `narration/transcript.txt`. A timecode like `00:00:05` before some
   words means they start in second 5; words between two timecodes are spread
   evenly over that second. The transcript can cover the whole video: each part
   finds its own first sentence and starts its clip there (`LEAD_IN`, 0.6 s
   before the first word).

Re-render after adding or replacing the transcript; nothing in the scene files changes.
If you edit the script wording, update the cue phrases that no longer match;
the render stops with the phrase it couldn't find. If a step can't finish
before the next one's words, the render prints a warning naming it.

## Adding a part

    from style import *

    class Part3(LessonScene):
        SCRIPT = "narration/part3.txt"

        def construct(self):
            ...shared objects on self...
            self.row_3_1()

        def row_3_1(self):
            self.row("3.1_name", "first words of the row")
            self.at("some words", FadeIn(...))

## Palette

| Name | Hex | Used for |
| --- | --- | --- |
| BG | #F4EEE1 | cream background |
| PAPER | #EAE2D1 | panels, the speedometer face |
| INK | #2E2B27 | text, axes, the road |
| MUTED | #8E8676 | tick labels, axis titles, guides, rejected lines |
| CURVE | #3F6E8C | the car and everything that tracks it |
| AVG | #C65D3B | averages, gradients, the speedometer needle |
| WRONG | #B23A3A | contradictions |
| ACCENT | #6B8F4E | results |
| GOLD | #D9A23F | highlights |

## The motion

The car covers 250 m in 10 s: s(t) = 5t² for the first 5 s, then brakes
symmetrically, s(t) = 250 − 5(10 − t)². Part 4's numbers (80 m at 4 s,
84.05 m at 4.1 s) come from the same function.
