"""
Part 1 of the script: storyboard rows 1.1 to 1.3, then the handoff to part 2.

The last few seconds, after the narration ends, turn the screen into part 2's
opening frame (road, car at 0 m, clock at 0.0 s), so the two clips join
without a visible cut.

Preview:   manim -pql part1_intro.py Part1
Final:     manim -qh --fps 30 --save_sections part1_intro.py Part1
"""

from style import *

# Small "steady vs changing" graphs in row 1.3
PANEL_SIZE = (4.4, 2.6)
LEFT_PANEL = np.array([-3.5, -1.0, 0])
RIGHT_PANEL = np.array([3.5, -1.0, 0])
WINDOW = 0.8          # width of the sliding rise-over-run triangle, in graph units


class Part1(LessonScene):
    SCRIPT = "narration/part1.txt"
    NEXT_START = ('study "change"', 1.7)    # part 1 ends with the handoff, 1.7 s after this

    def construct(self):
        self.row_1_1()
        self.row_1_2()
        self.row_1_3()
        self.handoff_to_part2()

    # ------------------------------------------------------------------
    # 1.1  Title; calculus, then differentiation as part of it
    # ------------------------------------------------------------------
    def row_1_1(self):
        self.row("1.1_title", "In this video")
        self.title = txt("Why your speedometer needs calculus", 44, INK, MEDIUM).move_to(UP * 1.2)
        calculus = txt("calculus", 34, INK).move_to(DOWN * 0.3)
        diff = txt("differentiation", 28, AVG).next_to(calculus, DOWN, buff=0.7)
        link = Line(calculus.get_bottom() + DOWN * 0.1, diff.get_top() + UP * 0.1, color=MUTED, stroke_width=2)
        self.title_card = VGroup(self.title, calculus, link, diff)

        self.at("In this video", FadeIn(self.title, shift=UP * 0.15), run_time=1.0)
        self.at("introduce calculus", FadeIn(calculus))
        self.at("more specifically", Create(link), FadeIn(diff, shift=DOWN * 0.1))

    # ------------------------------------------------------------------
    # 1.2  "change"
    # ------------------------------------------------------------------
    def row_1_2(self):
        self.row("1.2_change", "After all")
        self.change = txt("change", 72, INK, slant=ITALIC)
        self.at("After all", FadeOut(self.title_card))
        self.at("the mathematics of change", FadeIn(self.change, scale=0.9), run_time=1.0)

    # ------------------------------------------------------------------
    # 1.3  Steady change we can handle; changing change we can't
    # ------------------------------------------------------------------
    def row_1_3(self):
        self.row("1.3_steady_vs_curved", "and there has to be")
        self.at("and there has to be", self.change.animate.scale(0.5).move_to(UP * 3.1))

        # left: a bath filling at a steady 2 litres a minute
        left_axes, left_labels = mini_axes(LEFT_PANEL, "time (min)", "water (L)", y_max=10)
        bath = left_axes.plot(lambda x: 2 * x, x_range=[0, 5], color=CURVE, stroke_width=4)
        left_caption = txt("a bath filling at a steady rate", SIZE_TICK, MUTED).next_to(left_labels, DOWN, buff=0.2)
        left_tri = rise_run_triangle(left_axes, lambda x: 2 * x, 2.6, 1.4)
        left_value = txt("2 L/min", SIZE_LABEL, AVG, BOLD).next_to(left_tri, RIGHT, buff=0.15)
        tick = tick_mark().next_to(left_value, RIGHT, buff=0.2)
        self.left = VGroup(left_axes, left_labels, bath, left_caption, left_tri, left_value, tick)

        self.at("a good reason",
                Create(left_axes), FadeIn(left_labels), Create(bath), FadeIn(left_caption), run_time=1.2)
        self.at("the maths we've learned", Create(left_tri), FadeIn(left_value), Create(tick))

        # right: a car pulling away; the gradient depends on where you look
        f = lambda x: 0.6 * x**2
        right_axes, right_labels = mini_axes(RIGHT_PANEL, "time (s)", "distance (m)", y_max=15)
        curve = right_axes.plot(f, x_range=[0, 5], color=CURVE, stroke_width=4)
        right_caption = txt("a car pulling away", SIZE_TICK, MUTED).next_to(right_labels, DOWN, buff=0.2)
        u = ValueTracker(0.4)
        tri = always_redraw(lambda: rise_run_triangle(right_axes, f, u.get_value(), WINDOW))
        value = always_redraw(lambda: num(
            f"{(f(u.get_value() + WINDOW) - f(u.get_value())) / WINDOW:.1f} m/s", SIZE_LABEL, AVG, BOLD
        ).next_to(right_axes.c2p(u.get_value() + WINDOW, f(u.get_value() + WINDOW)), RIGHT, buff=0.15))

        # the small car riding above the graph; it becomes part 2's car at the end
        mini_road_y = right_axes.c2p(0, 15)[1] + 0.35
        x0, x1 = right_axes.c2p(0, 0)[0], right_axes.c2p(5, 0)[0]
        self.mini_car = make_car().scale(0.55)
        self.mini_car.add_updater(lambda m: m.move_to(
            [interpolate(x0, x1, f(u.get_value()) / f(5)), mini_road_y, 0], aligned_edge=DOWN))
        self.mini_car.update()

        self.at("so far",
                Create(right_axes), FadeIn(right_labels), Create(curve), FadeIn(right_caption),
                FadeIn(self.mini_car), run_time=0.9)
        self.add(tri, value)
        self.span("enough", 'study "change"', u.animate.set_value(4.0), rate_func=smooth)
        question = txt("?", 48, AVG, BOLD).next_to(value, RIGHT, buff=0.2)
        self.play(FadeIn(question, scale=0.6), run_time=0.6)
        self.mini_car.clear_updaters()
        self.right = VGroup(right_axes, right_labels, curve, right_caption, tri, value, question)
        self.wait_until('study "change"', end=True)

    # ------------------------------------------------------------------
    # Handoff: end on part 2's first frame
    # ------------------------------------------------------------------
    def handoff_to_part2(self):
        self.next_section("1.4_handoff")
        t = ValueTracker(0)
        road, car, clock = opening_layout(t, Motion())
        target = car.copy().clear_updaters()
        k = max(self.clip_end() - self.now, 0.8) / 2.2     # fit the handoff into the time before part 2
        self.play(FadeOut(self.left), FadeOut(self.right), FadeOut(self.change), run_time=0.8 * k)
        self.play(Transform(self.mini_car, target), Create(road), FadeIn(clock), run_time=1.4 * k)
        self.remove(self.mini_car)
        self.add(car)
        self.finish('study "change"')


# ----------------------------------------------------------------------
# Helpers for the small graphs in 1.3
# ----------------------------------------------------------------------
def mini_axes(center, x_title, y_title, y_max):
    axes = Axes(x_range=[0, 5, 1], y_range=[0, y_max, y_max / 5],
                x_length=PANEL_SIZE[0], y_length=PANEL_SIZE[1], tips=False,
                axis_config={"color": INK, "stroke_width": 2, "include_numbers": False, "tick_size": 0.05})
    axes.move_to(center)
    labels = VGroup(
        txt(x_title, SIZE_TICK, MUTED).next_to(axes.x_axis, DOWN, buff=0.2),
        txt(y_title, SIZE_TICK, MUTED).next_to(axes.c2p(0, y_max), UP, buff=0.15).align_to(axes.c2p(0, 0), LEFT),
    )
    return axes, labels
