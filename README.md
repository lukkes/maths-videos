# Animating maths videos with Claude and Manim
## Process

Provided a working setup of Descript, Manim and Claude (on Desktop):
- Create/generate the script for the video and polish
- Create/generate the storyboard for the video, giving each paragraph a description of what the animated visuals should do
- Record yourself narrating the script/use text-to-speech in a tool like Descript
- Export the transcript of your recording and hand that to Claude, asking it to write the Manim code that animates your storyboard and syncs the scene to the transcript
- Put everything together in Descript, polish as necessary, add captions
- Distribute

The output of the process is:
- The individual videos files
- The Manim source code including a shared style file that can be reused across videos.
- The git repo which can grow with every video
- Other MD files to act as instructions for the LLMs

## Files

- `style.py`: palette, type sizes, layout positions, the car's motion, and the
  components every part reuses (road, car, clock, axes, `CurveTracker`,
  speedometer, `fraction`, `dotted`).
- `timeline.py`: times scenes to the narration. Scenes name words, not seconds.
- `narration/part1.txt` to `narration/part6.txt`: the script text for each part,
  used for estimated timing until there's a recording.
- `narration/transcript.txt`: the Descript transcript export. Chapter headings in it
  (a line with --- under it) are ignored. Each clip ends where the next part starts in
  the recording, so the clips laid end to end from 0:00 line up with the audio.
- `part1_intro.py`: part 1 (rows 1.1 to 1.3) and the handoff into part 2.
- `part2_question.py`: part 2, one method per storyboard row.
- `part3_limits_of_old_maths.py`: part 3; opens on part 2's last frame.
- `part4a_windows.py`: part 4, rows 4.1 to 4.21 (speedometer to 10t + 5h).
- `part4b_limit.py`: part 4, rows 4.22 to 4.33 (two-sided limit to the power rule).
- `part5_twice.py`: part 5, rows 5.1, 5.2, 5.3, 5.6, 5.7, 5.9 (differentiating twice; the same stack of derivatives for an epidemic; 5.9 shows car, epidemic and wire side by side).
- `part6_next.py`: part 6, rows 6.1, 6.2, 6.4, 6.5 (next video, integration, end card).

Each part opens on the frame the previous part ends on. The end state is built by
one function (`GraphStage` in `style.py`, `part3_ending()`, `part4a_ending()`, `part4b_ending()`, `part5_ending()`), and
the next part calls the same function, so the frames always match.
- `renders/`: rendered clips.

## Rendering

    .venv/bin/manim -pql part1_intro.py Part1                             # quick preview
    .venv/bin/manim -qh --fps 30 --save_sections part1_intro.py Part1     # final, one clip per row
    .venv/bin/manim -qh --fps 30 --save_sections part2_question.py Part2
    .venv/bin/manim -qh --fps 30 --save_sections part3_limits_of_old_maths.py Part3
    .venv/bin/manim -qh --fps 30 --save_sections part4a_windows.py Part4a
    .venv/bin/manim -qh --fps 30 --save_sections part4b_limit.py Part4b
    .venv/bin/manim -qh --fps 30 --save_sections part5_twice.py Part5
    .venv/bin/manim -qh --fps 30 --save_sections part6_next.py Part6

Parts 4 to 6 use LaTeX for formulas. To render it on a Mac, install BasicTeX
(`brew install --cask basictex`), open a new terminal, then:

    sudo tlmgr update --self
    sudo tlmgr install standalone preview dvisvgm sansmath helvet

## Joining parts

Each part ends on the frame the next part starts on, so clips butt together
without a visible cut. Part 1 finishes its narration, then a short handoff
(section `1.4_handoff`, about 2.5 s, no narration) fades the graphs and grows
the small car into part 2's car on the road, with the clock at 0.0 s. Part 2
starts with that road, car and clock already on screen (`opening_layout()` in
`style.py` builds them for both). In Descript, leave a pause of about 2.5 s in
the voice between the two parts, or lay the handoff clip under the start of
part 2's first sentence.

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
