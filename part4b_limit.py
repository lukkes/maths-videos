"""
Part 4b: storyboard rows 4.22 to 4.33. From the two-sided squeeze to the power rule.

Opens on part 4a's last frame (built by part4a_ending()).

Preview:   manim -pql part4b_limit.py Part4b
Final:     manim -qh --fps 30 --save_sections part4b_limit.py Part4b
"""

from types import SimpleNamespace

from style import *
from part4a_windows import part4a_ending, PANEL_X, SUB_Y, T0, F, WIDE_H

BEFORE_VALUES = ["39.5", "39.95", "39.995"]
TRAP_Y = -3.4


def tangent_at(x0):
    """The tangent line to 5t^2 at x0, as a function."""
    slope = 10 * x0
    return lambda x: F(x0) + slope * (x - x0)


# ----------------------------------------------------------------------
# Pieces on screen at the end of 4b, built here so part 5 can rebuild them
# ----------------------------------------------------------------------
DEFINITION_TOP = np.array([PANEL_X, 1.0, 0])   # where the definition sits, shrunk, from 4.31 on


def general_definition():
    """s'(t) = lim (s(t+h) - s(t)) / h, full size, as first written in 4.30."""
    return tex(r"s'(t)", "=", r"\lim_{h \to 0} \frac{s(t+h) - s(t)}{h}").move_to([PANEL_X, -0.6, 0])


def speed_result():
    """s'(t) = 10t."""
    line = tex("s'(t)", "=", "10t").move_to([PANEL_X, 0.25, 0])
    line[2].set_color(AVG)
    return line


def speed_graph():
    """The small speed-time graph of 4.32, the whole 10 s trip: (axes, labels, line)."""
    vaxes = Axes(x_range=[0, T_TOTAL, 1], y_range=[0, 60, 20], x_length=3.8, y_length=1.7, tips=False,
                 axis_config={"color": INK, "stroke_width": 2, "include_numbers": False, "tick_size": 0.05})
    vaxes.move_to([PANEL_X + 0.2, -2.1, 0])
    vlabels = VGroup(txt("speed (m/s)", SIZE_TICK - 2, MUTED).next_to(vaxes.c2p(0, 60), UP, buff=0.1)
                     .align_to(vaxes.c2p(0, 0), LEFT),
                     txt("time (s)", SIZE_TICK - 2, MUTED).next_to(vaxes.x_axis, DOWN, buff=0.12))
    vline = vaxes.plot(v, x_range=[0, T_TOTAL, 0.05], color=AVG, stroke_width=4, use_smoothing=False)
    return vaxes, vlabels, vline


def moving_tangent(axes, t):
    """A short tangent to the car's curve at time t (a ValueTracker), redrawn every frame."""
    def now():
        x = float(np.clip(t.get_value(), 0.05, T_TOTAL - 0.05))
        p = axes.c2p(x, s(x))
        q = axes.c2p(x + 1, s(x) + v(x))
        d = (q - p) / np.linalg.norm(q - p)
        return Line(p - d * 1.1, p + d * 1.1, color=AVG, stroke_width=3).set_z_index(5)
    return always_redraw(now)


def speed_marker(vaxes, t):
    """Dot on the speed graph at time t, with its reading."""
    dot = always_redraw(lambda: Dot(vaxes.c2p(t.get_value(), v(t.get_value())), radius=0.07, color=AVG))
    val = always_redraw(lambda: num(f"{v(t.get_value()):.0f} m/s", SIZE_TICK, AVG, MEDIUM)
                        .next_to(dot, RIGHT, buff=0.1))
    return dot, val


def power_rule_parts():
    """5t^2, the rewritten 2·5t^1 and '= 10t', positioned as in 4.33: (start, moved, result)."""
    start = tex("5", "t", "^{2}").move_to([PANEL_X - 1.2, -0.45, 0])
    moved = tex("2", r"\cdot", "5", "t", "^{1}").move_to(start, aligned_edge=LEFT)
    result = tex("=", "10t").next_to(moved, RIGHT, buff=0.2)
    result[1].set_color(AVG)
    return start, moved, result


def power_rule_steps(start, moved):
    """Animations for 5t^2 -> 2·5t^1: the power drops in front, then one comes off it."""
    drop = [TransformFromCopy(start[2], moved[0], path_arc=-PI / 2),
            ReplacementTransform(start[0], moved[2]), ReplacementTransform(start[1], moved[3]), FadeIn(moved[1])]
    knock = [ReplacementTransform(start[2], moved[4])]
    return drop, knock


def part4b_ending():
    """Everything on screen at the end of part 4b."""
    stage = GraphStage(5.0)
    definition = general_definition().scale(0.75).move_to(DEFINITION_TOP)
    vaxes, vlabels, vline = speed_graph()
    vdot, vval = speed_marker(vaxes, stage.t)
    _, moved, result = power_rule_parts()
    return SimpleNamespace(stage=stage, definition=definition, v_line=speed_result(),
                           vaxes=vaxes, vlabels=vlabels, vline=vline, vdot=vdot, vval=vval,
                           tangent=moving_tangent(stage.axes, stage.t), power=VGroup(moved, result))


class Part4b(LessonScene):
    SCRIPT = "narration/part4b.txt"
    NEXT_START = "Since the derivative itself is also"

    def construct(self):
        self.restore_part4a_ending()
        self.row_4_22()
        self.row_4_23()
        self.row_4_24()
        self.row_4_25()
        self.row_4_26()
        self.row_4_27()
        self.row_4_28()
        self.row_4_29()
        self.row_4_30()
        self.row_4_31()
        self.row_4_32()
        self.row_4_33()

    def restore_part4a_ending(self):
        e = part4a_ending()
        self.e = e
        self.stage, self.zaxes, self.h, self.secants, self.table = e.stage, e.zaxes, e.h, e.secants, e.table
        st = e.stage
        self.add(st.road, st.car, st.clock, e.zaxes, e.zlabels, e.zcurve, e.a,
                 e.secants.lines, e.secants.dots, e.expr, e.box, e.sub, e.table.all())

    # ------------------------------------------------------------------
    # 4.22  Windows before t = 4
    # ------------------------------------------------------------------
    def row_4_22(self):
        self.row("4.22_windows_before", "Now, the curious among us")
        e = self.e
        self.at("Now, the curious among us", self.h.animate.set_value(0.1), run_time=0.8)
        line, dot = self.secants.add_side(-1)
        self.at("check intervals before", FadeIn(dot), Create(line), run_time=1.0)
        self.sub_before = tex("40", "-", "5h", color=GOLD)
        self.at("and you get forty minus", FadeIn(self.sub_before.move_to([PANEL_X - 1.3, SUB_Y, 0])))
        self.at("A tenth of a second before", self.table.add_column("before", BEFORE_VALUES, GOLD),
                run_time=1.2)
        self.span("a hundredth gives", "point nine nine five", self.h.animate.set_value(0.001))

    # ------------------------------------------------------------------
    # 4.23  The speed is trapped between the two columns
    # ------------------------------------------------------------------
    def row_4_23(self):
        self.row("4.23_trapped", "The averages from before")
        self.trap = TrapLine(39.4, 40.6, center=[PANEL_X + 0.3, TRAP_Y, 0], length=4.6,
                             ticks=[39.5, 40.0, 40.5], decimals=1)
        self.trap.set(39.5, 40.5)
        self.at("its speed at the instant must sit between",
                Create(self.trap.line), FadeIn(self.trap.labels), FadeIn(self.trap.band), run_time=1.0)
        self.trapped = txt("trapped between the two columns", SIZE_LABEL, GOLD, BOLD).move_to([PANEL_X + 0.3, -2.8, 0])
        self.at("trapped between the two columns", self.trap.squeeze(39.95, 40.05), FadeIn(self.trapped),
                run_time=1.0)
        self.at("traps it even tighter", self.trap.squeeze(39.995, 40.005), run_time=1.0)

    # ------------------------------------------------------------------
    # 4.24  Only 40 survives every row; 40.001 drops out
    # ------------------------------------------------------------------
    def row_4_24(self):
        self.row("4.24_only_forty", "There is exactly one number")
        forty = self.trap.marker(40.0, ACCENT, "40")
        one = txt("one number", SIZE_LABEL, ACCENT, BOLD).next_to(forty, LEFT, buff=0.35)
        self.at("exactly one number", FadeOut(self.trapped), FadeIn(one))
        self.at("and that number is forty", FadeIn(forty, shift=DOWN * 0.1))

        fine = TrapLine(39.998, 40.002, center=[PANEL_X + 0.3, TRAP_Y, 0], length=4.6,
                        ticks=[39.999, 40.0, 40.001], decimals=3)
        fine.set(39.995, 40.005)                      # the third row's trap, wider than this view
        fine_forty = fine.marker(40.0, ACCENT, "40")
        guess = fine.marker(40.001, WRONG, "40.001")
        self.at("say forty point", FadeOut(VGroup(self.trap.group(), forty, one)),
                FadeIn(VGroup(fine.line, fine.labels, fine.band, fine_forty)), run_time=0.9)
        self.play(FadeIn(guess, shift=DOWN * 0.1), run_time=0.5)
        self.at("a ten-thousandth of a second", self.table.add_row(["39.9995", "0.0001", "40.0005"]),
                fine.squeeze(39.9995, 40.0005), run_time=1.2)
        self.at("no longer trapping our guess", Wiggle(guess), run_time=0.8)
        self.play(FadeOut(guess, shift=UP * 0.2), run_time=0.5)
        self.fine = VGroup(fine.group(), fine_forty)

    # ------------------------------------------------------------------
    # 4.25  The definition: speed at t = 4 is 40 m/s
    # ------------------------------------------------------------------
    def row_4_25(self):
        self.row("4.25_definition", "So finally we have arrived")
        e = self.e
        clear = VGroup(self.table.all(), self.fine, e.sub, self.sub_before, e.expr, e.box)
        zero = tex_frac(["0"], ["0"], color=WRONG).move_to([PANEL_X, 0.6, 0])
        zero_strike = strike(zero, WRONG, 5)
        self.at("So finally", FadeOut(clear), FadeIn(zero), run_time=1.0)
        self.at("the definition that we were missing", Create(zero_strike))
        lines = ["the number the averages close in on,", "from both sides,", "as the window becomes smaller"]
        definition = VGroup(*[txt(l, SIZE_LABEL, AVG, BOLD) for l in lines]).arrange(DOWN, buff=0.12)
        definition.move_to([PANEL_X, -0.25, 0])
        heading = txt("speed at an instant =", SIZE_LABEL, INK, MEDIUM).next_to(definition, UP, buff=0.25)
        self.at("the speed at an instant", FadeOut(VGroup(zero, zero_strike)), FadeIn(heading))
        self.at("the number the averages close in on", FadeIn(definition[0]))
        self.at("from both sides", FadeIn(definition[1]))
        self.at("as the window becomes smaller", FadeIn(definition[2]))
        answer = tex(r"\text{speed at } t = 4\ \text{s} = 40\ \text{m/s}").move_to([PANEL_X, -1.75, 0])
        self.at("that number is forty meters", FadeIn(answer, shift=UP * 0.1))
        self.answer_line = VGroup(heading, definition, answer)

    # ------------------------------------------------------------------
    # 4.26  The limit notation
    # ------------------------------------------------------------------
    def row_4_26(self):
        self.row("4.26_limit", "Mathematicians have a name")
        self.lim1 = tex(r"\lim_{h \to 0}", r"\left(40 + 5h\right)", "=", "40").move_to([PANEL_X + 0.5, 0.2, 0])
        self.lim1[3].set_color(AVG)
        name = txt("limit", SIZE_LABEL + 4, AVG, BOLD).next_to(self.lim1, LEFT, buff=0.45)
        self.at("Mathematicians have a name", FadeOut(self.answer_line))
        self.at("It's called a limit", FadeIn(name))
        self.at("it's written like this", FadeIn(self.lim1[0], shift=UP * 0.1))
        self.at("in front of the expression", FadeIn(self.lim1[1]))
        self.at("the one number that", FadeIn(self.lim1[2]), FadeIn(self.lim1[3]))
        self.lim_extras = VGroup(name)

    # ------------------------------------------------------------------
    # 4.27  Keeping t: 10t + 5h -> 10t
    # ------------------------------------------------------------------
    def row_4_27(self):
        self.row("4.27_keep_t", "And if we don't plug in four seconds")
        self.lim2 = tex(r"\lim_{h \to 0}", r"\left(10t + 5h\right)", "=", "10t").move_to([PANEL_X + 0.5, -1.0, 0])
        self.lim2[3].set_color(AVG)
        self.at("but keep t", FadeIn(self.lim2[0]), FadeIn(self.lim2[1]))
        self.at("into ten times t", FadeIn(self.lim2[2]), FadeIn(self.lim2[3]))

    # ------------------------------------------------------------------
    # 4.28  The two secants close onto the tangent
    # ------------------------------------------------------------------
    def row_4_28(self):
        self.row("4.28_tangent", "Observe the same thing graphically")
        panel = VGroup(self.lim1, self.lim_extras, self.lim2)
        self.at("Observe the same thing graphically", FadeOut(panel),
                self.h.animate.set_value(WIDE_H), run_time=1.2)
        self.span("as h gets smaller and smaller", "settle on one particular line", self.h.animate.set_value(0.003),
                  rate_func=smooth)
        za = self.zaxes
        (xa, ya), (xb, yb) = clipped_line_points(za, T0, F(T0), 10 * T0, 2.0)
        tline = Line(za.c2p(xa, ya), za.c2p(xb, yb), color=INK, stroke_width=3.5).set_z_index(5)
        tlabel = txt("tangent", SIZE_LABEL + 4, INK, BOLD).move_to(za.c2p(1.6, 150))
        still = self.secants.freeze(self)
        self.at("That line is the tangent", FadeOut(still), Create(tline), FadeIn(tlabel), run_time=1.0)
        self.tangent = VGroup(tline, tlabel)

    # ------------------------------------------------------------------
    # 4.29  Its gradient is the speed at that instant
    # ------------------------------------------------------------------
    def row_4_29(self):
        self.row("4.29_tangent_gradient", "As we might expect")
        tri = rise_run_triangle(self.zaxes, tangent_at(T0), T0, 1.0, AVG, 3)
        val = num("40 m/s", SIZE_LABEL, AVG, BOLD).next_to(tri[1], RIGHT, buff=0.1)
        self.at("the gradient of the tangent", Create(tri), FadeIn(val))
        self.tri = VGroup(tri, val)

    # ------------------------------------------------------------------
    # 4.30  The general procedure
    # ------------------------------------------------------------------
    def row_4_30(self):
        self.row("4.30_general_definition", "But now let's step back")
        rr = tex_frac(["s(t+h) - s(t)"], ["h"]).move_to([PANEL_X, 0.6, 0])
        self.at("We wrote rise over run", FadeIn(rr))
        self.at("where the answer heads", Indicate(rr, color=AVG))
        self.definition = general_definition()
        self.at("Written out in general", ReplacementTransform(rr, self.definition[2]), FadeIn(self.definition[:2]),
                run_time=1.5)

    # ------------------------------------------------------------------
    # 4.31  It's called the derivative; doing it is differentiating
    # ------------------------------------------------------------------
    def row_4_31(self):
        self.row("4.31_derivative", "This is a derivative")
        d = self.definition
        word = txt("derivative", SIZE_LABEL + 4, AVG, BOLD).next_to(d, DOWN, buff=0.45)
        verb = txt("differentiating", SIZE_LABEL, INK, BOLD).next_to(word, DOWN, buff=0.2)
        self.at("This is a derivative", FadeIn(word))
        self.at("is called differentiating", FadeIn(verb))
        self.at("We read s dash of t", Indicate(d[0], color=AVG, scale_factor=1.3))
        self.play(FadeOut(word), FadeOut(verb), d.animate.scale(0.75).move_to(DEFINITION_TOP), run_time=0.8)

    # ------------------------------------------------------------------
    # 4.32  The derivative is a function: speed at every moment
    # ------------------------------------------------------------------
    def row_4_32(self):
        self.row("4.32_derivative_is_function", "One more seemingly minor thing")
        st, e = self.stage, self.e
        self.at("One more seemingly minor thing",
                FadeOut(VGroup(e.zaxes, e.zlabels, e.zcurve, e.a, self.tangent, self.tri)),
                FadeIn(VGroup(st.axes, st.axis_labels, st.tracker.curve)), run_time=1.2)
        self.v_line = speed_result()
        self.at("namely ten times t", FadeIn(self.v_line))

        vaxes, vlabels, vline = speed_graph()
        t = st.t
        tan = moving_tangent(st.axes, t)
        vdot, vval = speed_marker(vaxes, t)
        self.at("It lets us find the speed", Create(vaxes), FadeIn(vlabels), Create(vline), run_time=1.0)
        self.add(st.tracker.dot, tan, vdot, vval)
        self.at("Ten meters per second after one second", t.animate.set_value(1.0), run_time=0.9)
        self.at("twenty after two", t.animate.set_value(2.0), run_time=0.7)
        self.at("fifty after five", t.animate.set_value(5.0), run_time=0.9)

    # ------------------------------------------------------------------
    # 4.33  The textbook rule is this, shortened
    # ------------------------------------------------------------------
    def row_4_33(self):
        self.row("4.33_power_rule", "And if you've seen a textbook rule")
        start, moved, result = power_rule_parts()
        self.at("you've already met this result", FadeIn(start))
        drop, knock = power_rule_steps(start, moved)
        self.at("bring the power down in front", *drop, run_time=1.0)
        self.at("knock one off the power", *knock)
        self.at("which is ten times t", FadeIn(result, shift=LEFT * 0.1))
        self.at("exactly what the limit gave us", Indicate(result[1], color=AVG),
                Indicate(self.v_line[2], color=AVG))
        self.finish("what the limit gave us")
