"""
Part 1 of the script: storyboard rows 1.1 to 1.3, then the handoff to part 2.

1.1  Title question; a thrown ball and a planet in orbit, moving the whole time,
     with "calculus" and "differentiation" between them.
1.2  "change".
1.3  The car's three graphs stacked on the left, a speedometer on the right and
     a small car under the graphs, all driven by one clock. The small car then
     moves up to become part 2's car on the road (the handoff), so the two clips
     join without a visible cut.

Preview:   manim -pql part1_intro.py Part1
Final:     manim -qh --fps 30 --save_sections part1_intro.py Part1
"""

from style import *

STACK_SCALE = 0.72                         # the three graphs in 1.3
STACK_CENTER = np.array([-3.4, 0.3, 0])
MINI_ROAD_Y = -3.05                        # the small car's road under the graphs
SPEEDO_1_3 = dict(center=np.array([3.4, -0.2, 0]), radius=1.7)


class Part1(LessonScene):
    SCRIPT = "narration/part1.txt"
    SPEEDO = SPEEDO_1_3
    NEXT_START = ('study "change"', 1.7)    # part 1 ends with the handoff, 1.7 s after this

    def construct(self):
        self.row_1_1()
        self.row_1_2()
        self.row_1_3()
        self.handoff_to_part2()

    # ------------------------------------------------------------------
    # 1.1  Title question; a thrown ball and an orbit; calculus and differentiation
    # ------------------------------------------------------------------
    def row_1_1(self):
        self.row("1.1_title", "In this video")
        title = txt("What do we use derivatives for?", 40, INK, MEDIUM).move_to(UP * 3.2)
        calculus = txt("calculus", 34, INK).move_to(UP * 0.1)
        diff = txt("differentiation", 28, AVG).next_to(calculus, DOWN, buff=0.7)
        link = Line(calculus.get_bottom() + DOWN * 0.1, diff.get_top() + UP * 0.1, color=MUTED, stroke_width=2)

        self.at("In this video", FadeIn(title, shift=UP * 0.15), run_time=1.0)
        self.at("introduce calculus", FadeIn(calculus))
        self.at("more specifically", Create(link), FadeIn(diff, shift=DOWN * 0.1))

        # left and right: two things whose speed keeps changing, both moving the whole time
        ball = thrown_ball(np.array([-4.5, -0.6, 0]))
        orbit = planet_orbit(np.array([4.5, -0.6, 0]))
        self.at("in such a way", FadeIn(ball, shift=UP * 0.15), run_time=0.8)
        self.at("why mathematicians", FadeIn(orbit, shift=UP * 0.15), run_time=0.8)
        self.opening = VGroup(title, calculus, link, diff, ball, orbit)

    # ------------------------------------------------------------------
    # 1.2  "change"
    # ------------------------------------------------------------------
    def row_1_2(self):
        self.row("1.2_change", "After all")
        self.change = txt("change", 72, INK, slant=ITALIC)
        self.at("After all", FadeOut(self.opening))
        self.at("the mathematics of change", FadeIn(self.change, scale=0.9), run_time=0.8)
        self.play(ApplyWave(self.change, amplitude=0.12, wave_func=smooth), run_time=0.7)   # the word itself changes

    # ------------------------------------------------------------------
    # 1.3  Three graphs, speedometer and a small car, all on one clock
    # ------------------------------------------------------------------
    def row_1_3(self):
        self.row("1.3_graphs_and_speedometer", "and there has to be")
        stack = car_stack()
        stack.group().scale(STACK_SCALE).move_to(STACK_CENTER)
        u = self.u = ValueTracker(0.0)
        speedo = make_speedometer(lambda: v(u.get_value()), **self.SPEEDO)
        view = self.drive_view(u)
        x0, x1 = stack.axes[2].c2p(0, 0)[0], stack.axes[2].c2p(T_TOTAL, 0)[0]
        mini_road = Line([x0 - 0.2, MINI_ROAD_Y, 0], [x1 + 0.2, MINI_ROAD_Y, 0], color=INK, stroke_width=2)
        self.mini_car = make_car().scale(0.6)
        self.mini_car.add_updater(lambda m: m.move_to(
            [interpolate(x0, x1, s(u.get_value()) / D_TOTAL), MINI_ROAD_Y, 0], aligned_edge=DOWN))
        self.mini_car.update()

        self.at("and there has to be", self.change.animate.scale(0.45).move_to(UP * 3.6),
                FadeIn(stack.frame()), FadeIn(view), FadeIn(speedo), Create(mini_road), FadeIn(self.mini_car),
                run_time=1.0)
        curves = VGroup(*[stack.growing(k, u) for k in range(3)])
        dots = stack.dots(u)
        self.add(curves, dots)
        self.span("a good reason", 'study "change"', u.animate.set_value(T_TOTAL), rate_func=linear)
        self.remove(curves)
        self.add(stack.curves)
        self.mini_car.clear_updaters()
        self.rest = VGroup(stack.group(), dots, view, speedo, mini_road, self.change)

    def drive_view(self, u):
        """What sits behind the speedometer in 1.3; nothing here (part1-B adds a windscreen)."""
        return VGroup()

    # ------------------------------------------------------------------
    # Handoff: the small car moves up and becomes part 2's car on the road
    # ------------------------------------------------------------------
    def handoff_to_part2(self):
        self.next_section("1.4_handoff")
        t = ValueTracker(0)
        road, car, clock = opening_layout(t, Motion())
        target = car.copy().clear_updaters()
        k = max(self.clip_end() - self.now, 0.8) / 2.2     # fit the handoff into the time before part 2
        self.play(FadeOut(self.rest), run_time=0.8 * k)
        self.play(Transform(self.mini_car, target), FadeIn(road), FadeIn(clock), run_time=1.4 * k)
        self.remove(self.mini_car)
        self.add(car)
        self.finish('study "change"')


# ----------------------------------------------------------------------
# The two moving clips in 1.1
# ----------------------------------------------------------------------
SPACE = "#1D1F26"            # the inside of the orbit


def thrown_ball(center, width=4.2, height=1.7, period=2.2):
    """A ball thrown over a pine tree, again and again (its own clock, no cues needed)."""
    ground = Line(center + np.array([-width / 2, -1.0, 0]), center + np.array([width / 2, -1.0, 0]),
                  color=INK, stroke_width=2)
    start = center + np.array([-width / 2 + 0.3, -1.0, 0])
    arc = lambda u: start + np.array([u * (width - 0.6), 4 * height * u * (1 - u), 0])
    path = ParametricFunction(arc, t_range=[0, 1], color=MUTED, stroke_width=2)
    tree = pine_tree(center + np.array([-0.9, -1.0, 0]), 0.95)
    ball = Dot(start, radius=0.12, color=AVG).set_z_index(2)
    clock = {"t": 0.0}

    def fly(m, dt):
        clock["t"] += dt
        m.move_to(arc((clock["t"] / period) % 1.0))

    ball.add_updater(fly)
    label = txt("a thrown ball", SIZE_TICK, MUTED).next_to(ground, DOWN, buff=0.18)
    return VGroup(tree, ground, DashedVMobject(path, num_dashes=28), ball, label)


def planet_orbit(center, a=1.6, b=1.1, period=5.0):
    """
    A planet on an ellipse with the sun at one focus, moving by Kepler's law, so it
    speeds up as it swings close to the sun. Stars twinkle a little.
    """
    ring = Ellipse(width=2 * a, height=2 * b, color=MUTED, stroke_width=2, fill_color=SPACE,
                   fill_opacity=1).move_to(center)
    e = np.sqrt(1 - (b / a) ** 2)
    focus = center + np.array([a * e, 0, 0])
    sun = VGroup(Circle(radius=0.26, stroke_width=0, fill_color=GOLD, fill_opacity=0.25),
                 Circle(radius=0.15, stroke_width=0, fill_color=GOLD, fill_opacity=1)).move_to(focus)
    rng = np.random.default_rng(11)
    stars = VGroup()
    while len(stars) < 28:
        x, y = rng.uniform(-1, 1, 2)
        p = center + np.array([x * a * 0.92, y * b * 0.92, 0])
        if x * x + y * y < 0.85 and np.linalg.norm(p - focus) > 0.35:
            stars.add(Dot(p, radius=rng.uniform(0.012, 0.03), color=WHITE))
    phases = rng.uniform(0, TAU, len(stars))
    clock = {"t": 0.0}

    def position(t):
        mean = TAU * t / period
        E = mean
        for _ in range(6):                        # solve Kepler's equation E - e sin E = M
            E -= (E - e * np.sin(E) - mean) / (1 - e * np.cos(E))
        return center + np.array([a * np.cos(E), b * np.sin(E), 0])

    planet = Dot(position(0), radius=0.09, color=CURVE).set_z_index(2)

    def orbit(m, dt):
        clock["t"] += dt
        m.move_to(position(clock["t"]))
        for star, ph in zip(stars, phases):
            star.set_opacity(0.55 + 0.45 * np.sin(2.2 * clock["t"] + ph))

    planet.add_updater(orbit)
    label = txt("a planet in orbit", SIZE_TICK, MUTED).next_to(ring, DOWN, buff=0.18)
    return VGroup(ring, stars, sun, planet, label)
