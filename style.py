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


def txt(s, size=SIZE_LABEL, color=INK, weight=NORMAL):
    """Text rendered large and scaled down; Pango kerns badly at small sizes."""
    return Text(s, font=FONT, weight=weight, color=color, font_size=96).scale(size / 96)


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


def make_road():
    road = Line([ROAD_X0 - 0.9, ROAD_Y, 0], [ROAD_X1 + 0.9, ROAD_Y, 0], color=INK, stroke_width=3)
    marks = VGroup()
    for d in range(0, int(D_TOTAL) + 1, 50):
        tick = Line(ORIGIN, DOWN * 0.12, color=INK, stroke_width=2)
        tick.move_to(road_point(d), aligned_edge=UP)
        marks.add(tick, txt(f"{d} m", SIZE_TICK, MUTED).next_to(tick, DOWN, buff=0.1))
    return VGroup(road, marks)


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
class LessonScene(TimedScene, MovingCameraScene):
    """Cream background, plus the narration timing from timeline.py."""

    def setup(self):
        MovingCameraScene.setup(self)
        self.camera.background_color = BG
        self.setup_timeline()
