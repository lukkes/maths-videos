"""
Shared look and building blocks for every scene in the video.

Anything used by more than one storyboard row lives here: palette, type sizes,
layout positions, the car's motion, and components (road, car, clock, axes,
the curve that traces the car, speedometer, fractions). Scene files import
from this module and only describe what happens, and when.
"""

import manimpango
import numpy as np
from manim import *

from timeline import TimedScene

# ==========================================================================
# Palette. Each colour has one job.
# ==========================================================================
BG = "#F4EEE1"      # cream background
PAPER = "#EAE2D1"   # panels, the speedometer face
INK = "#2E2B27"     # text, axes, the road
MUTED = "#8E8676"   # tick labels, axis titles, guides, rejected lines
CURVE = "#3F6E8C"   # the car and everything that tracks it (dusty blue)
AVG = "#C65D3B"     # averages, gradients, the speedometer needle (terracotta)
WRONG = "#B23A3A"   # contradictions
ACCENT = "#6B8F4E"  # results (olive)
GOLD = "#D9A23F"    # highlights, the sun

# ==========================================================================
# Type. Sizes are in Manim font-size units.
# ==========================================================================
FONT = "Inter" if "Inter" in manimpango.list_fonts() else ""

SIZE_TICK = 22      # axis numbers, road marks, axis titles, small captions
SIZE_LABEL = 24     # labels on the chart, headings over formulas
SIZE_FORMULA = 23   # inline formula chains on the right panel
SIZE_CLOCK = 30     # t = 0.0 s
SIZE_READING = 34   # speedometer number
SIZE_BIG = 72       # single-glyph emphasis, like "?"


def txt(s, size=SIZE_LABEL, color=INK, weight=NORMAL, slant=NORMAL):
    """Text rendered large and scaled down; Pango kerns badly at small sizes."""
    return Text(s, font=FONT, weight=weight, slant=slant, color=color, font_size=96).scale(size / 96)


def num(s, size=SIZE_LABEL, color=INK, weight=NORMAL):
    """Like txt, but every digit has the same width, for numbers that change on screen."""
    m = MarkupText(f'<span font_features="tnum">{s}</span>',
                   font=FONT, weight=weight, color=color, font_size=96)
    return m.scale(size / 96)


def fraction(top, bottom, size=SIZE_FORMULA, color=INK, weight=NORMAL):
    """A stacked fraction built from text, no LaTeX."""
    a, b = txt(top, size, color, weight), txt(bottom, size, color, weight)
    bar = Line(LEFT, RIGHT, color=color, stroke_width=2.5)
    bar.stretch_to_fit_width(max(a.width, b.width) + 0.16)
    return VGroup(a, bar, b).arrange(DOWN, buff=0.12)


def dotted(a, b, color=MUTED, width=3):
    """A dotted straight line from a to b."""
    return DashedLine(a, b, color=color, stroke_width=width, dash_length=0.06, dashed_ratio=0.5)


# ==========================================================================
# Layout. The screen is 14.2 x 8 units, origin in the centre.
# Top band: clock and road. Bottom left: the graph. Bottom right: the panel
# for formulas and the speedometer.
# ==========================================================================
ROAD_Y = 2.15
ROAD_X0, ROAD_X1 = -5.2, 5.2
CLOCK_POS = np.array([-0.85, 3.3, 0])     # left edge of "t = 0.0 s"
AXES_ORIGIN = np.array([-5.6, -2.75, 0])  # where (0, 0) of the graph sits
AXES_SIZE = (6.4, 3.5)

PANEL_RIGHT = 6.9                         # right edge for text in the panel
FORMULA_Y = -0.35
SPEEDO_SMALL = dict(center=np.array([4.3, -0.9, 0]), radius=1.15)
SPEEDO_LARGE = dict(center=np.array([4.2, -0.75, 0]), radius=1.6)

# ==========================================================================
# The car's motion: 250 m in 10 s.
# Speeds up for 5 s with s = 5t^2, then brakes symmetrically to a stop.
# Part 4's numbers (80 m at 4 s, 84.05 m at 4.1 s) come from this function.
# ==========================================================================
T_TOTAL = 10.0
D_TOTAL = 250.0
AVG_SPEED = D_TOTAL / T_TOTAL  # 25 m/s


def s(t):
    t = float(np.clip(t, 0, T_TOTAL))
    return 5 * t**2 if t <= 5 else D_TOTAL - 5 * (T_TOTAL - t) ** 2


def v(t):
    t = float(np.clip(t, 0, T_TOTAL))
    return 10 * t if t <= 5 else 10 * (T_TOTAL - t)


def s_constant(t):
    """The impossible constant-speed version of the same trip."""
    return AVG_SPEED * float(np.clip(t, 0, T_TOTAL))


def v_constant(t):
    """25 m/s while moving: jumps up at the start, drops to 0 at the end."""
    return AVG_SPEED if 0 < t < T_TOTAL else 0.0


def v_parked(_t):
    return 0.0


class Motion:
    """Which motion the car and speedometer follow. Switch it mid-scene with use()."""

    def __init__(self, pos=s, speed=v):
        self.pos, self.speed = pos, speed

    def use(self, pos=s, speed=v):
        self.pos, self.speed = pos, speed


# ==========================================================================
# Components
# ==========================================================================
def road_point(d):
    """Screen point on the road for a distance d in metres."""
    return np.array([interpolate(ROAD_X0, ROAD_X1, d / D_TOTAL), ROAD_Y, 0])


# Scenery behind the road: low-contrast colours so the car, road and clock stay on top.
SKY = "#D5E3EA"
MOUNTAIN_FAR = "#C3D1D6"
MOUNTAIN_NEAR = "#B3C2C2"
PINE = "#8FA889"
PINE_DARK = "#7E9878"
POLE = "#9A8B7A"
WIRE = "#7D776F"


def pine_tree(base, height):
    """A pine: three stacked triangles on a short trunk, standing on `base`."""
    w = height * 0.55
    trunk = Rectangle(width=w * 0.14, height=height * 0.16, fill_color=POLE, fill_opacity=1, stroke_width=0)
    trunk.move_to(base, aligned_edge=DOWN)
    tiers = VGroup()
    for k, (frac_w, y0, y1) in enumerate([(1.0, 0.12, 0.55), (0.8, 0.35, 0.8), (0.58, 0.58, 1.0)]):
        tiers.add(Polygon(base + np.array([-w * frac_w / 2, height * y0, 0]),
                          base + np.array([w * frac_w / 2, height * y0, 0]),
                          base + np.array([0, height * y1, 0]),
                          fill_color=PINE if k % 2 == 0 else PINE_DARK, fill_opacity=1, stroke_width=0))
    return VGroup(trunk, tiers)


def mountain_range(y0, peaks, color, seed):
    """A ridge from the left edge of the screen to the right, `peaks` high points, base at y0."""
    rng = np.random.default_rng(seed)
    x0, x1 = -config.frame_width / 2, config.frame_width / 2
    xs = np.linspace(x0, x1, 2 * peaks + 1)
    ys = [y0 + (rng.uniform(0.45, 0.85) if i % 2 else rng.uniform(0.1, 0.3)) for i in range(len(xs))]
    pts = [np.array([x0, y0, 0])] + [np.array([x, y, 0]) for x, y in zip(xs, ys)] + [np.array([x1, y0, 0])]
    ridge = Polygon(*pts, fill_color=color, fill_opacity=1, stroke_width=0)
    ridge.bleed = True
    return ridge


def power_lines(y0, xs, height=0.85):
    """Poles at the given x positions, joined by two wires that sag a little between poles."""
    poles, wires = VGroup(), VGroup()
    tops = []
    for x in xs:
        pole = Line([x, y0, 0], [x, y0 + height, 0], color=POLE, stroke_width=3)
        arm = Line([x - 0.16, y0 + height - 0.08, 0], [x + 0.16, y0 + height - 0.08, 0], color=POLE, stroke_width=3)
        poles.add(pole, arm)
        tops.append((x, y0 + height - 0.08))
    for (xa, ya), (xb, yb) in zip(tops, tops[1:]):
        for dx in (-0.14, 0.14):
            wires.add(ParametricFunction(
                lambda u, xa=xa, xb=xb, ya=ya, dx=dx: np.array(
                    [interpolate(xa, xb, u) + dx, ya - 0.18 * 4 * u * (1 - u), 0]),
                t_range=[0, 1, 0.05], color=WIRE, stroke_width=1.3))
    return VGroup(wires, poles)


SUN_POS = np.array([5.75, 3.35, 0])


def make_sun(center=SUN_POS, radius=0.3):
    """
    A cartoon sun that never stops moving: two rings of short rays turning slowly in
    opposite directions, and a halo that breathes. Driven by its own clock (dt
    updaters), so it keeps going through every wait and animation without any cue.
    """
    halo = Circle(radius=radius * 1.55, stroke_width=0, fill_color=GOLD, fill_opacity=0.18).move_to(center)
    disc = Circle(radius=radius, stroke_width=0, fill_color=GOLD, fill_opacity=1).move_to(center)

    def ring(n, r0, r1, width, opacity, phase=0.0):
        rays = VGroup()
        for k in range(n):
            a = TAU * k / n + phase
            d = np.array([np.cos(a), np.sin(a), 0])
            rays.add(Line(center + d * r0, center + d * r1, color=GOLD, stroke_width=width,
                          stroke_opacity=opacity).set_cap_style(CapStyleType.ROUND))
        return rays

    long_rays = ring(10, radius * 1.3, radius * 1.85, 4, 0.9)
    short_rays = ring(10, radius * 1.3, radius * 1.6, 3, 0.6, phase=TAU / 20)
    clock = {"t": 0.0}

    def tick(m, dt):
        clock["t"] += dt
        long_rays.rotate(0.22 * dt, about_point=center)
        short_rays.rotate(-0.15 * dt, about_point=center)
        target = radius * 1.55 * (1 + 0.06 * np.sin(clock["t"] * 1.8))
        halo.scale(target / (halo.width / 2), about_point=center)

    sun = VGroup(halo, long_rays, short_rays, disc)
    sun.add_updater(tick)
    return sun


def make_scenery():
    """Sky, two mountain ranges, pine trees and power lines behind the road."""
    top = config.frame_height / 2
    sky = Rectangle(width=config.frame_width, height=top - ROAD_Y, fill_color=SKY, fill_opacity=1, stroke_width=0)
    sky.move_to([0, (top + ROAD_Y) / 2, 0])
    sky.bleed = True
    far = mountain_range(ROAD_Y, 5, MOUNTAIN_FAR, seed=4).stretch(1.0, 1).shift(UP * 0.12)
    near = mountain_range(ROAD_Y, 7, MOUNTAIN_NEAR, seed=9)
    rng = np.random.default_rng(7)
    trees = VGroup(*[pine_tree(np.array([x, ROAD_Y + 0.02, 0]), rng.uniform(0.35, 0.6))
                     for x in (-6.6, -6.25, -4.3, -3.95, -1.8, 1.4, 1.75, 3.6, 5.6, 5.95, 6.5)])
    lines = power_lines(ROAD_Y + 0.02, np.arange(-6.4, 6.6, 2.55))
    return VGroup(sky, make_sun(), far, near, trees, lines).set_z_index(-5)


def make_road():
    """Scenery, road and distance marks."""
    road = Line([ROAD_X0 - 0.9, ROAD_Y, 0], [ROAD_X1 + 0.9, ROAD_Y, 0], color=INK, stroke_width=3)
    marks = VGroup()
    for d in range(0, int(D_TOTAL) + 1, 50):
        tick = Line(ORIGIN, DOWN * 0.12, color=INK, stroke_width=2)
        tick.move_to(road_point(d), aligned_edge=UP)
        marks.add(tick, txt(f"{d} m", SIZE_TICK, MUTED).next_to(tick, DOWN, buff=0.1))
    return VGroup(make_scenery(), road, marks)


def make_car(color=CURVE):
    body = RoundedRectangle(width=1.0, height=0.26, corner_radius=0.09,
                            fill_color=color, fill_opacity=1, stroke_width=0)
    cabin = RoundedRectangle(width=0.52, height=0.26, corner_radius=0.09,
                             fill_color=color, fill_opacity=1, stroke_width=0)
    cabin.next_to(body, UP, buff=-0.08).shift(LEFT * 0.06)
    window = RoundedRectangle(width=0.34, height=0.11, corner_radius=0.04,
                              fill_color=BG, fill_opacity=1, stroke_width=0)
    window.move_to(cabin).shift(UP * 0.025)
    wheels = VGroup(*[
        Circle(radius=0.1, fill_color=INK, fill_opacity=1, stroke_color=BG,
               stroke_width=2).move_to(body.get_bottom() + RIGHT * dx)
        for dx in (-0.29, 0.29)
    ])
    return VGroup(cabin, body, window, wheels)


def car_on_road(t: ValueTracker, motion: Motion):
    """A car that always sits at motion.pos(t) on the road."""
    car = make_car()
    car.add_updater(lambda m: m.move_to(road_point(motion.pos(t.get_value())), aligned_edge=DOWN))
    car.update()
    return car


def opening_layout(t: ValueTracker, motion: Motion):
    """
    Road, car and clock as part 2 opens. Part 1 ends on exactly this frame and
    part 2 starts on it, so the cut between the two clips doesn't show.
    """
    return make_road(), car_on_road(t, motion), make_clock(t)


def tick_mark(size=0.32, color=ACCENT):
    """A drawn check mark (fonts don't all have the glyph)."""
    return VMobject(color=color, stroke_width=6).set_points_as_corners(
        [LEFT * 0.5 + UP * 0.05, DOWN * 0.4, RIGHT * 0.6 + UP * 0.6]).scale(size)


def make_clock(t: ValueTracker):
    return always_redraw(
        lambda: num(f"t = {t.get_value():.1f} s", SIZE_CLOCK).move_to(CLOCK_POS, aligned_edge=DL)
    )


def make_axes():
    """Distance-time axes, 0-10 s by 0-250 m. Returns (axes, labels)."""
    axes = Axes(
        x_range=[0, T_TOTAL, 1], y_range=[0, D_TOTAL, 50],
        x_length=AXES_SIZE[0], y_length=AXES_SIZE[1], tips=False,
        axis_config={"color": INK, "stroke_width": 2.5, "include_numbers": False, "tick_size": 0.06},
    )
    axes.shift(AXES_ORIGIN - axes.c2p(0, 0))
    labels = VGroup(
        *[txt(str(x), SIZE_TICK, MUTED).next_to(axes.c2p(x, 0), DOWN, buff=0.16) for x in range(0, 11, 2)],
        *[txt(str(y), SIZE_TICK, MUTED).next_to(axes.c2p(0, y), LEFT, buff=0.16) for y in range(50, 251, 50)],
        txt("time (s)", SIZE_TICK, MUTED).next_to(axes.c2p(5, 0), DOWN, buff=0.58),
        txt("distance (m)", SIZE_TICK, MUTED).next_to(axes.c2p(0, D_TOTAL), UP, buff=0.22)
        .align_to(axes.c2p(0, 0), LEFT),
    )
    return axes, labels


def labelled_dot(point, label, direction=UR, color=CURVE):
    dot = Dot(point, radius=0.11, color=color, stroke_color=BG, stroke_width=3).set_z_index(3)
    lab = num(label, SIZE_LABEL, color, MEDIUM).next_to(dot, direction, buff=0.14)
    return VGroup(dot, lab)


class CurveTracker:
    """
    The car's distance-time curve, drawn as the car moves: a growing trace, a
    dot at the current time, and dashed guides to both axes. Everything reads
    the same time tracker as the car.

        tracker = CurveTracker(axes, t)
        tracker.begin(scene)          # trace, dot and guides appear
        ... animate t ...
        tracker.settle(scene)         # trace becomes the full curve, guides go
    """

    def __init__(self, axes, t: ValueTracker, f=s, color=CURVE):
        self.axes, self.t, self.f = axes, t, f
        self.curve = axes.plot(f, x_range=[0, T_TOTAL], color=color, stroke_width=5).set_z_index(2)
        self.trace = self.curve.copy()
        self.trace.add_updater(
            lambda m: m.pointwise_become_partial(self.curve, 0, self.t.get_value() / T_TOTAL))
        self.trace.update()
        self.dot = Dot(radius=0.1, color=color, stroke_color=BG, stroke_width=3).set_z_index(3)
        self.dot.add_updater(lambda m: m.move_to(self.point()))
        self.dot.update()
        self.guides = always_redraw(self._guides)

    def point(self):
        x = self.t.get_value()
        return self.axes.c2p(x, self.f(x))

    def _guides(self):
        x = self.t.get_value()
        return VGroup(
            DashedLine(self.axes.c2p(0, self.f(x)), self.point(), color=MUTED, stroke_width=1.5, dash_length=0.06),
            DashedLine(self.axes.c2p(x, 0), self.point(), color=MUTED, stroke_width=1.5, dash_length=0.06),
        )

    def begin(self, scene):
        scene.add(self.trace, self.dot, self.guides)

    def settle(self, scene):
        scene.remove(self.trace, self.guides)
        scene.add(self.curve)

    def show_guides(self, scene):
        scene.add(self.guides)


def rise_run_triangle(axes, f, x, dx, color=AVG, width=3):
    """Run and rise of f between x and x + dx, drawn on the axes."""
    a, b = axes.c2p(x, f(x)), axes.c2p(x + dx, f(x))
    c = axes.c2p(x + dx, f(x + dx))
    return VGroup(Line(a, b, color=color, stroke_width=width), Line(b, c, color=color, stroke_width=width))


def secant(axes, f, x1, x2, color=AVG, extend=1.5, width=3):
    """The straight line through (x1, f(x1)) and (x2, f(x2)), drawn a little past both points."""
    line = Line(axes.c2p(x1, f(x1)), axes.c2p(x2, f(x2)), color=color, stroke_width=width)
    return line.scale(extend)


def gradient(f, x1, x2):
    return (f(x2) - f(x1)) / (x2 - x1)


def make_speedometer(read_speed, center, radius=1.25, max_speed=60):
    """
    A dial from 0 to max_speed m/s whose needle follows read_speed(), a function
    called every frame. Pass SPEEDO_SMALL or SPEEDO_LARGE as keyword arguments.
    """
    start, end = PI * 1.1, -PI * 0.1   # dial sweeps a little past horizontal

    def angle(val):
        return interpolate(start, end, np.clip(val, 0, max_speed) / max_speed)

    face = Circle(radius=radius * 1.12, fill_color=PAPER, fill_opacity=1, stroke_color=INK, stroke_width=2.5)
    arc = Arc(radius=radius, start_angle=start, angle=end - start, color=INK, stroke_width=3)
    ticks = VGroup()
    for k in range(0, max_speed + 1, 10):
        d = np.array([np.cos(angle(k)), np.sin(angle(k)), 0])
        ticks.add(Line(d * radius, d * (radius - 0.16), color=INK, stroke_width=2.5))
        ticks.add(txt(str(k), 18, MUTED).move_to(d * (radius - 0.36)))
    unit = txt("m/s", 18, MUTED).move_to(DOWN * radius * 0.42)
    dial = VGroup(face, arc, ticks, unit).move_to(center)
    hub = face.get_center()

    def needle_now():
        a = angle(read_speed())
        tip = hub + np.array([np.cos(a), np.sin(a), 0]) * radius * 0.88
        return VGroup(Line(hub, tip, color=AVG, stroke_width=5), Dot(hub, radius=0.07, color=INK))

    needle = always_redraw(needle_now)
    reading = always_redraw(
        lambda: num(f"{read_speed():.0f}", SIZE_READING, INK, MEDIUM).move_to(hub + DOWN * radius * 0.72))
    return VGroup(dial, needle, reading)


# ==========================================================================
# Base scene
# ==========================================================================
# ==========================================================================
# Formulas (LaTeX). Sans-serif maths so formulas sit well next to Inter.
# Pass formula parts as separate strings to address them later by index:
#     f = tex("5t^2", "+", "10t", "h")      f[2] is "10t"
# ==========================================================================
TEX = TexTemplate()
TEX.add_to_preamble(r"\usepackage[T1]{fontenc}\usepackage{helvet}"
                    r"\renewcommand{\familydefault}{\sfdefault}\usepackage{sansmath}\sansmath")
SIZE_TEX = 34       # formula size on the right panel
SIZE_TEX_SMALL = 26


def tex(*parts, size=SIZE_TEX, color=INK):
    return MathTex(*parts, tex_template=TEX, color=color, font_size=size)


def tex_frac(top_parts, bottom_parts, size=SIZE_TEX, color=INK):
    """A fraction whose top and bottom are separate tex objects, so each part stays addressable.
    Returns VGroup(top, bar, bottom)."""
    top, bottom = tex(*top_parts, size=size, color=color), tex(*bottom_parts, size=size, color=color)
    bar = Line(LEFT, RIGHT, color=color, stroke_width=2.5).stretch_to_fit_width(max(top.width, bottom.width) + 0.2)
    return VGroup(top, bar, bottom).arrange(DOWN, buff=0.12)


def strike(mob, color=WRONG, width=4):
    """A diagonal line through a mobject, for cancelling terms."""
    return Line(mob.get_corner(DL) + DL * 0.04, mob.get_corner(UR) + UR * 0.04, color=color, stroke_width=width)


# ==========================================================================
# Shared stage: what's on screen whenever the graph is showing.
# Parts build their opening and closing frames from this, so the frame one
# part ends on and the next part starts on are made by the same code.
# ==========================================================================
class GraphStage:
    def __init__(self, t_value=0.0):
        self.t = ValueTracker(t_value)
        self.motion = Motion()
        self.road, self.car, self.clock = opening_layout(self.t, self.motion)
        self.axes, self.axis_labels = make_axes()
        self.tracker = CurveTracker(self.axes, self.t)

    def base(self):
        """Road, car, clock, axes and the full curve."""
        return [self.road, self.car, self.clock, self.axes, self.axis_labels, self.tracker.curve]


# A close-up of the curve around t = 4, taller than the main graph and with a
# stronger vertical scale so the curve visibly bends and secants visibly tilt.
# It plots the formula 5t^2 itself (part 4 works with the formula).
ZOOM_X = (0, 6.2)
ZOOM_Y = (0, 190)
ZOOM_ORIGIN = np.array([-6.1, -3.35, 0])
ZOOM_SIZE = (5.0, 4.5)


def five_t_squared(t):
    return 5 * t * t


def make_zoomed_axes(f=five_t_squared, color=CURVE):
    """Close-up distance-time axes around t = 4. Returns (axes, labels, curve)."""
    axes = Axes(
        x_range=[ZOOM_X[0], ZOOM_X[1], 1], y_range=[ZOOM_Y[0], ZOOM_Y[1], 50],
        x_length=ZOOM_SIZE[0], y_length=ZOOM_SIZE[1], tips=False,
        axis_config={"color": INK, "stroke_width": 2.5, "include_numbers": False, "tick_size": 0.05},
    )
    axes.shift(ZOOM_ORIGIN - axes.c2p(ZOOM_X[0], ZOOM_Y[0]))
    labels = VGroup(
        *[txt(f"{x} s", SIZE_TICK, MUTED).next_to(axes.c2p(x, ZOOM_Y[0]), DOWN, buff=0.14) for x in (2, 4, 6)],
        *[txt(str(y), SIZE_TICK, MUTED).next_to(axes.c2p(ZOOM_X[0], y), LEFT, buff=0.14)
          for y in range(50, 151, 50)],
        txt("distance (m)", SIZE_TICK, MUTED).next_to(axes.c2p(ZOOM_X[0], ZOOM_Y[1]), UP, buff=0.14)
        .align_to(axes.c2p(ZOOM_X[0], ZOOM_Y[0]), LEFT),
    )
    curve = axes.plot(f, x_range=list(ZOOM_X), color=color, stroke_width=5).set_z_index(2)
    return axes, labels, curve


def clipped_line_points(axes, x0, y0, slope, half_width):
    """Endpoints (in data coordinates) of a line through (x0, y0), clipped to the axes ranges."""
    (xa, xb), (ya, yb) = axes.x_range[:2], axes.y_range[:2]
    pts = []
    for x in (x0 - half_width, x0 + half_width):
        x = float(np.clip(x, xa, xb))
        y = y0 + slope * (x - x0)
        if y < ya or y > yb:
            y = float(np.clip(y, ya, yb))
            x = x0 + (y - y0) / slope if slope else x
        pts.append((x, y))
    return pts


class Magnifier:
    """
    A boxed close-up of a small region of a graph, shown elsewhere on screen,
    with a lens circle on the graph and two lines linking lens and box.

        mag = Magnifier(axes, f, x_range=(3.95, 4.2), y_range=(78, 86), center=[3.2, -0.4, 0])
        scene.play(mag.show())
        dot = mag.live_dot(lambda: 4 + h.get_value(), AVG)
    """

    def __init__(self, axes, f, x_range, y_range, center, size=2.6, color=CURVE):
        self.main, self.f = axes, f
        self.inner = Axes(x_range=[*x_range, (x_range[1] - x_range[0]) / 5], y_range=[*y_range, 1],
                          x_length=size, y_length=size, tips=False,
                          axis_config={"stroke_opacity": 0, "include_ticks": False}).move_to(center)
        self.box = Square(side_length=size + 0.1, color=MUTED, stroke_width=2).move_to(center)
        self.curve = self.inner.plot(f, x_range=list(x_range), color=color, stroke_width=5)
        mid = ((x_range[0] + x_range[1]) / 2, (y_range[0] + y_range[1]) / 2)
        self.lens = Circle(radius=0.22, color=MUTED, stroke_width=2).move_to(axes.c2p(*mid))
        self.links = VGroup(Line(self.lens.get_top(), self.box.get_corner(UL), color=MUTED, stroke_width=1.2),
                            Line(self.lens.get_bottom(), self.box.get_corner(DL), color=MUTED, stroke_width=1.2))
        self.links.set_stroke(opacity=0.6)

    def group(self):
        return VGroup(self.lens, self.links, self.box, self.curve)

    def show(self):
        return AnimationGroup(Create(self.lens), Create(self.links), FadeIn(self.box), Create(self.curve))

    def point(self, x):
        return self.inner.c2p(x, self.f(x))

    def live_dot(self, x_func, color, radius=0.09):
        return always_redraw(lambda: Dot(self.point(x_func()), radius=radius, color=color).set_z_index(6))


class WindowSecants:
    """
    Secants from a fixed point x0 to x0 + h ("after", side +1) and/or x0 - h
    ("before", side -1), with their outer dots, all driven by one ValueTracker h.
    Lines and dots are separate groups so dots can appear before lines.

        w = WindowSecants(axes, s, 4.0, h, sides=(+1,))
        scene.add(w.dots)                 # live dots
        scene.play(Create(w.lines))       # live secant lines
        scene.play(h.animate.set_value(0.01))
        still = w.freeze(scene)           # swap the live drawing for a still copy
    """

    COLORS = {+1: AVG, -1: GOLD}

    def __init__(self, axes, f, x0, h: ValueTracker, sides=(+1,), extend=2.0, colors=None):
        self.axes, self.f, self.x0, self.h, self.extend = axes, f, x0, h, extend
        self.COLORS = {**self.COLORS, **(colors or {})}
        self.sides = []
        self.lines, self.dots = VGroup(), VGroup()
        for side in sides:
            self.add_side(side)

    def point(self, side):
        x = self.x0 + side * max(self.h.get_value(), 0.0)
        return self.axes.c2p(x, self.f(x))

    def _line(self, side):
        def draw():
            h = max(self.h.get_value(), 1e-6)
            slope = gradient(self.f, self.x0, self.x0 + side * h)
            (xa, ya), (xb, yb) = clipped_line_points(self.axes, self.x0, self.f(self.x0), slope, self.extend)
            line = DashedLine(self.axes.c2p(xa, ya), self.axes.c2p(xb, yb), color=self.COLORS[side],
                              stroke_width=3.5, dash_length=0.07, dashed_ratio=0.55)
            return line.set_z_index(4)
        return always_redraw(draw)

    def _dot(self, side):
        return always_redraw(lambda: Dot(self.point(side), radius=0.08, color=self.COLORS[side]).set_z_index(5))

    def add_side(self, side):
        """Add a side; returns (line, dot) so they can be animated in."""
        self.sides.append(side)
        line, dot = self._line(side), self._dot(side)
        self.lines.add(line)
        self.dots.add(dot)
        return line, dot

    def value(self, side):
        h = self.h.get_value()
        return gradient(self.f, self.x0, self.x0 + side * h) if h > 0 else float("nan")

    def freeze(self, scene):
        still = VGroup(*[m.copy().clear_updaters() for m in [*self.lines, *self.dots]])
        scene.remove(self.lines, self.dots)
        scene.add(still)
        return still


def window_bracket(axes, x0, x1, color=AVG, lift=0.16):
    """A flat bracket just above the time axis from x0 to x1."""
    y = axes.c2p(x0, axes.y_range[0])[1] + lift
    a, b = np.array([axes.c2p(x0, 0)[0], y, 0]), np.array([axes.c2p(x1, 0)[0], y, 0])
    return VGroup(Line(a, b, color=color, stroke_width=3),
                  Line(a + DOWN * 0.07, a + UP * 0.07, color=color, stroke_width=3),
                  Line(b + DOWN * 0.07, b + UP * 0.07, color=color, stroke_width=3))


class ValueTable:
    """
    A small table that grows a row at a time. Columns are given as headers;
    rows are lists of strings in the same order.

        table = ValueTable(["h", "window after"], col_colors=[INK, AVG])
        scene.play(table.header_in())
        scene.play(table.add_row(["0.1", "40.5"]))
    """

    def __init__(self, headers, col_colors=None, size=SIZE_LABEL, col_width=1.7, row_height=0.42,
                 top_left=np.array([1.4, -0.6, 0])):
        self.headers = list(headers)
        self.colors = col_colors or [INK] * len(headers)
        self.size, self.col_width, self.row_height = size, col_width, row_height
        self.top_left = np.array(top_left, dtype=float)
        self.rows = []
        self.extra = VGroup()      # cells added by add_column
        self.header = VGroup(*[
            txt(hd, size - 2, MUTED, MEDIUM).move_to(self.cell(0, i)) for i, hd in enumerate(self.headers)])
        self.rule = Line(self.top_left + DOWN * 0.24, self.top_left + DOWN * 0.24 + RIGHT * col_width * len(headers),
                         color=MUTED, stroke_width=1.5)

    def cell(self, row, col):
        return self.top_left + RIGHT * (self.col_width * (col + 0.5)) + DOWN * (self.row_height * row)

    def header_in(self):
        return AnimationGroup(FadeIn(self.header), Create(self.rule))

    def make_row(self, values):
        r = len(self.rows) + 1
        return VGroup(*[num(v, self.size, self.colors[i]).move_to(self.cell(r, i)) for i, v in enumerate(values)])

    def add_row(self, values):
        row = self.make_row(values)
        self.rows.append(row)
        return LaggedStart(*[FadeIn(c, shift=DOWN * 0.08) for c in row], lag_ratio=0.25)

    def add_column(self, header, values, color):
        """Add a column on the LEFT of the existing ones, growing the table leftwards; returns the animation."""
        self.top_left = self.top_left + LEFT * self.col_width
        self.rule.generate_target()
        self.rule.target.put_start_and_end_on(self.rule.get_start() + LEFT * self.col_width, self.rule.get_end())
        new_header = txt(header, self.size - 2, MUTED, MEDIUM).move_to(self.cell(0, 0))
        new_cells = [num(v, self.size, color).move_to(self.cell(i + 1, 0)) for i, v in enumerate(values)]
        self.colors.insert(0, color)
        self.extra.add(new_header, *new_cells)
        return AnimationGroup(MoveToTarget(self.rule), FadeIn(new_header),
                              LaggedStart(*[FadeIn(c) for c in new_cells], lag_ratio=0.3))

    def all(self):
        return VGroup(self.header, self.rule, *self.rows, self.extra)


class TrapLine:
    """
    A number line showing an interval [low, high] shaded, closing in on a value.

        trap = TrapLine(39.4, 40.6, center=[4.2, -2.9, 0])
        scene.play(trap.show(39.5, 40.5))
        scene.play(trap.squeeze(39.95, 40.05))
    """

    def __init__(self, x_min, x_max, center, length=5.0, ticks=None, decimals=1):
        self.line = NumberLine(x_range=[x_min, x_max, (x_max - x_min) / 4], length=length,
                               color=INK, stroke_width=2, include_numbers=False, tick_size=0.06).move_to(center)
        ticks = ticks if ticks is not None else [x_min + (x_max - x_min) * k / 4 for k in range(5)]
        self.labels = VGroup(*[num(f"{v:.{decimals}f}", SIZE_TICK - 4, MUTED).next_to(self.line.n2p(v), DOWN, buff=0.12)
                               for v in ticks])
        self.low, self.high = ValueTracker(x_min), ValueTracker(x_max)
        self.band = always_redraw(self._band)

    def _band(self):
        lo, hi = self.line.x_range[0], self.line.x_range[1]
        a = self.line.n2p(np.clip(self.low.get_value(), lo, hi))
        b = self.line.n2p(np.clip(self.high.get_value(), lo, hi))
        width = max(abs(b[0] - a[0]), 0.004)
        rect = Rectangle(width=width, height=0.26, fill_color=GOLD, fill_opacity=0.45, stroke_width=0)
        rect.move_to((a + b) / 2)
        ends = VGroup(Line(a + UP * 0.17, a + DOWN * 0.17, color=GOLD, stroke_width=3),
                      Line(b + UP * 0.17, b + DOWN * 0.17, color=AVG, stroke_width=3))
        return VGroup(rect, ends)

    def group(self):
        return VGroup(self.line, self.labels, self.band)

    def set(self, low, high):
        self.low.set_value(low)
        self.high.set_value(high)

    def squeeze(self, low, high):
        return AnimationGroup(self.low.animate.set_value(low), self.high.animate.set_value(high))

    def marker(self, value, color, label):
        p = self.line.n2p(value)
        tri = Triangle(color=color, fill_color=color, fill_opacity=1, stroke_width=0).scale(0.08).rotate(PI)
        tri.move_to(p + UP * 0.3)
        lab = num(label, SIZE_TICK - 2, color, MEDIUM).next_to(tri, UP, buff=0.06)
        return VGroup(tri, lab)


class DerivativeStack:
    """
    Three graphs stacked vertically, each the derivative of the one above, with
    arrows between them on the right. Used for the car, the epidemic and the wire
    in part 5, so one stack can morph into another with morph_to().

        car = DerivativeStack([s, v, a], 5, [(0, 125), (0, 50), (0, 12)], ["distance (m)", ...])
        scene.play(Create(car.axes), FadeIn(car.titles))
        scene.play(*car.morph_to(epidemic))
    """

    CENTER = np.array([-3.4, -0.15, 0])
    SIZE = (5.0, 1.55)
    GAP = 1.0
    COLORS = (CURVE, AVG, ACCENT)

    def __init__(self, funcs, x_max, y_ranges, titles, center=None, x_title="time"):
        center = self.CENTER if center is None else np.array(center, dtype=float)
        w, h = self.SIZE
        self.funcs, self.x_max = list(funcs), x_max
        self.axes, self.titles, self.curves = VGroup(), VGroup(), VGroup()
        for k, ((lo, hi), title) in enumerate(zip(y_ranges, titles)):
            ax = Axes(x_range=[0, x_max, x_max / 5], y_range=[lo, hi, (hi - lo) / 4], x_length=w, y_length=h,
                      tips=False, axis_config={"color": INK, "stroke_width": 2, "include_ticks": False})
            ax.move_to(center + UP * (1 - k) * (h + self.GAP))
            self.axes.add(ax)
            self.titles.add(txt(title, SIZE_TICK, MUTED).next_to(ax, UP, buff=0.1).align_to(ax, LEFT))
            self.curves.add(self.plot(k))
        self.arrows = VGroup(*[
            Arrow([self.axes[k].get_right()[0] + 0.4, self.axes[k].get_center()[1], 0],
                  [self.axes[k].get_right()[0] + 0.4, self.axes[k + 1].get_center()[1], 0],
                  buff=0.3, color=MUTED, stroke_width=3, max_tip_length_to_length_ratio=0.12)
            for k in range(2)])
        self.x_title = txt(x_title, SIZE_TICK, MUTED).next_to(self.axes[2], DOWN, buff=0.1).align_to(self.axes[2], RIGHT)

    def plot(self, k, x_end=None):
        x_end = self.x_max if x_end is None else max(x_end, 0.02)
        f = self.funcs[k]
        return self.axes[k].plot(f, x_range=[0, x_end, self.x_max / 400], color=self.COLORS[k],
                                 stroke_width=4, use_smoothing=False).set_z_index(2)

    def growing(self, k, u: ValueTracker):
        """Curve k drawn from 0 up to the time in u, redrawn every frame."""
        return always_redraw(lambda: self.plot(k, u.get_value()))

    def point(self, k, x):
        return self.axes[k].c2p(x, self.funcs[k](x))

    def dots(self, u: ValueTracker, ks=(0, 1, 2)):
        return VGroup(*[always_redraw(lambda k=k: Dot(self.point(k, u.get_value()), radius=0.07,
                                                      color=self.COLORS[k]).set_z_index(5)) for k in ks])

    def frame(self):
        """Axes, titles, arrows and the time label: everything except the curves."""
        return VGroup(self.axes, self.titles, self.arrows, self.x_title)

    def group(self):
        return VGroup(self.frame(), self.curves)

    def morph_to(self, other, curves=True):
        anims = [ReplacementTransform(self.axes, other.axes), ReplacementTransform(self.titles, other.titles),
                 ReplacementTransform(self.arrows, other.arrows), ReplacementTransform(self.x_title, other.x_title)]
        if curves:
            anims.append(ReplacementTransform(self.curves, other.curves))
        return anims


def acceleration(t):
    """+10 m/s² while speeding up, -10 m/s² while braking."""
    return 10.0 if t < 5 else -10.0


def car_stack(**kw):
    return DerivativeStack([s, v, acceleration], T_TOTAL,
                           [(0, 260), (0, 55), (-12, 12)],
                           ["distance (m)", "speed (m/s)", "acceleration (m/s²)"], **kw)


class LessonScene(TimedScene, MovingCameraScene):
    """Cream background, plus the narration timing from timeline.py."""

    def setup(self):
        MovingCameraScene.setup(self)
        self.camera.background_color = BG
        self.setup_timeline()
