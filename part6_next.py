"""
Part 6: storyboard rows 6.1 to 6.5. What comes next: the power rule for any
power, three places derivatives get used, and integration. Ends on the end card.

Opens on part 5's last frame (built by part5_ending()).

Preview:   manim -pql part6_next.py Part6
Final:     manim -qh --fps 30 --save_sections part6_next.py Part6
"""

from style import *
from part4b_limit import general_definition, power_rule_parts, power_rule_steps
from part5_twice import part5_ending

CARD_SIZE = (4.1, 3.3)
CARD_XS = (-4.55, 0.0, 4.55)


def algebra_page():
    """The working from part 4, as a faint column of lines to scroll behind the definition."""
    lines = [r"s(t) = 5t^2", r"\frac{5(t+h)^2 - 5t^2}{h}", r"\frac{5t^2 + 10th + 5h^2 - 5t^2}{h}",
             r"\frac{10th + 5h^2}{h}", r"10t + 5h", r"40 - 5h \quad 40 + 5h",
             r"\lim_{h \to 0} (40 + 5h) = 40", r"\lim_{h \to 0} (10t + 5h) = 10t", r"s'(t) = 10t"]
    cols = VGroup(*[VGroup(*[tex(l, size=SIZE_TEX, color=MUTED) for l in lines[k::2] + lines[1 - k::2]])
                    .arrange(DOWN, buff=0.6) for k in (0, 1)])
    cols[0].move_to([-4.0, 0, 0])
    cols[1].move_to([4.0, 0, 0])
    page = cols.set_opacity(0.55).set_z_index(-2)
    return page.next_to([0, -4.2, 0], DOWN, buff=0)


def plot_card(center, f, x_range, y_range, x_title, y_title, label):
    """A small paper card with a graph and a label underneath: (card group, axes, curve)."""
    w, h = CARD_SIZE
    paper = RoundedRectangle(corner_radius=0.12, width=w, height=h, fill_color=PAPER, fill_opacity=1,
                             stroke_width=0).move_to(center)
    axes = Axes(x_range=[*x_range, (x_range[1] - x_range[0]) / 5], y_range=[*y_range, (y_range[1] - y_range[0]) / 4],
                x_length=w - 1.0, y_length=h - 1.45, tips=False,
                axis_config={"color": INK, "stroke_width": 2, "include_ticks": False})
    axes.move_to(paper.get_center() + UP * 0.3 + RIGHT * 0.1)
    titles = VGroup(txt(y_title, SIZE_TICK - 2, MUTED).next_to(axes, UP, buff=0.08).align_to(axes, LEFT),
                    txt(x_title, SIZE_TICK - 2, MUTED).next_to(axes, DOWN, buff=0.08).align_to(axes, RIGHT))
    curve = axes.plot(f, x_range=[*x_range, (x_range[1] - x_range[0]) / 200], color=CURVE, stroke_width=4)
    name = txt(label, SIZE_LABEL, AVG, BOLD).move_to([center[0], paper.get_bottom()[1] + 0.35, 0])
    return VGroup(paper, axes, titles, curve, name), axes, curve


def sliding_tangent(axes, f, x: ValueTracker, color=GOLD, half=0.65):
    """A short tangent to f that follows the x tracker."""
    def now():
        x0 = x.get_value()
        slope = (f(x0 + 1e-4) - f(x0 - 1e-4)) / 2e-4
        p, q = axes.c2p(x0, f(x0)), axes.c2p(x0 + 1, f(x0) + slope)
        d = (q - p) / np.linalg.norm(q - p)
        return VGroup(Line(p - d * half, p + d * half, color=color, stroke_width=4),
                      Dot(p, radius=0.06, color=color)).set_z_index(4)
    return always_redraw(now)


def profit(p):
    return 25 - (p - 5) ** 2


CAN_VOLUME = 1.0


def metal(r):
    """Surface area of a closed can of fixed volume, against its radius."""
    return 2 * PI * r**2 + 2 * CAN_VOLUME / r


def medicine(t):
    return 100 * np.exp(-0.35 * t)


NEXT_DOSE = 20
T_DOSE = np.log(100 / NEXT_DOSE) / 0.35


def end_card():
    title = txt("Why your speedometer needs calculus", 40, INK, MEDIUM).move_to(UP * 2.4)
    before = VGroup(txt("Before this video:", SIZE_LABEL + 4, INK, BOLD),
                    *[txt(item, SIZE_LABEL + 2, MUTED) for item in
                      ("gradient of a line", "functions and function notation", "expanding (t + h)²")])
    before.arrange(DOWN, aligned_edge=LEFT, buff=0.25).move_to([-3.0, -0.4, 0])
    nxt = VGroup(txt("Next:", SIZE_LABEL + 4, INK, BOLD), txt("the power rule, for any power", SIZE_LABEL + 2, AVG))
    nxt.arrange(DOWN, aligned_edge=LEFT, buff=0.25).align_to(before, UP).shift(RIGHT * 6.0)
    nxt.set_x(3.4)
    return VGroup(title, before, nxt)


class Part6(LessonScene):
    SCRIPT = "narration/part6.txt"

    def construct(self):
        self.ending5 = part5_ending()
        self.add(self.ending5)
        self.row_6_1()
        self.row_6_2()
        self.row_6_3()
        self.row_6_4()
        self.row_6_5()

    # ------------------------------------------------------------------
    # 6.1  The definition, with the algebra of part 4 scrolling behind it
    # ------------------------------------------------------------------
    def row_6_1(self):
        self.row("6.1_thats_it", "And that's it for this video")
        self.definition = general_definition().scale(1.35).move_to(ORIGIN)
        backing = BackgroundRectangle(self.definition, color=BG, fill_opacity=1, buff=0.3).set_z_index(-1)
        page = algebra_page()
        self.add(page)
        self.at("And that's it for this video", FadeOut(self.ending5), FadeIn(backing), FadeIn(self.definition),
                run_time=0.5)
        self.play(page.animate.shift(UP * (page.height + 8.4)), run_time=1.1, rate_func=linear)
        self.remove(page, backing)

    # ------------------------------------------------------------------
    # 6.2  Next video: the power rule for any power
    # ------------------------------------------------------------------
    def row_6_2(self):
        self.row("6.2_next_video", "In the next video")
        d = self.definition
        self.at("In the next video", d.animate.scale(1 / 1.35).move_to([-3.4, 1.6, 0]))

        start, moved, result = power_rule_parts()
        step = VGroup(start, moved, result)
        offset = np.array([3.4, 1.6, 0]) - VGroup(moved, result).get_center()
        step.shift(offset)
        self.at("the shortcut we saw earlier", FadeIn(start))
        drop, knock = power_rule_steps(start, moved)
        self.at("bringing the power down", *drop, run_time=1.0)
        self.at("knocking one off", *knock, FadeIn(result, shift=LEFT * 0.1))

        rule = tex("t^{n}", r"\;\longrightarrow\;", "n", r"\cdot", "t^{n-1}", size=SIZE_TEX + 8)
        rule[2].set_color(AVG)
        heading = txt("Next: the power rule, for any power", SIZE_LABEL, INK, BOLD)
        inner = VGroup(heading, rule).arrange(DOWN, buff=0.35)
        card = RoundedRectangle(corner_radius=0.12, width=inner.width + 0.7, height=inner.height + 0.6,
                                fill_color=PAPER, fill_opacity=1, stroke_width=0)
        VGroup(card, inner).move_to([3.4, -0.9, 0])
        inner.move_to(card)
        self.at("any power of t", FadeIn(card), FadeIn(rule, shift=UP * 0.1), run_time=0.9)
        self.at("not just t squared", FadeIn(heading))
        arrow = Arrow(d.get_bottom() + DOWN * 0.1, card.get_left() + LEFT * 0.1, color=MUTED, stroke_width=3,
                      buff=0.1, path_arc=PI / 6)
        self.at("we won't need to take a limit", Create(arrow), d.animate.set_opacity(0.45))
        self.next_bits = VGroup(d, step, card, inner, arrow)

    # ------------------------------------------------------------------
    # 6.3  Three places derivatives get used
    # ------------------------------------------------------------------
    def row_6_3(self):
        self.row("6.3_put_to_work", "Then we'll put derivatives to work")
        self.at("Then we'll put derivatives to work", FadeOut(self.next_bits))

        c1, ax1, _ = plot_card([CARD_XS[0], 0.2, 0], profit, (0, 10), (0, 28), "price", "profit", "best price")
        x1 = ValueTracker(1.5)
        t1 = sliding_tangent(ax1, profit, x1)
        self.at("find the price", FadeIn(c1, shift=UP * 0.15), run_time=0.7)
        self.add(t1)
        self.at("the most profit", x1.animate.set_value(5.0), run_time=1.0)

        c2, ax2, _ = plot_card([CARD_XS[1], 0.2, 0], metal, (0.25, 1.5), (0, 17), "radius", "metal", "least metal")
        x2 = ValueTracker(1.3)
        t2 = sliding_tangent(ax2, metal, x2)
        self.at("design a drink can", FadeIn(c2, shift=UP * 0.15), run_time=0.7)
        self.add(t2)
        self.at("using the least metal", x2.animate.set_value((CAN_VOLUME / (2 * PI)) ** (1 / 3)), run_time=1.0)

        c3, ax3, _ = plot_card([CARD_XS[2], 0.2, 0], medicine, (0, 10), (0, 105), "hours", "medicine", "next dose")
        x3 = ValueTracker(0.6)
        t3 = sliding_tangent(ax3, medicine, x3, color=AVG)
        dose_line = DashedLine(ax3.c2p(0, NEXT_DOSE), ax3.c2p(10, NEXT_DOSE), color=MUTED, stroke_width=2,
                               dash_length=0.07)
        dose_dot = Dot(ax3.c2p(T_DOSE, NEXT_DOSE), radius=0.08, color=GOLD).set_z_index(5)
        name = c3[-1]
        c3.remove(name)
        self.at("how doctors work out", FadeIn(c3, shift=UP * 0.15), run_time=0.7)
        self.add(t3)
        self.span("how quickly a medicine is leaving", "your bloodstream", x3.animate.set_value(T_DOSE))
        self.at("the next dose is due", Create(dose_line), FadeIn(dose_dot, scale=0.5), FadeIn(name))
        self.cards = VGroup(c1, c2, c3, name, t1, t2, t3, dose_line, dose_dot)

    # ------------------------------------------------------------------
    # 6.4  The reverse question: from speed back to distance
    # ------------------------------------------------------------------
    def row_6_4(self):
        self.row("6.4_integration", "And then there's the reverse question")
        size = dict(x_length=6.2, y_length=1.9, tips=False,
                    axis_config={"color": INK, "stroke_width": 2, "include_ticks": False})
        dist = Axes(x_range=[0, T_TOTAL, 1], y_range=[0, 260, 65], **size).move_to([-1.3, 1.45, 0])
        speed = Axes(x_range=[0, T_TOTAL, 1], y_range=[0, 55, 11], **size).move_to([-1.3, -1.75, 0])
        titles = VGroup(txt("distance (m)", SIZE_TICK, MUTED).next_to(dist, UP, buff=0.1).align_to(dist, LEFT),
                        txt("speed (m/s)", SIZE_TICK, MUTED).next_to(speed, UP, buff=0.1).align_to(speed, LEFT),
                        txt("time (s)", SIZE_TICK, MUTED).next_to(speed, DOWN, buff=0.1).align_to(speed, RIGHT))
        x_arrow = dist.get_right()[0] + 0.55
        up = Arrow([x_arrow, speed.get_center()[1], 0], [x_arrow, dist.get_center()[1], 0], buff=0.3,
                   color=AVG, stroke_width=4, max_tip_length_to_length_ratio=0.1)
        self.at("And then there's the reverse question", FadeOut(self.cards), Create(dist), Create(speed),
                FadeIn(titles), run_time=0.7)
        self.at("the reverse question", GrowArrow(up))

        vcurve = speed.plot(v, x_range=[0, T_TOTAL, 0.05], color=AVG, stroke_width=4, use_smoothing=False)
        self.at("if you only know the speed", Create(vcurve), run_time=1.0)

        u = ValueTracker(0.01)

        def area():
            x_end = u.get_value()
            xs = np.linspace(0, x_end, 60)
            pts = [speed.c2p(0, 0)] + [speed.c2p(x, v(x)) for x in xs] + [speed.c2p(x_end, 0)]
            return Polygon(*pts, stroke_width=0, fill_color=AVG, fill_opacity=0.3)

        shade = always_redraw(area)
        trace = always_redraw(lambda: dist.plot(s, x_range=[0, max(u.get_value(), 0.02), 0.05], color=CURVE,
                                                stroke_width=4))
        dot = always_redraw(lambda: Dot(dist.c2p(u.get_value(), s(u.get_value())), radius=0.07, color=CURVE)
                            .set_z_index(5))
        readout = always_redraw(lambda: num(f"{s(u.get_value()):.0f} m", SIZE_LABEL, INK, MEDIUM)
                                .move_to(speed.c2p(5, 17)))
        self.add(shade, trace, dot, readout)
        self.span("how far you've gone", "other half of calculus", u.animate.set_value(T_TOTAL), rate_func=linear)
        name = txt("integration", SIZE_LABEL + 4, AVG, BOLD).next_to(up, RIGHT, buff=0.25)
        self.at("called integration", FadeIn(name, shift=LEFT * 0.1))
        self.integration = VGroup(dist, speed, titles, up, vcurve, shade, trace, dot, readout, name)

    # ------------------------------------------------------------------
    # 6.5  End card (no narration)
    # ------------------------------------------------------------------
    def row_6_5(self):
        self.wait_until(self.when("a story for another video", end=True) + 0.8)
        self.check_bounds("end of 6.4_integration")
        self._current_row = "6.5_end_card"
        self.next_section("6.5_end_card")
        card = end_card()
        self.play(FadeOut(self.integration), run_time=0.8)
        self.play(FadeIn(card[0], shift=UP * 0.1), run_time=0.8)
        self.play(FadeIn(card[1]), FadeIn(card[2]), run_time=0.8)
        self.wait(4)
        self.finish("a story for another video", tail=self.now - self.when("a story for another video", end=True))
