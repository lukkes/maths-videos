"""
Part 4a: storyboard rows 4.1 to 4.21. From the speedometer to 10t + 5h.

Opens on part 3's last frame and ends on the frame part 4b starts on; both
frames are built by functions in this file and in part 3, so they match.

On-screen text is limited to numbers, formulas and the words bolded in the
storyboard (secant, postpone, binomial expansion).

Preview:   manim -pql part4a_windows.py Part4a
Final:     manim -qh --fps 30 --save_sections part4a_windows.py Part4a
"""

from types import SimpleNamespace

from style import *
from part3_limits_of_old_maths import part3_ending

T0 = 4.0                               # the instant we're after
F = five_t_squared                     # part 4 works with the formula
PANEL_X = 3.2                          # centre of the right-hand panel (close-up graph ends at x = -1.1)
RESULT_Y, SUB_Y = 1.0, 0.15            # 10t + 5h box, and the t = 4 lines under it
TABLE_TOP = np.array([1.0, -0.6, 0])   # top-left of the value table
COL_W = 1.55
WIDE_H = 2.0                           # a window wide enough for the tilt to show
WORK_H = 1.2                           # window width used while doing the algebra


# ----------------------------------------------------------------------
# Builders shared with part 4b (its opening is this part's ending)
# ----------------------------------------------------------------------
def point_a(zaxes):
    return Dot(zaxes.c2p(T0, F(T0)), radius=0.09, color=CURVE).set_z_index(6)


def result_box():
    """10t + 5h, boxed."""
    expr = tex("10t", "+", "5h").move_to([PANEL_X, RESULT_Y, 0])
    box = SurroundingRectangle(expr, color=AVG, buff=0.14, stroke_width=2.5)
    return expr, box


def sub_line():
    """The result at t = 4."""
    return tex("40", "+", "5h", color=AVG).move_to([PANEL_X + 1.3, SUB_Y, 0])


def after_table():
    return ValueTable(["h (s)", "after"], col_colors=[INK, AVG], top_left=TABLE_TOP + RIGHT * COL_W,
                      col_width=COL_W)


AFTER_ROWS = [("0.1", "40.5"), ("0.01", "40.05"), ("0.001", "40.005")]


def part4a_ending():
    """Everything on screen at the end of part 4a."""
    stage = GraphStage(T0)
    zaxes, zlabels, zcurve = make_zoomed_axes()
    h = ValueTracker(0.001)
    secants = WindowSecants(zaxes, F, T0, h, sides=(+1,))
    expr, box = result_box()
    expr[0].set_color(CURVE)          # as recoloured in 4.20
    expr[2].set_color(AVG)
    table = after_table()
    for row in AFTER_ROWS:
        table.rows.append(table.make_row(row))
    return SimpleNamespace(stage=stage, zaxes=zaxes, zlabels=zlabels, zcurve=zcurve, a=point_a(zaxes),
                           h=h, secants=secants, expr=expr, box=box, sub=sub_line(), table=table)


class Part4a(LessonScene):
    SCRIPT = "narration/part4a.txt"
    NEXT_START = "Now, the curious among us"

    def construct(self):
        self.restore_part3_ending()
        for row in (self.row_4_1, self.row_4_2, self.row_4_3, self.row_4_4, self.row_4_5, self.row_4_6,
                    self.row_4_7, self.row_4_8, self.row_4_9, self.row_4_10, self.row_4_11, self.row_4_12,
                    self.row_4_13, self.row_4_14, self.row_4_15, self.row_4_16, self.row_4_17, self.row_4_18,
                    self.row_4_19, self.row_4_20, self.row_4_21):
            row()

    def restore_part3_ending(self):
        stage, slider, terms = part3_ending()
        self.stage, self.slider, self.terms = stage, slider, terms
        self.add(*stage.base(), slider, terms)

    def at_panel(self, mob, y, dx=0.0):
        return mob.move_to([PANEL_X + dx, y, 0])

    # ------------------------------------------------------------------
    # 4.1  Back to the speedometer
    # ------------------------------------------------------------------
    def row_4_1(self):
        self.row("4.1_back_to_speedometer", "Going back to the car speedometer")
        st = self.stage
        self.speedo = make_speedometer(lambda: st.motion.speed(st.t.get_value()), **SPEEDO_LARGE)
        self.at("Going back to the car speedometer", FadeOut(self.terms), FadeOut(self.slider),
                FadeIn(self.speedo, scale=0.9), run_time=1.0)

    # ------------------------------------------------------------------
    # 4.2  A turning wheel and a rising turn count
    # ------------------------------------------------------------------
    def row_4_2(self):
        self.row("4.2_wheel", "After all, most speedometers")
        centre = np.array([3.4, -0.6, 0])
        angle = ValueTracker(0)

        def wheel():
            a = angle.get_value()
            rim = Circle(radius=1.0, color=INK, stroke_width=5).move_to(centre)
            spokes = VGroup(*[Line(centre, centre + np.array([np.cos(a + k * PI / 3), np.sin(a + k * PI / 3), 0]),
                                   color=MUTED, stroke_width=2.5) for k in range(6)])
            mark = Dot(centre + np.array([np.cos(a), np.sin(a), 0]), radius=0.1, color=AVG)
            return VGroup(rim, spokes, mark)

        live_wheel = always_redraw(wheel)
        count = always_redraw(lambda: num(f"{int(angle.get_value() // TAU)}", SIZE_BIG, AVG, BOLD)
                              .next_to(centre, RIGHT, buff=1.6))
        self.cutaway = VGroup(live_wheel, count)
        self.at("After all, most speedometers", FadeOut(self.speedo))
        self.at("they receive data from sensors", FadeIn(live_wheel), FadeIn(count))
        self.span("which measure how many times", "in a short window of time", angle.animate.set_value(5 * TAU + 0.5),
                  rate_func=linear)

    # ------------------------------------------------------------------
    # 4.3  Close-up of the graph; a point a tenth of a second later (magnified)
    # ------------------------------------------------------------------
    def row_4_3(self):
        self.row("4.3_tenth_later", "So with our t equals four seconds")
        st = self.stage
        self.zaxes, self.zlabels, self.zcurve = make_zoomed_axes()
        self.a = point_a(self.zaxes)
        self.h = ValueTracker(0.1)
        self.secants = WindowSecants(self.zaxes, F, T0, self.h, sides=(+1,))
        self.bracket = always_redraw(lambda: window_bracket(self.zaxes, T0, T0 + self.h.get_value()))
        self.bracket_label = always_redraw(lambda: num(f"{self.h.get_value():.2f} s", SIZE_TICK, AVG, MEDIUM)
                                           .next_to(self.bracket, UP, buff=0.08))
        # magnifier: 4 s and 4.1 s are too close on the full graph to read
        self.mag = Magnifier(self.zaxes, F, x_range=(3.94, 4.2), y_range=(77.5, 87.5),
                             center=[PANEL_X - 0.9, -1.35, 0], size=2.6)
        self.mag_a = Dot(self.mag.point(T0), radius=0.1, color=CURVE).set_z_index(6)
        self.mag_b = self.mag.live_dot(lambda: T0 + self.h.get_value(), AVG, radius=0.1)
        self.at("So with our t equals four seconds",
                FadeOut(self.cutaway),
                FadeOut(VGroup(st.axes, st.axis_labels, st.tracker.curve)),
                FadeIn(VGroup(self.zaxes, self.zlabels, self.zcurve)), run_time=1.2)
        self.at("point set", FadeIn(self.a, scale=0.6), self.mag.show(), run_time=1.0)
        self.play(FadeIn(self.mag_a, scale=0.6), run_time=0.4)
        self.at("a 10th of a second later", FadeIn(self.secants.dots), FadeIn(self.mag_b),
                FadeIn(self.bracket), FadeIn(self.bracket_label))

    # ------------------------------------------------------------------
    # 4.4  80 m and 84.05 m (in the magnifier)
    # ------------------------------------------------------------------
    def row_4_4(self):
        self.row("4.4_two_distances", "Suppose the car has traveled")
        mag = self.mag
        b_x = T0 + 0.1
        label_a = num("80 m", SIZE_TICK, CURVE, MEDIUM).next_to(self.mag_a, DR, buff=0.08)
        label_b = num("84.05 m", SIZE_TICK, AVG, MEDIUM).next_to(mag.point(b_x), UL, buff=0.08)
        rise = Line(mag.inner.c2p(b_x, F(T0)), mag.point(b_x), color=AVG, stroke_width=3)
        run = DashedLine(mag.point(T0), mag.inner.c2p(b_x, F(T0)), color=AVG, stroke_width=2)
        self.rise_label = num("4.05 m", SIZE_TICK, AVG, MEDIUM).next_to(rise, RIGHT, buff=0.1)
        self.numbers_on_graph = VGroup(label_a, label_b, rise, run, self.rise_label)
        self.at("80 meters by the first point", FadeIn(label_a))
        self.at("84.05 meters by the second", FadeIn(label_b))
        self.play(Create(run), Create(rise), FadeIn(self.rise_label), run_time=0.6)

    # ------------------------------------------------------------------
    # 4.5  4.05 / 0.1 = 40.5
    # ------------------------------------------------------------------
    def row_4_5(self):
        self.row("4.5_rise_over_run", "Rise over run gives us")
        frac = tex_frac([r"4.05\,\text{m}"], [r"0.1\,\text{s}"])
        rest = tex(r"=", r"40.5\ \text{m/s}")
        rest[1].set_color(AVG)
        self.fraction = self.at_panel(VGroup(frac, rest).arrange(RIGHT, buff=0.2), 0.7)
        self.at("4.05 meters divided by 0.1 seconds",
                TransformFromCopy(self.rise_label, frac[0]), TransformFromCopy(self.bracket_label, frac[2]),
                Create(frac[1]), run_time=1.0)
        self.at("which is 40.5", FadeIn(rest, shift=LEFT * 0.15))

    # ------------------------------------------------------------------
    # 4.6  The secant (word shown briefly)
    # ------------------------------------------------------------------
    def row_4_6(self):
        self.row("4.6_secant", "The straight line through these two points")
        mag = self.mag
        self.mag_secant = always_redraw(lambda: DashedLine(
            mag.point(T0) + (mag.point(T0) - mag.point(T0 + self.h.get_value())) * 0,
            mag.point(T0 + self.h.get_value()), color=AVG, stroke_width=3, dash_length=0.07).set_z_index(5)
            .scale(1.6))
        word = txt("secant", SIZE_LABEL + 4, AVG, BOLD).move_to(self.zaxes.c2p(1.5, 150))
        icon_c = Circle(radius=0.32, color=MUTED, stroke_width=2).next_to(word, RIGHT, buff=0.3)
        p, q = icon_c.point_at_angle(2.6), icon_c.point_at_angle(-0.5)
        icon_l = DashedLine(p + (p - q) * 0.3, q + (q - p) * 0.3, color=AVG, stroke_width=2.5, dash_length=0.06)
        self.at("these two points", Create(self.secants.lines), Create(self.mag_secant), run_time=1.0)
        self.at("is called a secant", FadeIn(word, scale=0.9))
        self.at("circle geometry", FadeIn(VGroup(icon_c, icon_l)))
        self.at("its gradient is the average speed", FadeOut(VGroup(word, icon_c, icon_l)),
                Indicate(self.fraction[1][1], color=AVG))

    # ------------------------------------------------------------------
    # 4.7  Better than 25, still an average; a hundredth gives 40.05
    # ------------------------------------------------------------------
    def row_4_7(self):
        self.row("4.7_still_an_average", "This works just like the speedometer")
        trip = num("25 m/s", SIZE_LABEL, MUTED).next_to(self.fraction, RIGHT, buff=0.5)
        trip_strike = strike(trip, MUTED, 3)
        self.at("a much better answer", FadeOut(self.numbers_on_graph), FadeIn(trip))
        self.at("it's still an average", Create(trip_strike))
        self.readout = always_redraw(lambda: num(f"{self.secants.value(+1):.2f} m/s", SIZE_LABEL + 4, AVG, BOLD)
                                     .next_to(self.mag.box, RIGHT, buff=0.35))
        self.at("if we take a hundredth of a second", FadeOut(VGroup(trip, trip_strike)), FadeIn(self.readout))
        self.span("a hundredth of a second instead", "we get forty point o five", self.h.animate.set_value(0.01))

    # ------------------------------------------------------------------
    # 4.8  Postpone the choice: call it h, open the window wide
    # ------------------------------------------------------------------
    def row_4_8(self):
        self.row("4.8_call_it_h", "This is where the new maths begins")
        self.at("This is where the new maths begins", FadeOut(self.fraction), FadeOut(self.readout),
                FadeOut(VGroup(self.mag.group(), self.mag_a, self.mag_b, self.mag_secant)), run_time=0.9)
        self.span("let's not pick a window size", "at all", self.h.animate.set_value(WIDE_H), rate_func=smooth)
        word = txt("postpone", SIZE_LABEL + 4, AVG, BOLD).move_to([PANEL_X, 0.2, 0])
        self.at("postpone that decision", FadeIn(word, scale=0.9))
        h_label = always_redraw(lambda: tex("h", size=SIZE_TEX, color=AVG).next_to(self.bracket, UP, buff=0.08))
        self.at("call the length of that window h", FadeOut(word), FadeOut(self.bracket_label), FadeIn(h_label))
        self.bracket_label = h_label
        self.span("h gets smaller and smaller", "smaller and smaller", self.h.animate.set_value(WORK_H),
                  rate_func=smooth)

    # ------------------------------------------------------------------
    # 4.9  Being stubborn with a letter
    # ------------------------------------------------------------------
    def row_4_9(self):
        self.row("4.9_stubborn", "A lot of maths is just this")
        self.at("using a letter instead of a value", Indicate(self.bracket_label, color=GOLD, scale_factor=1.6),
                run_time=1.0)

    # ------------------------------------------------------------------
    # 4.10  s(t) = 5t^2
    # ------------------------------------------------------------------
    def row_4_10(self):
        self.row("4.10_formula", "Let's say that while the car")
        self.formula = self.at_panel(tex("s(t)", "=", "5t^2"), 1.0)
        self.at("given by the function", FadeIn(self.formula))
        self.at("equals five times t squared", ShowPassingFlash(self.zcurve.copy().set_stroke(GOLD, 8), time_width=0.4),
                run_time=1.2)

    # ------------------------------------------------------------------
    # 4.11  s(4) = 80 and s(4.1) = 84.05
    # ------------------------------------------------------------------
    def row_4_11(self):
        self.row("4.11_check_numbers", "After four seconds, the distance")
        l1 = tex(r"s(4) = 5 \times 16 = 80", size=SIZE_TEX_SMALL)
        l2 = tex(r"s(4.1) = 5 \times 16.81 = 84.05", size=SIZE_TEX_SMALL)
        self.checks = VGroup(l1, l2).arrange(DOWN, aligned_edge=LEFT, buff=0.25).move_to([PANEL_X, -0.3, 0])
        self.at("After four seconds", FadeIn(l1), Indicate(self.a, color=GOLD))
        self.at("after four point one seconds", self.h.animate.set_value(0.1), run_time=0.8)
        self.at("five times sixteen point eight", FadeIn(l2), Indicate(self.secants.dots[0], color=GOLD))

    # ------------------------------------------------------------------
    # 4.12  The general fraction
    # ------------------------------------------------------------------
    def row_4_12(self):
        self.row("4.12_general_fraction", "The average speed over a window of length h")
        self.label_t = tex("s(t)", size=SIZE_TEX_SMALL, color=CURVE).next_to(self.a, RIGHT, buff=0.12).shift(DOWN * 0.15)
        self.label_th = always_redraw(lambda: tex("s(t+h)", size=SIZE_TEX_SMALL, color=AVG)
                                      .next_to(self.secants.point(+1), RIGHT, buff=0.14))
        self.f1 = self.at_panel(tex_frac(["5(t+h)^2", "-", "5t^2"], ["h"]), -0.5)
        top, bar, bottom = self.f1
        self.at("The average speed over a window of length h", FadeOut(self.checks),
                self.h.animate.set_value(WORK_H), run_time=1.0)
        self.play(FadeIn(self.label_t), FadeIn(self.label_th), run_time=0.5)
        self.at("which is five times t plus h", FadeIn(top[0], shift=UP * 0.1))
        self.at("minus the distance at the start", FadeIn(top[1]), FadeIn(top[2], shift=UP * 0.1))
        self.at("all divided by h", Create(bar), FadeIn(bottom))

    # ------------------------------------------------------------------
    # 4.13  Binomial expansion
    # ------------------------------------------------------------------
    def row_4_13(self):
        self.row("4.13_expand", "With a little bit of binomial expansion")
        word = txt("binomial expansion", SIZE_LABEL, MUTED, MEDIUM)
        rule = tex(r"(t+h)^2 = t^2 + 2th + h^2", size=SIZE_TEX_SMALL, color=MUTED)
        self.side_note = self.at_panel(VGroup(word, rule).arrange(DOWN, buff=0.12), 0.75)
        self.f2 = self.at_panel(tex_frac(["5t^2", "+", "10t", "h", "+", "5", "h", "^2", "-", "5t^2"], ["h"]), -0.5)
        t1, b1, d1 = self.f1
        t2, b2, d2 = self.f2
        self.at("binomial expansion", FadeOut(self.formula), FadeIn(word))
        self.at("t squared plus two times th", FadeIn(rule))
        self.at("the top becomes",
                ReplacementTransform(t1[0], VGroup(*t2[0:8])), ReplacementTransform(t1[1], t2[8]),
                ReplacementTransform(t1[2], t2[9]), ReplacementTransform(b1, b2), ReplacementTransform(d1, d2),
                run_time=1.2)

    # ------------------------------------------------------------------
    # 4.14  The 5t^2 terms cancel: they are where the car started
    # ------------------------------------------------------------------
    def row_4_14(self):
        self.row("4.14_cancel_start", "The five times t squared cancels out")
        top, bar, bottom = self.f2
        first, minus, last = top[0], top[8], top[9]
        self.at("The five times t squared cancels out", first.animate.set_color(GOLD), minus.animate.set_color(GOLD),
                last.animate.set_color(GOLD), FadeOut(self.side_note))
        link = DashedLine(first.get_left() + LEFT * 0.05, self.label_t.get_right() + RIGHT * 0.05, color=GOLD,
                          stroke_width=2)
        self.at("That quantity represents a distance", Create(link), self.label_t.animate.set_color(GOLD),
                run_time=1.0)
        strikes = VGroup(strike(first), strike(VGroup(minus, last)))
        self.at("at the start of our window", Create(strikes))

        self.f3 = self.at_panel(tex_frac(["10t", "h", "+", "5", "h", "^2"], ["h"]), -0.5)
        t3, b3, d3 = self.f3
        self.play(FadeOut(VGroup(first, minus, last, strikes, top[1], link)), self.label_t.animate.set_color(CURVE),
                  ReplacementTransform(VGroup(*top[2:8]), t3), ReplacementTransform(bar, b3),
                  ReplacementTransform(bottom, d3), run_time=0.9)

    # ------------------------------------------------------------------
    # 4.15  Where the car was doesn't matter, only how far it moved
    # ------------------------------------------------------------------
    def row_4_15(self):
        self.row("4.15_where_it_was", "The average speed of a window shouldn't")
        before = Line(road_point(0) + UP * 0.05, road_point(F(T0)) + UP * 0.05, color=MUTED, stroke_width=9,
                      stroke_opacity=0.6)
        inside = always_redraw(lambda: Line(road_point(F(T0)) + UP * 0.05,
                                            road_point(F(T0 + self.h.get_value())) + UP * 0.05,
                                            color=AVG, stroke_width=9))
        ghost = always_redraw(lambda: make_car().set_opacity(0.35)
                              .move_to(road_point(F(T0 + self.h.get_value())), aligned_edge=DOWN))
        self.road_marks = VGroup(before, inside, ghost)
        self.at("The average speed of a window", FadeIn(ghost), Create(inside))
        self.at("car was when the window opened", Create(before))

    # ------------------------------------------------------------------
    # 4.16  Every surviving term carries an h
    # ------------------------------------------------------------------
    def row_4_16(self):
        self.row("4.16_terms_with_h", "What survives is every term")
        top = self.f3[0]
        self.at("every term with at least one h", top[1].animate.set_color(AVG), top[4].animate.set_color(AVG),
                Indicate(self.bracket_label, color=AVG))

    # ------------------------------------------------------------------
    # 4.17  Divide by h: allowed, because h is a real window
    # ------------------------------------------------------------------
    def row_4_17(self):
        self.row("4.17_divide_by_h", "Here we are allowed to simplify")
        top, bar, bottom = self.f3
        self.cancel = VGroup(strike(top[1]), strike(top[4]), strike(bottom))
        self.at("simplify the fraction by h", FadeOut(self.road_marks), Create(self.cancel), run_time=1.0)
        self.at("a real, non-zero window length", Indicate(self.bracket, color=AVG, scale_factor=1.1))

    # ------------------------------------------------------------------
    # 4.18  10t + 5h
    # ------------------------------------------------------------------
    def row_4_18(self):
        self.row("4.18_result", "What remains after the cancellation")
        top, bar, bottom = self.f3
        self.expr, self.box = result_box()
        self.at("What remains",
                ReplacementTransform(top[0], self.expr[0]), ReplacementTransform(top[2], self.expr[1]),
                ReplacementTransform(VGroup(top[3], top[5]), self.expr[2]),
                FadeOut(VGroup(top[1], top[4], bar, bottom, self.cancel)), run_time=1.0)
        self.at("is ten times t plus five", Create(self.box))

    # ------------------------------------------------------------------
    # 4.19  What it means: the gradient of the secant over [t, t + h]
    # ------------------------------------------------------------------
    def row_4_19(self):
        self.row("4.19_what_it_is", "What is this, really?")
        self.at("tells us the average speed", Indicate(self.expr, color=AVG),
                Indicate(self.secants.lines[0], color=AVG, scale_factor=1.0))
        self.at("we haven't chosen yet", Indicate(self.bracket_label, color=AVG, scale_factor=1.5))

    # ------------------------------------------------------------------
    # 4.20  10t plus a correction 5h
    # ------------------------------------------------------------------
    def row_4_20(self):
        self.row("4.20_shape", "Notice the shape of it")
        e = self.expr
        self.at("which doesn't involve", e[0].animate.set_color(CURVE), Indicate(e[0], color=CURVE))
        self.at("a correction that", e[2].animate.set_color(AVG), Indicate(e[2], color=AVG),
                Indicate(self.bracket, color=AVG, scale_factor=1.1))

    # ------------------------------------------------------------------
    # 4.21  At t = 4: 40 + 5h, and a table of windows after
    # ------------------------------------------------------------------
    def row_4_21(self):
        self.row("4.21_at_four", "At four seconds, the average")
        self.sub = sub_line()
        self.table = after_table()
        self.at("At four seconds", FadeOut(self.label_th), FadeOut(self.label_t),
                TransformFromCopy(self.expr, self.sub), run_time=1.0)
        self.at("A window of a tenth of a second", self.table.header_in(), self.h.animate.set_value(0.1))
        self.play(self.table.add_row(AFTER_ROWS[0]), run_time=0.6)
        self.at("A hundredth of a second", self.table.add_row(AFTER_ROWS[1]), self.h.animate.set_value(0.01))
        self.at("a thousandth gives", self.table.add_row(AFTER_ROWS[2]), self.h.animate.set_value(0.001))
        # leave exactly part4a_ending() on screen
        self.play(FadeOut(self.bracket), FadeOut(self.bracket_label), run_time=0.5)
        self.finish("and so on", tail=1.0)
