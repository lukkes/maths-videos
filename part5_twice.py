"""
Part 5: storyboard rows 5.1, 5.2, 5.3, 5.6, 5.7 and 5.9. Differentiating twice,
then the same stack of derivatives for an epidemic; 5.9 also shows a third
stack for the current in a wire.

Opens on part 4b's last frame (built by part4b_ending()).

Preview:   manim -pql part5_twice.py Part5
Final:     manim -qh --fps 30 --save_sections part5_twice.py Part5
"""

from style import *
from part4b_limit import part4b_ending

PANEL_X = 4.3                     # centre of the right-hand panel in part 5
T_SECANT = 1.5                    # where the secant on the speed graph starts, in 5.2

# ----------------------------------------------------------------------
# The three stacks: car, epidemic, wire
# ----------------------------------------------------------------------


def cases(t):
    return 100 / (1 + np.exp(-1.2 * (t - 5)))


def new_cases(t):
    c = cases(t)
    return 1.2 * c * (1 - c / 100)


def new_cases_change(t):
    return 1.2 * new_cases(t) * (1 - 2 * cases(t) / 100)


def epidemic_stack(**kw):
    return DerivativeStack([cases, new_cases, new_cases_change], 10,
                           [(0, 110), (0, 33), (-13, 13)],
                           ["total cases in an epidemic", "new cases per day", "change in new cases per day"],
                           x_title="days", **kw)


T_OFF = 6.0          # the switch opens
TAU_ON, TAU_OFF = 1.5, 0.12
I_OFF = 1 - np.exp(-T_OFF / TAU_ON)


def current(t):
    if t <= T_OFF:
        return 1 - np.exp(-t / TAU_ON)
    return I_OFF * np.exp(-(t - T_OFF) / TAU_OFF)


def charge(t):
    if t <= T_OFF:
        return t - TAU_ON * (1 - np.exp(-t / TAU_ON))
    q_off = T_OFF - TAU_ON * (1 - np.exp(-T_OFF / TAU_ON))
    return q_off + I_OFF * TAU_OFF * (1 - np.exp(-(t - T_OFF) / TAU_OFF))


def current_change(t):
    if t <= T_OFF:
        return np.exp(-t / TAU_ON) / TAU_ON
    return -I_OFF / TAU_OFF * np.exp(-(t - T_OFF) / TAU_OFF)


def wire_stack(**kw):
    return DerivativeStack([charge, current, current_change], 10,
                           [(0, 5.5), (0, 1.1), (-9, 1.2)],
                           ["charge through the wire", "current", "rate of change of current"], **kw)


# ----------------------------------------------------------------------
# 5.9's side-by-side frame, built here so part 6 can open on it
# ----------------------------------------------------------------------
THUMB_SCALE = 0.5
THUMB_SLOTS = [np.array([x, -0.1, 0]) for x in (-5.3, -2.15, 1.0)]


def side_labels(ref):
    """The two questions and their names, lined up with the arrows of the stack `ref`: (first, second, guides)."""
    def block(lines, keyword, k):
        b = VGroup(*[txt(l, SIZE_LABEL, INK) for l in lines],
                   txt(keyword, SIZE_LABEL + 2, AVG, BOLD)).arrange(DOWN, buff=0.12)
        b[-1].shift(DOWN * 0.08)
        return b.move_to([4.6, ref.arrows[k].get_center()[1], 0])

    first = block(["how fast is it changing?"], "derivative", 0).shift(UP * 0.2)
    second = block(["is that change speeding up", "or slowing down?"], "derivative of a derivative", 1)
    second.shift(DOWN * 0.25)
    guides = VGroup(*[DashedLine([ref.arrows[k].get_right()[0] + 0.1, b.get_center()[1], 0],
                                 [b.get_left()[0] - 0.15, b.get_center()[1], 0],
                                 color=MUTED, stroke_width=1.5, dash_length=0.06)
                      for k, b in ((0, first), (1, second))])
    return first, second, guides


def part5_ending():
    """Everything on screen at the end of part 5: the three small stacks and the labels."""
    stacks = [car_stack(), epidemic_stack(), wire_stack()]
    for st, slot in zip(stacks, THUMB_SLOTS):
        st.group().scale(THUMB_SCALE).move_to(slot)
    first, second, guides = side_labels(stacks[2])
    return VGroup(*[st.group() for st in stacks], first, second, guides)


class Part5(LessonScene):
    SCRIPT = "narration/part5.txt"
    START = "Since the derivative itself is also"
    NEXT_START = "And that's it for this video"

    def construct(self):
        self.restore_part4b_ending()
        for row in (self.row_5_1, self.row_5_2, self.row_5_3, self.row_5_6, self.row_5_7, self.row_5_9):
            row()

    def restore_part4b_ending(self):
        e = part4b_ending()
        self.e = e
        st = e.stage
        self.add(st.road, st.car, st.clock, st.axes, st.axis_labels, st.tracker.curve, st.tracker.dot, e.tangent,
                 e.definition, e.v_line, e.power, e.vaxes, e.vlabels, e.vline, e.vdot, e.vval)

    # ------------------------------------------------------------------
    # 5.1  The speed graph moves into a stack; empty axes for a third graph
    # ------------------------------------------------------------------
    def row_5_1(self):
        self.row("5.1_stack", "Since the derivative itself is also")
        e, st = self.e, self.e.stage
        car = self.car = car_stack()
        self.at("Since the derivative itself is also",
                FadeOut(VGroup(st.road, st.car, st.clock, st.axis_labels, st.tracker.dot, e.tangent, e.definition,
                               e.power, e.vdot, e.vval, e.vlabels[1])),
                ReplacementTransform(st.axes, car.axes[0]), ReplacementTransform(st.tracker.curve, car.curves[0]),
                ReplacementTransform(e.vaxes, car.axes[1]), ReplacementTransform(e.vline, car.curves[1]),
                ReplacementTransform(e.vlabels[0], car.titles[1]), FadeIn(car.titles[0]),
                e.v_line.animate.move_to([PANEL_X, 2.7, 0]), run_time=1.5)
        self.add(car.titles[1], car.curves[0], car.curves[1])
        self.play(GrowArrow(car.arrows[0]), run_time=0.6)
        self.at("its rate of change", Create(car.axes[2]), GrowArrow(car.arrows[1]), FadeIn(car.x_title),
                run_time=1.0)

    # ------------------------------------------------------------------
    # 5.2  Same procedure on 10t: the secant already lies on the line
    # ------------------------------------------------------------------
    def row_5_2(self):
        self.row("5.2_same_procedure", "Turns out we can")
        car = self.car
        axes = car.axes[1]
        self.h = h = ValueTracker(2.5)
        sec = WindowSecants(axes, car.funcs[1], T_SECANT, h, sides=(+1,), extend=3.5, colors={+1: GOLD})
        start = Dot(car.point(1, T_SECANT), radius=0.08, color=GOLD).set_z_index(5)
        bracket = always_redraw(lambda: window_bracket(axes, T_SECANT, T_SECANT + h.get_value(), GOLD))
        h_label = always_redraw(lambda: tex("h", size=SIZE_TEX_SMALL, color=GOLD).next_to(bracket, UP, buff=0.06))
        self.at("Running the same procedure on ten", FadeIn(start), FadeIn(sec.dots), Create(sec.lines),
                FadeIn(bracket), FadeIn(h_label), run_time=1.0)

        f1 = tex_frac([r"10(t+h) - 10t"], ["h"], size=SIZE_TEX_SMALL)
        f2 = tex_frac(["10h"], ["h"], size=SIZE_TEX_SMALL)
        eq1, eq2 = tex("=", size=SIZE_TEX_SMALL), tex("=", size=SIZE_TEX_SMALL)
        ten = tex("10", size=SIZE_TEX, color=ACCENT)
        chain = VGroup(f1, eq1, f2, eq2, ten).arrange(RIGHT, buff=0.2).move_to([PANEL_X, 1.45, 0])
        self.at("the average change over a window", FadeIn(f1))
        self.at("minus ten times T over", FadeIn(eq1), FadeIn(f2))
        self.span("which is just ten", "which is just ten", FadeIn(eq2), FadeIn(ten),
                  h.animate.set_value(0.4))
        self.secant_bits = VGroup(start, sec.lines, sec.dots, bracket, h_label)
        self.chain = chain

    # ------------------------------------------------------------------
    # 5.3  A flat line at 10: acceleration
    # ------------------------------------------------------------------
    def row_5_3(self):
        self.row("5.3_acceleration", "So the speed goes up")
        car = self.car
        u = self.u = ValueTracker(0)
        speedo = make_speedometer(lambda: v(u.get_value()), center=np.array([PANEL_X, -1.95, 0]), radius=1.0)
        clock = always_redraw(lambda: num(f"t = {u.get_value():.0f} s", SIZE_LABEL)
                              .next_to(speedo, UP, buff=0.15))
        dots = car.dots(u)
        flat = car.growing(2, u)
        self.at("So the speed goes up", FadeOut(self.secant_bits), FadeIn(speedo), FadeIn(clock), run_time=0.6)
        self.add(dots, flat)
        for k in range(1, 6):                     # one even step per second
            self.play(u.animate.set_value(k), run_time=0.3, rate_func=smooth)
            self.wait(0.05)
        self.play(u.animate.set_value(T_TOTAL), run_time=1.0, rate_func=linear)   # then it brakes
        self.remove(flat)
        self.add(car.curves[2])

        brace = Brace(car.arrows, RIGHT, color=INK, buff=0.15)
        twice = txt("differentiating twice", SIZE_LABEL, INK, BOLD).next_to(brace, RIGHT, buff=0.15)
        self.at("differentiating twice", GrowFromCenter(brace), FadeIn(twice))
        car.titles[2].become(txt("acceleration (m/s²)", SIZE_LABEL, ACCENT, BOLD)
                             .next_to(car.axes[2], UP, buff=0.1).align_to(car.axes[2], LEFT))
        acc = VGroup(num("10 m/s²", SIZE_LABEL, ACCENT, MEDIUM).move_to(car.axes[2].c2p(2.5, 5)),
                     num("−10 m/s²", SIZE_LABEL, ACCENT, MEDIUM).move_to(car.axes[2].c2p(7.5, -5)))
        self.at("acceleration", FadeIn(car.titles[2], shift=UP * 0.1), FadeIn(acc), run_time=0.5)
        self.car_extras = VGroup(speedo, clock, dots, brace, twice, acc, self.chain, self.e.v_line)

    # ------------------------------------------------------------------
    # 5.6  The same stack for an epidemic
    # ------------------------------------------------------------------
    def row_5_6(self):
        self.row("5.6_epidemic", "But differentiation produces meaningful")
        car = self.car
        epi = self.epi = epidemic_stack()
        self.at("But differentiation produces meaningful", FadeOut(self.car_extras), run_time=0.8)
        self.at("Take the total number of cases", *car.morph_to(epi), run_time=1.0)
        self.at("cases in an epidemic", Indicate(epi.titles[0], color=CURVE, scale_factor=1.15))
        self.at("new cases per day", Indicate(epi.titles[1], color=AVG, scale_factor=1.15))
        ax, x_left = epi.axes[2], epi.arrows.get_right()[0] + 0.45
        up = txt("+  speeding up", SIZE_LABEL, ACCENT, BOLD)
        up.move_to([x_left, ax.c2p(0, 6.5)[1], 0], aligned_edge=LEFT)
        down = txt("−  slowing down", SIZE_LABEL, AVG, BOLD)
        down.move_to([x_left, ax.c2p(0, -6.5)[1], 0], aligned_edge=LEFT)
        self.at("speeding up", FadeIn(up))
        self.at("slowing down", FadeIn(down), run_time=0.5)
        self.epi_labels = VGroup(up, down)

    # ------------------------------------------------------------------
    # 5.7  "The curve is flattening": the peak of new cases
    # ------------------------------------------------------------------
    def row_5_7(self):
        self.row("5.7_flattening", "When we were hearing news")
        epi = self.epi
        x = 5.0
        top = epi.axes[0].get_top()[1]
        bottom = epi.axes[2].get_bottom()[1]
        cx = epi.axes[0].c2p(x, 0)[0]
        cursor = DashedLine([cx, top, 0], [cx, bottom, 0], color=MUTED, stroke_width=2, dash_length=0.08)
        marks = VGroup(*[Dot(epi.point(k, x), radius=0.08, color=epi.COLORS[k]).set_z_index(5) for k in range(3)])
        self.at("When we were hearing news", Create(cursor), FadeIn(marks), run_time=0.9)

        caption = txt("the curve is flattening", SIZE_LABEL, BG, BOLD)
        plate = RoundedRectangle(corner_radius=0.08, width=caption.width + 0.5, height=caption.height + 0.35,
                                 fill_color=INK, fill_opacity=1, stroke_width=0)
        strip = Rectangle(width=0.12, height=plate.height, fill_color=AVG, fill_opacity=1, stroke_width=0)
        upper_third = VGroup(plate, caption, strip.next_to(plate, LEFT, buff=0)).move_to([PANEL_X, 2.9, 0])
        self.at("the curve flattening", FadeIn(upper_third, shift=DOWN * 0.2))

        rising = self.short_tangent(epi, 0, x, GOLD)
        flat = self.short_tangent(epi, 1, x, GOLD)
        self.at("still getting new cases every day", Create(rising), Indicate(marks[0], scale_factor=1.6))
        self.at("decreasing rate", Create(flat), Indicate(marks[2], scale_factor=1.6))
        self.flatten_bits = VGroup(cursor, marks, upper_third, rising, flat, self.epi_labels)

    def short_tangent(self, stack, k, x, color, half=0.7):
        f, ax = stack.funcs[k], stack.axes[k]
        slope = (f(x + 1e-4) - f(x - 1e-4)) / 2e-4
        p, q = ax.c2p(x, f(x)), ax.c2p(x + 1, f(x) + slope)
        d = (q - p) / np.linalg.norm(q - p)
        return Line(p - d * half, p + d * half, color=color, stroke_width=4).set_z_index(4)

    # ------------------------------------------------------------------
    # 5.9  Three stacks side by side: derivative, derivative of a derivative
    # ------------------------------------------------------------------
    def row_5_9(self):
        self.row("5.9_side_by_side", "Whenever you ask")
        epi = self.epi
        car, wire = car_stack(), wire_stack()     # the wire stack is shown here without being narrated
        for st, slot in ((car, THUMB_SLOTS[0]), (wire, THUMB_SLOTS[2])):
            st.group().scale(THUMB_SCALE).move_to(slot)
        self.at("Whenever you ask", FadeOut(self.flatten_bits),
                epi.group().animate.scale(THUMB_SCALE).move_to(THUMB_SLOTS[1]),
                FadeIn(car.group()), FadeIn(wire.group()), run_time=0.8)

        stacks = [car, epi, wire]
        first, second, guides = side_labels(wire)
        self.at("how fast something is changing", FadeIn(first[:-1]), Create(guides[0]),
                *[Indicate(st.arrows[0], color=AVG) for st in stacks])
        self.at("asking for a derivative", FadeIn(first[-1], shift=UP * 0.1))
        self.at("whether that change is speeding up", FadeIn(second[:-1]), Create(guides[1]),
                *[Indicate(st.arrows[1], color=AVG) for st in stacks])
        self.at("the derivative of a derivative", FadeIn(second[-1], shift=UP * 0.1), run_time=0.45)
        self.finish("the derivative of a derivative")
