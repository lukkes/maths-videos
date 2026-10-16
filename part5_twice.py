"""
Part 5: storyboard rows 5.1 to 5.9 (5.4 and 5.5 are empty in the storyboard).
Differentiating twice, then the same stack of derivatives for an epidemic and
for the current in a coil.

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


def acceleration(t):
    """+10 m/s² while speeding up, -10 m/s² while braking."""
    return 10.0 if t < 5 else -10.0


def car_stack(**kw):
    return DerivativeStack([s, v, acceleration], T_TOTAL,
                           [(0, 260), (0, 55), (-12, 12)],
                           ["distance (m)", "speed (m/s)", "acceleration (m/s²)"], **kw)


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
# The coil circuit in 5.8: battery, switch, coil, and a spark gap across the coil
# ----------------------------------------------------------------------
class CoilCircuit:
    LEFT_X, RIGHT_X, TOP_Y, BOTTOM_Y = 2.1, 6.5, 2.35, 0.2
    COIL = (3.4, 5.2)          # x range of the coil on the top wire
    GAP_Y = 1.5                # height of the spark gap branch

    def __init__(self):
        l, r, top, bot = self.LEFT_X, self.RIGHT_X, self.TOP_Y, self.BOTTOM_Y
        c0, c1 = self.COIL
        w = dict(color=INK, stroke_width=3)

        coil = ParametricFunction(
            lambda u: np.array([c0 + (c1 - c0) * u - 0.16 * np.sin(2 * PI * 6 * u),
                                top + 0.1 * (1 - np.cos(2 * PI * 6 * u)), 0]),
            t_range=[0, 1, 0.002], **w)
        mid = (c0 + c1) / 2
        gap_l, gap_r = mid - 0.12, mid + 0.12
        self.gap = (np.array([gap_l, self.GAP_Y, 0]), np.array([gap_r, self.GAP_Y, 0]))
        battery_x = 4.3
        sw_a, sw_b = np.array([2.7, bot, 0]), np.array([3.3, bot, 0])
        self.switch_hinge, self.switch_end = sw_a, sw_b

        wires = VGroup(
            Line([l, top, 0], [c0, top, 0], **w), Line([c1, top, 0], [r, top, 0], **w),
            Line([r, top, 0], [r, bot, 0], **w), Line([l, bot, 0], [l, top, 0], **w),
            Line([r, bot, 0], [battery_x + 0.12, bot, 0], **w),
            Line([battery_x - 0.12, bot, 0], sw_b, **w), Line(sw_a, [l, bot, 0], **w),
            # the spark-gap branch across the coil
            Line([c0, top, 0], [c0, self.GAP_Y, 0], **w), Line([c0, self.GAP_Y, 0], self.gap[0], **w),
            Line([c1, top, 0], [c1, self.GAP_Y, 0], **w), Line([c1, self.GAP_Y, 0], self.gap[1], **w),
        )
        battery = VGroup(Line([battery_x + 0.12, bot - 0.28, 0], [battery_x + 0.12, bot + 0.28, 0], **w),
                         Line([battery_x - 0.12, bot - 0.15, 0], [battery_x - 0.12, bot + 0.15, 0],
                              color=INK, stroke_width=6))
        electrodes = VGroup(*[Dot(p, radius=0.05, color=INK) for p in self.gap])
        terminals = VGroup(*[Dot(p, radius=0.05, color=INK) for p in (sw_a, sw_b)])
        self.lever = Line(sw_a, sw_b, color=INK, stroke_width=3.5)
        self.coil = coil
        self.label = txt("voltage across a coil", SIZE_LABEL, AVG, BOLD).next_to([mid, top + 0.25, 0], UP, buff=0.1)
        self.body = VGroup(wires, coil, battery, electrodes, terminals, self.lever)

    def open_switch(self):
        return Rotate(self.lever, angle=PI / 5, about_point=self.switch_hinge)

    def spark(self):
        a, b = self.gap
        pts = [a + RIGHT * 0.03]
        for k, frac in enumerate(np.linspace(0, 1, 6)[1:-1]):
            pts.append(interpolate(a, b, frac) + UP * (0.09 if k % 2 == 0 else -0.09))
        pts.append(b + LEFT * 0.03)
        bolt = VMobject(color=GOLD, stroke_width=5).set_points_as_corners(pts).set_z_index(6)
        glow = Circle(radius=0.3, stroke_width=0, fill_color=GOLD, fill_opacity=0.35).move_to((a + b) / 2)
        return VGroup(glow, bolt)


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
        for row in (self.row_5_1, self.row_5_2, self.row_5_3, self.row_5_6, self.row_5_7, self.row_5_8,
                    self.row_5_9):
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
        lower_third = VGroup(plate, caption, strip.next_to(plate, LEFT, buff=0)).move_to([PANEL_X, -2.6, 0])
        self.at("the curve flattening", FadeIn(lower_third, shift=UP * 0.2))

        rising = self.short_tangent(epi, 0, x, GOLD)
        flat = self.short_tangent(epi, 1, x, GOLD)
        self.at("still getting new cases every day", Create(rising), Indicate(marks[0], scale_factor=1.6))
        self.at("decreasing rate", Create(flat), Indicate(marks[2], scale_factor=1.6))
        self.flatten_bits = VGroup(cursor, marks, lower_third, rising, flat, self.epi_labels)

    def short_tangent(self, stack, k, x, color, half=0.7):
        f, ax = stack.funcs[k], stack.axes[k]
        slope = (f(x + 1e-4) - f(x - 1e-4)) / 2e-4
        p, q = ax.c2p(x, f(x)), ax.c2p(x + 1, f(x) + slope)
        d = (q - p) / np.linalg.norm(q - p)
        return Line(p - d * half, p + d * half, color=color, stroke_width=4).set_z_index(4)

    # ------------------------------------------------------------------
    # 5.8  The same stack for a wire and a coil
    # ------------------------------------------------------------------
    def row_5_8(self):
        self.row("5.8_coil", "Or take the charge")
        epi = self.epi
        wire = self.wire = wire_stack()
        circuit = CoilCircuit()
        self.at("Or take the charge", FadeOut(self.flatten_bits), FadeOut(epi.curves),
                *epi.morph_to(wire, curves=False), FadeIn(circuit.body), run_time=1.2)
        u = ValueTracker(0.02)
        growing = VGroup(*[wire.growing(k, u) for k in range(3)])
        self.add(growing)
        self.span("that has flowed through a wire", "the current changes", u.animate.set_value(T_OFF - 0.05),
                  Succession(Indicate(wire.titles[0], color=CURVE, scale_factor=1.15, run_time=1), Wait(0.6),
                             Indicate(wire.titles[1], color=AVG, scale_factor=1.15, run_time=1), Wait(2.5)),
                  rate_func=linear)
        spark = circuit.spark()
        self.at("produces a voltage across a coil", circuit.open_switch(), u.animate.set_value(T_OFF + 0.6),
                run_time=0.6, rate_func=linear)
        self.play(FadeIn(spark, scale=0.5), FadeIn(circuit.label), run_time=0.25)
        self.play(FadeOut(spark), u.animate.set_value(10), run_time=1.2, rate_func=linear)
        self.remove(growing)
        self.add(wire.curves)
        again = circuit.spark()
        self.at("into a spark", FadeIn(again, scale=0.5), run_time=0.25)
        self.play(FadeOut(again), run_time=0.5)
        self.circuit = VGroup(circuit.body, circuit.label)

    # ------------------------------------------------------------------
    # 5.9  Three stacks side by side: derivative, derivative of a derivative
    # ------------------------------------------------------------------
    def row_5_9(self):
        self.row("5.9_side_by_side", "Whenever you ask")
        wire = self.wire
        car, epi = car_stack(), epidemic_stack()
        thumbs = [car.group(), epi.group()]
        for g, slot in zip(thumbs, THUMB_SLOTS):
            g.scale(THUMB_SCALE).move_to(slot)
        self.at("Whenever you ask", FadeOut(self.circuit),
                wire.group().animate.scale(THUMB_SCALE).move_to(THUMB_SLOTS[2]),
                FadeIn(thumbs[0]), FadeIn(thumbs[1]), run_time=0.7)

        stacks = [car, epi, wire]
        first, second, guides = side_labels(wire)
        self.at("how fast something is changing", FadeIn(first[:-1]), Create(guides[0]),
                *[Indicate(st.arrows[0], color=AVG) for st in stacks])
        self.at("asking for a derivative", FadeIn(first[-1], shift=UP * 0.1))
        self.at("whether that change is speeding up", FadeIn(second[:-1]), Create(guides[1]),
                *[Indicate(st.arrows[1], color=AVG) for st in stacks])
        self.at("the derivative of a derivative", FadeIn(second[-1], shift=UP * 0.1))
        self.finish("the derivative of a derivative")
