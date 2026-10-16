"""
Part 3 of the script: storyboard rows 3.1 to 3.7.

Opens on part 2's last frame (car at 4 s, the distance-time curve, the large
speedometer and its question mark), so the two clips join without a cut.

Preview:   manim -pql part3_limits_of_old_maths.py Part3
Final:     manim -qh --fps 30 --save_sections part3_limits_of_old_maths.py Part3
"""

from style import *

T_ASK = 4.0                          # the instant we ask about
PANEL_X = 4.2                        # centre of the right-hand panel
WINDOW = 0.8                         # width of the sliding triangle in 3.6


def other_car(t):
    """A second car: speeds up for 3 s, cruises at 30 m/s for 4 s, then brakes."""
    t = float(np.clip(t, 0, T_TOTAL))
    if t <= 3:
        return 5 * t**2
    if t <= 7:
        return 45 + 30 * (t - 3)
    return 165 + 30 * (t - 7) - 5 * (t - 7) ** 2


def naming_terms():
    """The three terms part 3 ends on (built here, reused by part 4a's opening)."""
    terms = VGroup(
        txt("calculus", SIZE_LABEL, INK, MEDIUM),
        txt("differential calculus", SIZE_LABEL, INK, MEDIUM),
        VGroup(txt("derivative", SIZE_LABEL, AVG, BOLD),
               txt("= rate of change at one moment", SIZE_TICK, INK)).arrange(DOWN, buff=0.12),
    ).arrange(DOWN, buff=0.4)
    return terms.move_to([PANEL_X, -1.0, 0])


def frozen_slider(axes):
    """The rise-over-run triangle where part 3 stops it, at t = 4."""
    return rise_run_triangle(axes, s, T_ASK, WINDOW)


def part3_ending():
    """Everything on screen at the end of part 3: (stage, slider, terms)."""
    stage = GraphStage(T_ASK)
    return stage, frozen_slider(stage.axes), naming_terms()


class Part3(LessonScene):
    SCRIPT = "narration/part3.txt"
    NEXT_START = "Going back to the car speedometer"

    def construct(self):
        self.restore_part2_ending()
        self.row_3_1()
        self.row_3_2()
        self.row_3_3()
        self.row_3_4()
        self.row_3_5()
        self.row_3_6()
        self.row_3_7()

    def restore_part2_ending(self):
        """Rebuild exactly what part 2 leaves on screen."""
        stage = GraphStage(T_ASK)
        self.t, self.motion = stage.t, stage.motion
        self.road, self.car, self.clock = stage.road, stage.car, stage.clock
        self.axes, self.axis_labels, self.tracker = stage.axes, stage.axis_labels, stage.tracker
        self.start_dot = labelled_dot(self.axes.c2p(0, 0), "")[0]
        self.end_dot = labelled_dot(self.axes.c2p(T_TOTAL, D_TOTAL), "")[0]
        self.speedo = make_speedometer(lambda: self.motion.speed(self.t.get_value()), **SPEEDO_LARGE)
        self.question = txt("?", SIZE_BIG, AVG, BOLD).next_to(self.speedo, LEFT, buff=0.35)
        self.add(*stage.base(), self.tracker.dot, self.tracker.guides,
                 self.start_dot, self.end_dot, self.speedo, self.question)

    def panel(self, mob, y):
        return mob.move_to([PANEL_X, y, 0])

    # ------------------------------------------------------------------
    # 3.1  Speed at t = 4 is rise over run
    # ------------------------------------------------------------------
    def row_3_1(self):
        self.row("3.1_speed_at_4", "What's the speed of the car")
        self.at("What's the speed of the car", FadeOut(self.speedo), FadeOut(self.question))
        self.rr = self.panel(fraction("rise", "run", SIZE_LABEL, MUTED), 1.0)
        self.at("rise over run", FadeIn(self.rr, shift=UP * 0.1))

    # ------------------------------------------------------------------
    # 3.2  Two choices of points, two different gradients
    # ------------------------------------------------------------------
    def pair(self, x1, x2, color):
        dots = VGroup(*[Dot(self.axes.c2p(x, s(x)), radius=0.08, color=color).set_z_index(4) for x in (x1, x2)])
        line = secant(self.axes, s, x1, x2, color)
        value = num(f"gradient = {gradient(s, x1, x2):.1f} m/s", SIZE_LABEL, color, MEDIUM)
        return dots, line, value

    def row_3_2(self):
        self.row("3.2_which_two_points", "But how can we choose")
        d1, l1, v1 = self.pair(2.0, 6.0, AVG)
        d2, l2, v2 = self.pair(3.5, 4.5, GOLD)
        self.panel(v1, 0.05)
        self.panel(v2, -0.6)
        self.at("If I choose these two points", FadeIn(d1, scale=0.6), Create(l1), FadeIn(v1), run_time=1.0)
        self.at("and if I choose these two points", FadeIn(d2, scale=0.6), Create(l2), FadeIn(v2), run_time=1.0)
        self.play(FadeOut(d1), FadeOut(l1), v1.animate.set_opacity(0.35), run_time=0.6)
        self.pair2 = (d2, l2, v2)
        self.v1 = v1

    # ------------------------------------------------------------------
    # 3.3  One point: zero over zero
    # ------------------------------------------------------------------
    def row_3_3(self):
        self.row("3.3_zero_over_zero", "Even worse")
        d2, l2, v2 = self.pair2
        half = ValueTracker(0.5)       # half-width of the window around t = 4

        def ends():
            h = half.get_value()
            return T_ASK - h, T_ASK + h

        live_dots = always_redraw(lambda: VGroup(*[
            Dot(self.axes.c2p(x, s(x)), radius=0.08, color=GOLD).set_z_index(4) for x in ends()]))
        live_line = always_redraw(lambda: secant(self.axes, s, *ends(), GOLD)
                                  if half.get_value() > 0.03 else VMobject())
        live_rise = always_redraw(lambda: num(
            f"rise = {s(ends()[1]) - s(ends()[0]):.2f} m", SIZE_LABEL, MUTED).move_to([PANEL_X, -1.35, 0]))
        live_run = always_redraw(lambda: num(
            f"run = {ends()[1] - ends()[0]:.2f} s", SIZE_LABEL, MUTED).move_to([PANEL_X, -1.85, 0]))

        self.remove(d2, l2)
        self.add(live_dots, live_line)
        self.at("Even worse", FadeOut(v2), FadeOut(self.v1), FadeIn(live_rise), FadeIn(live_run))
        self.span("if I choose a single point", "isn't useful anymore", half.animate.set_value(0), rate_func=smooth)

        zero = self.panel(fraction("0 m", "0 s", 40, WRONG, BOLD), -0.4)
        q = txt("= ?", 40, WRONG, BOLD).next_to(zero, RIGHT, buff=0.25)
        self.at("zero divided by zero", FadeOut(live_rise), FadeOut(live_run), FadeIn(zero), FadeIn(q))
        self.play(Wiggle(VGroup(zero, q), scale_value=1.08, rotation_angle=0.04 * TAU), run_time=0.7)
        self.old_graph = VGroup(live_dots, live_line, zero, q, self.rr, self.tracker.curve,
                                self.tracker.dot, self.start_dot, self.end_dot)

    # ------------------------------------------------------------------
    # 3.4  A car at constant speed
    # ------------------------------------------------------------------
    def row_3_4(self):
        self.row("3.4_constant_speed", "And it's worth noticing")
        self.remove(self.tracker.guides)
        self.at("And it's worth noticing", FadeOut(self.old_graph))
        self.other = self.axes.plot(other_car, x_range=[0, T_TOTAL], color=MUTED, stroke_width=4)
        self.straight_part = self.axes.plot(other_car, x_range=[3, 7], color=CURVE, stroke_width=6)
        label = txt("another car", SIZE_TICK, MUTED).next_to(self.axes.c2p(10, other_car(10)), RIGHT, buff=0.15)
        self.at("If we study this other car", Create(self.other), FadeIn(label), run_time=1.2)
        self.other_label = label

        frame = self.camera.frame
        frame.save_state()
        self.at("zoom in only on this part",
                Create(self.straight_part),
                frame.animate.set(width=6.2).move_to(self.axes.c2p(5, other_car(5))),
                run_time=1.6)

    # ------------------------------------------------------------------
    # 3.5  Any two points give the same answer
    # ------------------------------------------------------------------
    def row_3_5(self):
        self.row("3.5_any_two_points", "Rise over run becomes")
        small = SIZE_TICK * 0.55        # the camera is zoomed about 2.3x
        triangles = VGroup()
        for x1, x2 in [(3.3, 4.1), (4.4, 6.3), (5.6, 6.6)]:
            tri = rise_run_triangle(self.axes, other_car, x1, x2 - x1, AVG, 2)
            val = num(f"{gradient(other_car, x1, x2):.0f} m/s", small, AVG, MEDIUM)
            val.next_to(tri[1], RIGHT, buff=0.06)
            triangles.add(VGroup(tri, val))
        self.at("any two points", LaggedStart(*[Create(g[0]) for g in triangles], lag_ratio=0.4), run_time=1.6)
        self.at("the same answer", LaggedStart(*[FadeIn(g[1]) for g in triangles], lag_ratio=0.3), run_time=1.0)
        tick = tick_mark(0.16).next_to(triangles[-1], UR, buff=0.1)
        self.at("perfectly capable", Create(tick))
        self.constant_bits = VGroup(triangles, tick)

    # ------------------------------------------------------------------
    # 3.6  When the rate keeps changing, the answer depends on the points
    # ------------------------------------------------------------------
    def row_3_6(self):
        self.row("3.6_rate_keeps_changing", "The trouble starts")
        self.at("The trouble starts",
                Restore(self.camera.frame),
                FadeOut(self.constant_bits), FadeOut(self.other), FadeOut(self.straight_part),
                FadeOut(self.other_label), FadeIn(self.tracker.curve), run_time=1.2)

        self.u = ValueTracker(0.5)
        self.slider = always_redraw(lambda: rise_run_triangle(self.axes, s, self.u.get_value(), WINDOW))
        self.slider_value = always_redraw(lambda: num(
            f"{gradient(s, self.u.get_value(), self.u.get_value() + WINDOW):.1f} m/s", SIZE_LABEL, AVG, BOLD
        ).move_to([PANEL_X, 0.4, 0]))
        self.add(self.slider, self.slider_value)
        self.span("rate of change itself", "which two points we pick", self.u.animate.set_value(T_ASK),
                  rate_func=smooth)

    # ------------------------------------------------------------------
    # 3.7  Naming it: differential calculus, derivative
    # ------------------------------------------------------------------
    def row_3_7(self):
        self.row("3.7_naming_it", "This is precisely the problem")
        self.slider.clear_updaters()
        self.slider_value.clear_updaters()
        terms = naming_terms()
        self.at("calculus was invented", FadeOut(self.slider_value), FadeIn(terms[0], shift=UP * 0.1))
        self.at("differential calculus", FadeIn(terms[1], shift=UP * 0.1))
        self.at("is called a derivative", FadeIn(terms[2], shift=UP * 0.1))
        underline = Line(terms[2][0].get_corner(DL) + DOWN * 0.08, terms[2][0].get_corner(DR) + DOWN * 0.08,
                         color=GOLD, stroke_width=5)
        self.play(ShowPassingFlash(underline, time_width=0.9), run_time=0.8)   # the key word, underlined once
        self.finish("called a derivative")
