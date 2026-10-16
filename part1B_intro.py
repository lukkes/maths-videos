"""
Part 1, variant B (experimental): the same as part1_intro.py, except that in 1.3
the speedometer sits under a windscreen with pine trees passing on both sides, as
seen from the driver's seat. Trees start small near the horizon, grow as they come
closer, and fade out at the edges of the windscreen. They pass at the car's speed:
still while the car is at rest, fastest at 5 s, slowing as it brakes.

Preview:   manim -pql part1B_intro.py Part1b
Final:     manim -qh --fps 30 --save_sections part1B_intro.py Part1b
"""

from part1_intro import *

CENTER_X = 3.4
TOP_Y, BOTTOM_Y = 2.75, -3.0          # windscreen
TOP_HALF, BOTTOM_HALF = 2.2, 3.1      # half-widths at top and bottom
HORIZON_Y = 0.85
GROUND = "#CBD4BC"
ROAD_GREY = "#B7B1A6"
N_TREES = 10


def edge_half_width(y):
    """Half-width of the windscreen at height y."""
    return interpolate(BOTTOM_HALF, TOP_HALF, (y - BOTTOM_Y) / (TOP_Y - BOTTOM_Y))


def corner(side, y):
    return np.array([CENTER_X + side * edge_half_width(y), y, 0])


class Part1b(Part1):
    SPEEDO = dict(center=np.array([CENTER_X, -1.65, 0]), radius=1.2)

    def drive_view(self, u):
        sky = Polygon(corner(-1, TOP_Y), corner(1, TOP_Y), corner(1, HORIZON_Y), corner(-1, HORIZON_Y),
                      fill_color=SKY, fill_opacity=1, stroke_width=0)
        ground = Polygon(corner(-1, HORIZON_Y), corner(1, HORIZON_Y), corner(1, BOTTOM_Y), corner(-1, BOTTOM_Y),
                         fill_color=GROUND, fill_opacity=1, stroke_width=0)
        vp = np.array([CENTER_X, HORIZON_Y, 0])
        road = Polygon(vp + LEFT * 0.04, vp + RIGHT * 0.04, np.array([CENTER_X + 1.3, BOTTOM_Y, 0]),
                       np.array([CENTER_X - 1.3, BOTTOM_Y, 0]), fill_color=ROAD_GREY, fill_opacity=1, stroke_width=0)
        ridge = Polygon(*[corner(-1, HORIZON_Y)] +
                        [np.array([CENTER_X + x, HORIZON_Y + h, 0]) for x, h in
                         [(-1.9, 0.25), (-1.3, 0.45), (-0.7, 0.2), (0.0, 0.38), (0.8, 0.18), (1.5, 0.5), (2.0, 0.22)]] +
                        [corner(1, HORIZON_Y)], fill_color=MOUNTAIN_FAR, fill_opacity=1, stroke_width=0)
        frame = Polygon(corner(-1, TOP_Y), corner(1, TOP_Y), corner(1, BOTTOM_Y), corner(-1, BOTTOM_Y),
                        stroke_color=INK, stroke_width=7, fill_opacity=0).round_corners(0.25).set_z_index(3)

        # Each tree has a depth p in [0, 1): 0 at the horizon, 1 at the edge of the windscreen.
        state = {"p": list(np.linspace(0, 1, N_TREES, endpoint=False)),
                 "side": [(-1) ** k for k in range(N_TREES)],
                 "jitter": list(np.random.default_rng(5).uniform(0.85, 1.15, N_TREES))}

        def advance(m, dt):
            rate = 0.55 * v(u.get_value()) / 50          # trees pass faster when the car is faster
            state["p"] = [(p + dt * rate) % 1.0 for p in state["p"]]

        def trees_now():
            group = VGroup()
            for p, side, j in sorted(zip(state["p"], state["side"], state["jitter"])):
                d = p ** 1.7                                  # perspective: slow far away, fast up close
                y = HORIZON_Y - 2.2 * d
                x = CENTER_X + side * (0.35 + (edge_half_width(y) - 0.2) * d * j)
                height = (0.12 + 1.6 * d) * j
                tree = pine_tree(np.array([x, y, 0]), height)
                room = edge_half_width(y) - abs(x - CENTER_X)    # distance to the windscreen edge
                fade = min(1.0, p / 0.08) * float(np.clip(room / (0.45 * height + 0.05), 0, 1))
                group.add(tree.set_opacity(fade))
            return group

        driver = VMobject()
        driver.add_updater(advance)
        trees = always_redraw(trees_now)
        return VGroup(sky, ridge, ground, road, trees, frame, driver)
