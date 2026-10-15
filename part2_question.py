"""
Part 2 of the script: storyboard rows 2.1 to 2.9.

One scene with a section per storyboard row, so the car and graph carry over
between rows without a cut. There are no durations in this file: every step
names the words it belongs to, and timeline.py turns those into times, from
the Descript transcript if there is one, or estimated from narration/part2.txt.

Preview:   manim -pql part2_question.py Part2
Final:     manim -qh --fps 30 --save_sections part2_question.py Part2
"""

from style import *


class Part2(LessonScene):
    SCRIPT = "narration/part2.txt"

    def construct(self):
        # Shared state: one time value drives car, clock, graph dot and speedometer.
        self.t = ValueTracker(0)
        self.motion = Motion()
        self.road = make_road()
        self.car = car_on_road(self.t, self.motion)
        self.clock = make_clock(self.t)
        self.axes, self.axis_labels = make_axes()
        self.p0 = self.axes.c2p(0, 0)
        self.p1 = self.axes.c2p(T_TOTAL, D_TOTAL)

        self.row_2_1()
        self.row_2_2()
        self.row_2_3()
        self.row_2_4()
        self.row_2_5()
        self.row_2_6()
        self.row_2_7()
        self.row_2_8()
        self.row_2_9()

    def drive_to(self, seconds):
        """Animation: move the car (and everything tied to it) to a time on the clock."""
        return self.t.animate.set_value(seconds)

    # ------------------------------------------------------------------
    # 2.1  The trip
    # ------------------------------------------------------------------
    def row_2_1(self):
        self.row("2.1_trip", "Let's look at this")
        self.at("Let's look at this", FadeIn(self.road), FadeIn(self.car), FadeIn(self.clock), run_time=1.0)
        self.span("a car starting from rest", "stopping at the end", self.drive_to(T_TOTAL), rate_func=linear)

    # ------------------------------------------------------------------
    # 2.2  Other things that move
    # ------------------------------------------------------------------
    def row_2_2(self):
        self.row("2.2_why_motion", "Studying cars")
        ball, ball_motion = thrown_ball(center=np.array([-3.2, -1.3, 0]))
        orbit, orbit_motion = planet_orbit(center=np.array([3.2, -1.3, 0]))
        self.vignettes = VGroup(ball, orbit)
        self.at("Studying cars", FadeIn(self.vignettes))
        self.span("or more generally", "invent new mathematics", ball_motion, orbit_motion, rate_func=linear)

    # ------------------------------------------------------------------
    # 2.3  The empty graph; car back to the start
    # ------------------------------------------------------------------
    def row_2_3(self):
        self.row("2.3_what_can_we_say", "So what can we say")
        self.at("So what can we say", FadeOut(self.vignettes), Create(self.axes), FadeIn(self.axis_labels),
                run_time=1.2)
        self.at("this moving car", self.drive_to(0), run_time=1.2, rate_func=smooth)

    # ------------------------------------------------------------------
    # 2.4  The two facts we have
    # ------------------------------------------------------------------
    def row_2_4(self):
        self.row("2.4_two_points", "Well, we can say")
        self.start_pt = labelled_dot(self.p0, "(0 s, 0 m)", UR)
        self.end_pt = labelled_dot(self.p1, "(10 s, 250 m)", RIGHT)
        self.at("took 10 seconds", FadeIn(self.start_pt, scale=0.6))
        self.at("cover 250 metres", FadeIn(self.end_pt, scale=0.6))

    # ------------------------------------------------------------------
    # 2.5  A straight line would mean an instant jump in speed
    # ------------------------------------------------------------------
    def row_2_5(self):
        self.row("2.5_not_a_straight_line", "We know that the car")
        self.straight = dotted(self.p0, self.p1, CURVE, 4).set_z_index(1)
        self.speedo = make_speedometer(lambda: self.motion.speed(self.t.get_value()), **SPEEDO_SMALL)
        self.at("couldn't possibly be a straight line", Create(self.straight), run_time=1.5)
        self.at("because that means", FadeIn(self.speedo))

        self.motion.use(s_constant, v_constant)
        line_dot = Dot(self.p0, radius=0.09, color=CURVE, stroke_color=BG, stroke_width=3).set_z_index(3)
        line_dot.add_updater(lambda m: m.move_to(self.axes.c2p(self.t.get_value(), s_constant(self.t.get_value()))))
        self.add(line_dot)
        self.span("a constant speed", "the entire duration", self.drive_to(T_TOTAL), rate_func=linear)

        self.at("infinite acceleration",
                self.straight.animate.set_color(MUTED).set_stroke(width=3),
                FadeOut(line_dot), FadeOut(self.start_pt[1]), run_time=1.0)
        self.motion.use(s, v_parked)          # needle stays at 0 while rewinding
        self.at("which we know", self.drive_to(0), run_time=1.0, rate_func=smooth)
        self.motion.use(s, v)

    # ------------------------------------------------------------------
    # 2.6  The real curve
    # ------------------------------------------------------------------
    def row_2_6(self):
        self.row("2.6_the_real_curve", "So a more realistic curve")
        self.tracker = CurveTracker(self.axes, self.t)
        self.tracker.begin(self)
        self.span("starts out flat", "as it brakes", self.drive_to(T_TOTAL), rate_func=linear)
        self.tracker.settle(self)

    # ------------------------------------------------------------------
    # 2.7  Average speed
    # ------------------------------------------------------------------
    def row_2_7(self):
        self.row("2.7_average_speed", "And another thing")
        self.build_formula_chain()     # laid out whole now; 2.7 shows the right end, 2.8 the left

        self.at("And another thing", FadeOut(self.speedo), FadeOut(self.end_pt[1]))
        corner = self.axes.c2p(T_TOTAL, 0)
        self.run_line, self.rise_line = dotted(self.p0, corner), dotted(corner, self.p1)
        dist_val = txt("250 m", SIZE_LABEL, MUTED, MEDIUM).next_to(self.rise_line, RIGHT, buff=0.14)
        time_val = txt("10 s", SIZE_LABEL, MUTED, MEDIUM).next_to(self.axes.c2p(7.5, 0), UP, buff=0.12)
        self.at("the average speed",
                LaggedStart(AnimationGroup(Create(self.run_line), FadeIn(time_val)),
                            AnimationGroup(Create(self.rise_line), FadeIn(dist_val)), lag_ratio=0.5),
                run_time=1.6)
        # the two values leave the chart and become the fraction
        frac = self.chain["frac"]
        self.at("250 metres divided by",
                FadeIn(self.heading),
                ReplacementTransform(dist_val, frac[0]), ReplacementTransform(time_val, frac[2]),
                Create(frac[1]), run_time=1.4)
        self.at("meaning 25", FadeIn(self.chain["eq3"]), FadeIn(self.chain["result"], shift=LEFT * 0.2))

    def build_formula_chain(self):
        """gradient(A) = rise/run = 250 m / 10 s = 25 m/s, plus its heading."""
        F = SIZE_FORMULA
        parts = dict(
            grad=VGroup(txt("gradient(", F), txt("A", F, AVG, BOLD), txt(")", F)).arrange(RIGHT, buff=0.03),
            eq1=txt("=", F),
            rr=fraction("rise", "run", F),
            eq2=txt("=", F),
            frac=fraction("250 m", "10 s", F),
            eq3=txt("=", F),
            result=txt("25 m/s", F, AVG, BOLD),
        )
        row = VGroup(*parts.values()).arrange(RIGHT, buff=0.16)
        row.move_to([0, FORMULA_Y, 0]).align_to(np.array([PANEL_RIGHT, 0, 0]), RIGHT)
        self.chain = parts
        self.chain_row = row
        self.heading = VGroup(txt("average", SIZE_LABEL, AVG, MEDIUM), txt("speed", SIZE_LABEL, INK, MEDIUM))
        self.heading.arrange(RIGHT, buff=0.14, aligned_edge=DOWN)
        self.heading.next_to(parts["frac"], UP, buff=0.45).align_to(parts["frac"], LEFT)

    # ------------------------------------------------------------------
    # 2.8  Gradient = rise over run = distance over time
    # ------------------------------------------------------------------
    def row_2_8(self):
        self.row("2.8_gradient", "This is also exactly")
        c = self.chain
        self.label_a = txt("A", SIZE_LABEL + 2, AVG, BOLD).move_to(
            (self.p0 + self.p1) / 2 + np.array([-0.3, 0.32, 0]))
        self.at("the gradient of the straight line",
                self.straight.animate.set_color(AVG).set_stroke(width=4),
                FadeIn(self.label_a, scale=0.7), FadeIn(c["grad"]), FadeIn(c["eq1"]), run_time=1.4)
        self.at("rise over run",
                FadeIn(c["rr"]), FadeIn(c["eq2"]),
                Indicate(VGroup(self.run_line, self.rise_line), color=INK, scale_factor=1.0), run_time=1.2)

        dt = fraction("distance", "time")
        self.dt_row = VGroup(dt, txt("=", SIZE_FORMULA), txt("speed", SIZE_FORMULA, ACCENT, BOLD))
        self.dt_row.arrange(RIGHT, buff=0.2).next_to(self.chain_row, DOWN, buff=0.7).align_to(c["rr"], LEFT)
        self.at("rise is distance", TransformFromCopy(c["rr"], dt), FadeIn(self.dt_row[1:]), run_time=1.6)

    # ------------------------------------------------------------------
    # 2.9  The speedometer question
    # ------------------------------------------------------------------
    def row_2_9(self):
        self.row("2.9_speedometer_question", "But let's play this again")
        self.at("But let's play this again",
                FadeOut(VGroup(self.run_line, self.rise_line, self.straight, self.label_a,
                               self.heading, self.chain_row, self.dt_row)), run_time=1.0)
        speedo = make_speedometer(lambda: self.motion.speed(self.t.get_value()), **SPEEDO_LARGE)
        self.at("looking at the speedometer", FadeIn(speedo, scale=0.85))
        self.play(self.drive_to(0), run_time=0.8, rate_func=smooth)   # straight after the fade
        self.tracker.show_guides(self)
        self.span("How does this speedometer", "every instant", self.drive_to(4.0),
                  rate_func=rate_functions.ease_out_cubic)
        question = txt("?", SIZE_BIG, AVG, BOLD).next_to(speedo, LEFT, buff=0.35)
        self.at("Can the maths", FadeIn(question, scale=0.6),
                Flash(self.tracker.dot, color=AVG, line_length=0.16, flash_radius=0.24))
        self.finish("help us with this?")


# ----------------------------------------------------------------------
# 2.2 vignettes: small, flat, same palette as the car. Each returns
# (mobjects, animation of the motion).
# ----------------------------------------------------------------------
def thrown_ball(center, width=4.2, height=1.7):
    ground = Line(center + np.array([-width / 2, -1.0, 0]), center + np.array([width / 2, -1.0, 0]),
                  color=INK, stroke_width=2)
    start = center + np.array([-width / 2 + 0.3, -1.0, 0])
    path = ParametricFunction(lambda u: start + np.array([u * (width - 0.6), 4 * height * u * (1 - u), 0]),
                              t_range=[0, 1], color=MUTED, stroke_width=2)
    ball = Dot(start, radius=0.11, color=CURVE)
    label = txt("a thrown ball", SIZE_TICK, MUTED).next_to(ground, DOWN, buff=0.18)
    return VGroup(ground, DashedVMobject(path, num_dashes=28), ball, label), MoveAlongPath(ball, path)


def planet_orbit(center):
    sun = Dot(center, radius=0.16, color=GOLD)
    ring = Ellipse(width=3.2, height=1.9, color=MUTED, stroke_width=2).move_to(center)
    planet = Dot(ring.point_from_proportion(0), radius=0.09, color=CURVE)
    label = txt("a planet in orbit", SIZE_TICK, MUTED).next_to(ring, DOWN, buff=0.18)
    return VGroup(ring, sun, planet, label), MoveAlongPath(planet, ring)
