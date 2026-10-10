"""
LEVEL 1 - EARTH TO MOON   (Member 1 - branch: member1-level1)

Requires:  pip install panda3d

How the main game uses this level
---------------------------------
    from levels.level1 import Level1

    def on_level1_done():
        ...start Level 2 here...

    level = Level1(base, on_complete=on_level1_done)
    level.start()

* `base` is your ShowBase instance (create it before the level).
* `on_complete` is called with no arguments when the player presses
  "Continue" on the Level 1 complete screen. The level cleans itself up
  (GUI, scene, tasks, key bindings, camera/lens settings) BEFORE calling it,
  so Level 2 can build its own scene immediately.
* The messenger event "level1-complete" is also sent, in case the main game
  prefers `self.accept("level1-complete", ...)`.
* `on_exit` (optional) is called if the player chooses "Quit" in the pause or
  crash menu. Without it the application exits.
* `level.cleanup()` can be called at any time to remove the level.

Run it on its own for testing:   python levels/level1.py

Flow
----
menu -> boarding -> countdown -> takeoff -> flight (asteroids) -> arrival
     -> landing on the Moon -> complete -> on_complete()

Controls: Arrow keys / WASD = fly, P or ESC = pause, ENTER/SPACE = start.
The astronaut, rocket, planets, and rocks are generated in code, so valid
3D model files are not required. The supplied .obj-named files are not used.
"""
import math
import random
import sys

from direct.gui.DirectGui import DirectButton, DirectFrame
from direct.gui.OnscreenText import OnscreenText
from direct.interval.IntervalGlobal import (
    Func, LerpFunc, LerpHprInterval, LerpPosInterval, LerpScaleInterval, Parallel, Sequence,
    Wait,
)
from direct.showbase.DirectObject import DirectObject
from panda3d.core import (
    AmbientLight, ClockObject, DirectionalLight, Geom, GeomNode, GeomPoints,
    GeomTriangles, GeomVertexData, GeomVertexFormat, GeomVertexWriter,
    NodePath, Point3, TextNode, TransparencyAttrib, Vec3, Vec4,
)


# ======================================================================
#  Procedural geometry helpers
# ======================================================================
def make_box(sx, sy, sz, name="box"):
    hx, hy, hz = sx / 2.0, sy / 2.0, sz / 2.0
    faces = [
        ((1, 0, 0), [(hx, -hy, -hz), (hx, hy, -hz), (hx, hy, hz), (hx, -hy, hz)]),
        ((-1, 0, 0), [(-hx, hy, -hz), (-hx, -hy, -hz), (-hx, -hy, hz), (-hx, hy, hz)]),
        ((0, 1, 0), [(hx, hy, -hz), (-hx, hy, -hz), (-hx, hy, hz), (hx, hy, hz)]),
        ((0, -1, 0), [(-hx, -hy, -hz), (hx, -hy, -hz), (hx, -hy, hz), (-hx, -hy, hz)]),
        ((0, 0, 1), [(-hx, -hy, hz), (hx, -hy, hz), (hx, hy, hz), (-hx, hy, hz)]),
        ((0, 0, -1), [(-hx, hy, -hz), (hx, hy, -hz), (hx, -hy, -hz), (-hx, -hy, -hz)]),
    ]
    vdata = GeomVertexData(name, GeomVertexFormat.getV3n3(), Geom.UHStatic)
    vw = GeomVertexWriter(vdata, "vertex")
    nw = GeomVertexWriter(vdata, "normal")
    tris = GeomTriangles(Geom.UHStatic)
    for i, (normal, corners) in enumerate(faces):
        for c in corners:
            vw.addData3(c[0], c[1], c[2])
            nw.addData3(normal[0], normal[1], normal[2])
        base = i * 4
        tris.addVertices(base, base + 1, base + 2)
        tris.addVertices(base, base + 2, base + 3)
    geom = Geom(vdata)
    geom.addPrimitive(tris)
    node = GeomNode(name)
    node.addGeom(geom)
    return node


def make_sphere(radius=1.0, rings=10, segs=14, jitter=0.0, color_fn=None,
                name="sphere"):
    """UV sphere. jitter > 0 makes it lumpy; color_fn(normal) -> (r, g, b, a)
    paints per-vertex colours (used for the Earth and the Moon)."""
    lumps = {}

    def lump(i, j):
        key = (i, 0) if i in (0, rings) else (i, j % segs)
        if key not in lumps:
            lumps[key] = 1.0 + random.uniform(-jitter, jitter)
        return lumps[key]

    fmt = GeomVertexFormat.getV3n3c4() if color_fn else GeomVertexFormat.getV3n3()
    vdata = GeomVertexData(name, fmt, Geom.UHStatic)
    vw = GeomVertexWriter(vdata, "vertex")
    nw = GeomVertexWriter(vdata, "normal")
    cw = GeomVertexWriter(vdata, "color") if color_fn else None
    for i in range(rings + 1):
        phi = math.pi * i / rings
        for j in range(segs + 1):
            theta = 2.0 * math.pi * j / segs
            n = Vec3(math.sin(phi) * math.cos(theta),
                     math.sin(phi) * math.sin(theta),
                     math.cos(phi))
            r = radius * lump(i, j)
            vw.addData3(n.x * r, n.y * r, n.z * r)
            nw.addData3(n.x, n.y, n.z)
            if cw is not None:
                c = color_fn(n)
                cw.addData4(c[0], c[1], c[2], c[3])
    tris = GeomTriangles(Geom.UHStatic)
    for i in range(rings):
        for j in range(segs):
            a = i * (segs + 1) + j
            b = a + 1
            c = a + segs + 1
            d = c + 1
            tris.addVertices(a, c, b)
            tris.addVertices(b, c, d)
    geom = Geom(vdata)
    geom.addPrimitive(tris)
    node = GeomNode(name)
    node.addGeom(geom)
    return node


def make_cylinder(r0, r1, height, segs=20, name="cylinder"):
    """Cylinder / cone along +Z: radius r0 at z=0, radius r1 at z=height."""
    vdata = GeomVertexData(name, GeomVertexFormat.getV3n3(), Geom.UHStatic)
    vw = GeomVertexWriter(vdata, "vertex")
    nw = GeomVertexWriter(vdata, "normal")
    tris = GeomTriangles(Geom.UHStatic)
    slope = (r0 - r1) / height
    for j in range(segs + 1):
        ang = 2.0 * math.pi * j / segs
        c, s = math.cos(ang), math.sin(ang)
        n = Vec3(c, s, slope)
        n.normalize()
        vw.addData3(r0 * c, r0 * s, 0.0)
        nw.addData3(n.x, n.y, n.z)
        vw.addData3(r1 * c, r1 * s, height)
        nw.addData3(n.x, n.y, n.z)
    for j in range(segs):
        b0 = 2 * j
        t0 = b0 + 1
        b1 = b0 + 2
        t1 = b0 + 3
        tris.addVertices(b0, b1, t0)
        tris.addVertices(t0, b1, t1)
    base = 2 * (segs + 1)
    for z, r, nz in ((0.0, r0, -1.0), (height, r1, 1.0)):
        if r <= 0.0:
            continue
        center = base
        vw.addData3(0.0, 0.0, z)
        nw.addData3(0.0, 0.0, nz)
        for j in range(segs + 1):
            ang = 2.0 * math.pi * j / segs
            vw.addData3(r * math.cos(ang), r * math.sin(ang), z)
            nw.addData3(0.0, 0.0, nz)
        for j in range(segs):
            tris.addVertices(center, center + 1 + j, center + 2 + j)
        base = center + segs + 2
    geom = Geom(vdata)
    geom.addPrimitive(tris)
    node = GeomNode(name)
    node.addGeom(geom)
    return node


def make_stars(count=700, radius=500.0):
    vdata = GeomVertexData("stars", GeomVertexFormat.getV3(), Geom.UHStatic)
    vw = GeomVertexWriter(vdata, "vertex")
    pts = GeomPoints(Geom.UHStatic)
    for i in range(count):
        v = Vec3(random.gauss(0, 1), random.gauss(0, 1), random.gauss(0, 1))
        if v.length() < 0.001:
            v = Vec3(0, 1, 0)
        v.normalize()
        vw.addData3(v.x * radius, v.y * radius, v.z * radius)
        pts.addVertex(i)
    pts.closePrimitive()
    geom = Geom(vdata)
    geom.addPrimitive(pts)
    node = GeomNode("stars")
    node.addGeom(geom)
    return node


def earth_color(n):
    if abs(n.z) > 0.9:
        return (0.95, 0.97, 1.0, 1.0)                       # polar ice
    cloud = math.sin(9.0 * n.x) * math.sin(8.0 * n.y + 1.0) * math.sin(9.0 * n.z)
    if cloud > 0.72:
        return (0.96, 0.96, 0.99, 1.0)
    land = (math.sin(3.1 * n.x + 1.0) * math.sin(2.7 * n.y + 0.5)
            + math.sin(4.3 * n.z + 2.0) * math.cos(2.2 * n.x)
            + 0.5 * math.sin(7.0 * n.x + 3.0 * n.y))
    if land > 1.0:
        return (0.55, 0.45, 0.27, 1.0)                      # desert / mountains
    if land > 0.45:
        return (0.22, 0.55, 0.22, 1.0)                      # land
    return (0.08, 0.28, 0.68, 1.0)                          # ocean


def moon_color(n):
    g = 0.62
    if math.sin(2.3 * n.x + 1.0) * math.sin(1.9 * n.y) + math.cos(2.7 * n.z) > 1.0:
        g = 0.38                                            # dark maria
    elif math.sin(12.0 * n.x) * math.sin(12.0 * n.y) * math.sin(12.0 * n.z) > 0.75:
        g = 0.46                                            # craters
    return (g, g, g * 0.97, 1.0)


def part(parent, geom, color, pos=(0, 0, 0), hpr=(0, 0, 0), scale=1.0,
         unlit=False):
    """Attach a geometry node to `parent` with position/orientation/colour."""
    np = parent.attachNewNode(geom)
    np.setPos(pos[0], pos[1], pos[2])
    np.setHpr(hpr[0], hpr[1], hpr[2])
    if isinstance(scale, (tuple, list)):
        np.setScale(scale[0], scale[1], scale[2])
    else:
        np.setScale(scale)
    if color is not None:
        np.setColor(color[0], color[1], color[2], color[3])
    if unlit:
        np.setLightOff()
    return np


def _heading(dx, dy):
    """Panda heading (degrees) that makes a +Y-facing model face (dx, dy)."""
    return math.degrees(math.atan2(-dx, dy))


# ======================================================================
#  The level
# ======================================================================
class Level1(DirectObject):
    NAME = "LEVEL 1 - EARTH TO MOON"
    TASK = "level1-update"

    FLIGHT_SECONDS = 70.0       # length of the flight (progress 0% -> 100%)
    FORWARD_SPEED = 70.0
    ARRIVAL_SECONDS = 5.0
    MOON_RADIUS = 300.0
    MOON_END_Y = 450.0          # moon centre distance when progress hits 100%
    MOON_NEAR_Y = 340.0         # moon centre distance at end of the approach
    FIELD_X = 16.0
    FIELD_Z = 9.0
    SHIP_SPEED = 42.0
    SPAWN_Y = 230.0
    KILL_Y = -40.0
    PAUSABLE = ("boarding", "countdown", "takeoff", "transition", "flight",
                "arrival", "landing")
    BG = {
        "launch": (0.45, 0.72, 1.0),
        "space": (0.0, 0.0, 0.02),
        "moon": (0.0, 0.0, 0.01),
    }

    # ------------------------------------------------------------ setup
    def __init__(self, app, on_complete=None, on_exit=None):
        self.app = app
        self.on_complete = on_complete
        self.on_exit = on_exit
        self.clock = ClockObject.getGlobalClock()

        self.state = "init"
        self.paused = False
        self._cleaned = False
        self.seq = None
        self._paused_seq = None
        self.fx = []
        self.asteroids = []
        self.dust = []
        self._gui = []
        self.scenes = {}
        self.keys = {"left": False, "right": False, "up": False, "down": False}

        self.msg_timer = None
        self.shake = 0.0
        self.flash = 0.0
        self.invuln = 0.0
        self.hull = 100
        self.progress = 0.0
        self.flight_time = 0.0
        self.travelled = 0.0
        self.arrival_t = 0.0
        self.scenery_speed = self.FORWARD_SPEED
        self.moon_y = self.MOON_END_Y + self.FLIGHT_SECONDS * self.FORWARD_SPEED
        self.spawn_timer = 1.0
        self.puff_timer = 0.0
        self._fill_w = -1.0
        self._pct = -1
        self.vel = Vec3(0, 0, 0)

        app.disableMouse()
        lens = app.camLens
        self._saved_lens = (lens.getFov()[0], lens.getNear(), lens.getFar())
        bg = app.getBackgroundColor()
        self._saved_bg = (bg[0], bg[1], bg[2])
        lens.setFov(65)
        lens.setNearFar(0.5, 30000.0)

        self.camera = app.camera
        self.root = app.render.attachNewNode("level1-root")

        self._build_lights()
        self._build_assets()
        self.ship_model = self._build_rocket()
        self.astronaut = self._build_astronaut()
        self._build_launch_scene()
        self._build_space_scene()
        self._build_moon_scene()
        self._build_ui()
        self._setup_input()

    def _build_lights(self):
        amb = AmbientLight("l1-ambient")
        amb.setColor(Vec4(0.38, 0.38, 0.46, 1))
        self.root.setLight(self.root.attachNewNode(amb))
        sun = DirectionalLight("l1-sun")
        sun.setColor(Vec4(1.0, 0.96, 0.88, 1))
        sun_np = self.root.attachNewNode(sun)
        sun_np.setHpr(-30, -35, 0)
        self.root.setLight(sun_np)

    def _build_assets(self):
        self.sphere_unit = make_sphere(1.0, 10, 14, name="sphere")
        self.rocks = [make_sphere(1.0, 8, 10, jitter=0.3, name="rock")
                      for _ in range(6)]
        self.earth_geom = make_sphere(1.0, 28, 40, color_fn=earth_color,
                                      name="earth")
        self.moon_geom = make_sphere(1.0, 28, 40, color_fn=moon_color,
                                     name="moon")
        self.stars_geom = make_stars()
        self.dust_geom = make_box(0.05, 1.6, 0.05)
        self.fx_root = self.root.attachNewNode("l1-fx")

    # ---- the rocket (upright, nose along +Z, hatch on the -Y side)
    def _build_rocket(self):
        r = NodePath("l1-rocket")
        hull = (0.93, 0.94, 0.98, 1)
        red = (0.82, 0.16, 0.16, 1)
        part(r, make_cylinder(1.0, 1.0, 6.0), hull)
        part(r, make_cylinder(1.02, 1.02, 0.5), red, pos=(0, 0, 3.0))
        part(r, make_cylinder(1.0, 0.0, 2.6), red, pos=(0, 0, 6.0))
        part(r, make_cylinder(0.8, 0.5, 0.5), (0.2, 0.2, 0.24, 1),
             pos=(0, 0, -0.5))
        for h in (0, 120, 240):
            pivot = r.attachNewNode("fin")
            pivot.setH(h)
            part(pivot, make_box(1.2, 0.15, 2.2), red, pos=(1.5, 0, 1.1))
        part(r, self.sphere_unit, (0.25, 0.6, 1.0, 1), pos=(0, -0.93, 4.4),
             scale=(0.45, 0.2, 0.45))
        part(r, make_box(0.9, 0.12, 1.5), (0.08, 0.08, 0.12, 1),
             pos=(0, -0.97, 2.05))                              # open doorway
        self.hatch = part(r, make_box(0.95, 0.14, 1.55), hull,
                          pos=(0, -1.0, 2.05), scale=(0.01, 1, 1))
        # engine flame (cones pointing down, hidden until needed)
        self.flame = r.attachNewNode("flame")
        self.flame.setPos(0, 0, -0.5)
        self.flame.setP(180)
        part(self.flame, make_cylinder(0.6, 0.0, 3.6), (1.0, 0.55, 0.1, 1),
             unlit=True)
        part(self.flame, make_cylinder(0.35, 0.0, 2.3), (1.0, 0.95, 0.6, 1),
             unlit=True)
        self.flame.hide()
        return r

    # ---- the astronaut (feet at z=0, facing +Y)
    def _build_astronaut(self):
        a = NodePath("l1-astronaut")
        white = (0.95, 0.95, 0.97, 1)
        grey = (0.6, 0.62, 0.68, 1)
        part(a, make_box(0.7, 0.4, 0.9), white, pos=(0, 0, 1.05))
        part(a, make_box(0.5, 0.25, 0.6), grey, pos=(0, -0.3, 1.1))
        part(a, self.sphere_unit, white, pos=(0, 0, 1.78), scale=0.3)
        part(a, self.sphere_unit, (0.9, 0.7, 0.2, 1), pos=(0, 0.18, 1.8),
             scale=(0.2, 0.16, 0.17))
        self.legs = []
        self.arms = []
        for sx in (-1, 1):
            leg = a.attachNewNode("leg")
            leg.setPos(sx * 0.18, 0, 0.6)
            part(leg, make_box(0.25, 0.28, 0.6), white, pos=(0, 0, -0.3))
            self.legs.append(leg)
            arm = a.attachNewNode("arm")
            arm.setPos(sx * 0.47, 0, 1.4)
            part(arm, make_box(0.2, 0.22, 0.65), white, pos=(0, 0, -0.3))
            self.arms.append(arm)
        return a

    def _walk_pose(self, phase):
        s = math.sin(phase) * 35.0
        self.legs[0].setP(s)
        self.legs[1].setP(-s)
        self.arms[0].setP(-s * 0.8)
        self.arms[1].setP(s * 0.8)

    # ---- scene 1: Earth launch pad
    def _build_launch_scene(self):
        s = self.root.attachNewNode("l1-launch")
        self.scenes["launch"] = s
        self.launch_root = s
        part(s, make_cylinder(450, 450, 0.5), (0.27, 0.52, 0.23, 1),
             pos=(0, 0, -0.5))                                  # grass
        part(s, make_cylinder(9, 9, 0.6), (0.5, 0.5, 0.54, 1))  # launch pad
        part(s, make_cylinder(3.4, 3.4, 0.62), (0.28, 0.28, 0.31, 1))
        tower = (0.8, 0.32, 0.15, 1)
        part(s, make_box(0.7, 0.7, 11.0), tower, pos=(-4.3, 0.6, 6.1))
        part(s, make_box(3.4, 0.3, 0.3), tower, pos=(-2.7, 0.6, 9.2))
        length = math.hypot(6.1, 1.3)
        angle = math.degrees(math.atan2(1.3, 6.1))
        part(s, make_box(1.6, length, 0.12), (0.55, 0.55, 0.6, 1),
             pos=(0, -4.45, 1.25), hpr=(0, angle, 0))           # boarding ramp
        part(s, self.sphere_unit, (1.0, 0.95, 0.6, 1), pos=(90, 320, 150),
             scale=16, unlit=True)                              # sun
        for _ in range(8):
            part(s, self.sphere_unit, (1, 1, 1, 1),
                 pos=(random.uniform(-220, 220), random.uniform(250, 330),
                      random.uniform(60, 130)),
                 scale=(random.uniform(25, 45), 10, random.uniform(7, 12)),
                 unlit=True)                                    # clouds
        for _ in range(12):
            ang = math.radians(random.uniform(-70, 70))
            dist = random.uniform(160, 300)
            part(s, self.sphere_unit,
                 (random.uniform(0.15, 0.25), random.uniform(0.38, 0.5),
                  random.uniform(0.15, 0.25), 1),
                 pos=(math.sin(ang) * dist, math.cos(ang) * dist, 0),
                 scale=(random.uniform(50, 90), random.uniform(40, 60),
                        random.uniform(14, 34)))                # hills
        for _ in range(18):
            x = random.uniform(-70, 70)
            y = random.uniform(14, 90)
            if abs(x) < 14 and y < 25:
                continue
            part(s, make_cylinder(0.3, 0.3, 1.8), (0.4, 0.27, 0.15, 1),
                 pos=(x, y, 0))
            part(s, make_cylinder(1.6, 0.0, 4.2), (0.12, 0.4, 0.15, 1),
                 pos=(x, y, 1.5))                               # trees

    # ---- scene 2: space flight
    def _build_space_scene(self):
        s = self.root.attachNewNode("l1-space")
        self.scenes["space"] = s
        stars = s.attachNewNode(self.stars_geom)
        stars.setLightOff()
        stars.setRenderModeThickness(2)
        stars.setBin("background", 0)
        stars.setDepthWrite(False)
        self.earth = part(s, self.earth_geom, None, pos=(-60, 200, -380),
                          scale=300.0)
        self.moon = part(s, self.moon_geom, None, pos=(0, self.moon_y, 0),
                         scale=self.MOON_RADIUS)
        self.ship_np = s.attachNewNode("l1-ship")
        self.ast_root = s.attachNewNode("l1-asteroids")
        for _ in range(110):
            d = part(s, self.dust_geom, (0.5, 0.6, 0.9, 1),
                     pos=(random.uniform(-35, 35),
                          random.uniform(self.KILL_Y, self.SPAWN_Y),
                          random.uniform(-22, 22)),
                     unlit=True)
            self.dust.append(d)

    # ---- scene 3: Moon surface (landing)
    def _build_moon_scene(self):
        s = self.root.attachNewNode("l1-moon")
        self.scenes["moon"] = s
        stars = s.attachNewNode(self.stars_geom)
        stars.setLightOff()
        stars.setRenderModeThickness(2)
        stars.setBin("background", 0)
        stars.setDepthWrite(False)
        part(s, make_cylinder(500, 500, 1.0), (0.58, 0.58, 0.56, 1),
             pos=(0, 0, -1.0))                                  # ground
        for _ in range(20):
            ang = random.uniform(0, 2 * math.pi)
            dist = random.uniform(14, 130)
            rad = random.uniform(3, 14)
            part(s, self.sphere_unit, (0.42, 0.42, 0.41, 1),
                 pos=(math.cos(ang) * dist, math.sin(ang) * dist, 0.05),
                 scale=(rad, rad, 0.35))                        # craters
        for _ in range(30):
            ang = random.uniform(0, 2 * math.pi)
            dist = random.uniform(8, 120)
            g = random.uniform(0.35, 0.55)
            part(s, random.choice(self.rocks), (g, g, g * 0.95, 1),
                 pos=(math.cos(ang) * dist, math.sin(ang) * dist, 0.1),
                 scale=random.uniform(0.4, 1.6))                # rocks
        part(s, self.earth_geom, None, pos=(-130, 360, 130), scale=45.0)
        self.flag = s.attachNewNode("l1-flag")
        self.flag.setPos(6.2, -3.8, 0)
        part(self.flag, make_box(0.08, 0.08, 3.0), (0.85, 0.85, 0.9, 1),
             pos=(0, 0, 1.5))
        part(self.flag, make_box(1.4, 0.05, 0.9), (0.85, 0.15, 0.15, 1),
             pos=(0.74, 0, 2.5))
        self.flag.hide()

    # ---- user interface
    def _track(self, widget):
        self._gui.append(widget)
        return widget

    def _label(self, parent, text, z, scale=0.07, fg=(1, 1, 1, 1)):
        return OnscreenText(parent=parent, text=text, pos=(0, z), scale=scale,
                            fg=fg, shadow=(0, 0, 0, 1),
                            align=TextNode.ACenter, mayChange=False)

    def _button(self, parent, text, z, command):
        return DirectButton(
            parent=parent, text=text, text_fg=(1, 1, 1, 1), scale=0.07,
            pos=(0, 0, z), command=command, pad=(0.5, 0.3),
            frameColor=((0.15, 0.4, 0.85, 1), (0.1, 0.3, 0.7, 1),
                        (0.25, 0.55, 1.0, 1), (0.3, 0.3, 0.3, 1)))

    def _panel(self, w, h, z=0.0):
        f = DirectFrame(parent=self.app.aspect2d, frameSize=(-w, w, -h, h),
                        frameColor=(0.02, 0.05, 0.12, 0.78), pos=(0, 0, z))
        f.hide()
        return self._track(f)

    def _build_ui(self):
        app = self.app
        # --- HUD: level name + progress (top centre), hull (top left), pause
        tc = app.a2dTopCenter.attachNewNode("l1-hud-top")
        tl = app.a2dTopLeft.attachNewNode("l1-hud-left")
        tr = app.a2dTopRight.attachNewNode("l1-hud-right")
        self.hud_nodes = [tc, tl, tr]
        white = (1, 1, 1, 1)
        shadow = (0, 0, 0, 1)
        self._track(OnscreenText(parent=tc, text=self.NAME, pos=(0, -0.09),
                                 scale=0.06, fg=white, shadow=shadow,
                                 align=TextNode.ACenter, mayChange=False))
        self.prog_bg = self._track(DirectFrame(
            parent=tc, frameSize=(-0.6, 0.6, -0.018, 0.018), pos=(0, 0, -0.16),
            frameColor=(0.15, 0.15, 0.2, 0.85)))
        self.prog_fill = self._track(DirectFrame(
            parent=self.prog_bg, frameSize=(0, 0.0001, -0.014, 0.014),
            pos=(-0.6, 0, 0), frameColor=(0.3, 0.8, 1.0, 1)))
        self._track(OnscreenText(parent=tc, text="EARTH", pos=(-0.64, -0.175),
                                 scale=0.04, fg=white, shadow=shadow,
                                 align=TextNode.ARight, mayChange=False))
        self._track(OnscreenText(parent=tc, text="MOON", pos=(0.64, -0.175),
                                 scale=0.04, fg=white, shadow=shadow,
                                 align=TextNode.ALeft, mayChange=False))
        self.pct_text = self._track(OnscreenText(
            parent=tc, text="JOURNEY 0%", pos=(0, -0.25), scale=0.045, fg=white,
            shadow=shadow, align=TextNode.ACenter, mayChange=True))
        self._track(OnscreenText(parent=tl, text="HULL", pos=(0.06, -0.09),
                                 scale=0.05, fg=white, shadow=shadow,
                                 align=TextNode.ALeft, mayChange=False))
        self.hull_bg = self._track(DirectFrame(
            parent=tl, frameSize=(0, 0.5, -0.018, 0.018), pos=(0.06, 0, -0.15),
            frameColor=(0.15, 0.15, 0.2, 0.85)))
        self.hull_fill = self._track(DirectFrame(
            parent=self.hull_bg, frameSize=(0, 0.5, -0.014, 0.014),
            frameColor=(0.3, 0.9, 0.4, 1)))
        self.lives_text = self._track(OnscreenText(
            parent=tl, text="HITS LEFT: 4", pos=(0.06, -0.23), scale=0.042,
            fg=white, shadow=shadow, align=TextNode.ALeft, mayChange=True))
        self._track(DirectButton(
            parent=tr, text="PAUSE", text_fg=white, scale=0.05,
            pos=(-0.16, 0, -0.1), command=self.toggle_pause, pad=(0.4, 0.3),
            frameColor=((0.15, 0.4, 0.85, 1), (0.1, 0.3, 0.7, 1),
                        (0.25, 0.55, 1.0, 1), (0.3, 0.3, 0.3, 1))))
        self._set_hud(False)

        # --- big centre texts
        self.count_text = self._track(OnscreenText(
            parent=app.aspect2d, text="", pos=(0, 0.1), scale=0.4,
            fg=(1, 0.9, 0.3, 1), shadow=shadow, align=TextNode.ACenter,
            mayChange=True))
        self.count_text.hide()
        self.msg_text = self._track(OnscreenText(
            parent=app.aspect2d, text="", pos=(0, 0.55), scale=0.075,
            fg=(1, 0.95, 0.6, 1), shadow=shadow, align=TextNode.ACenter,
            mayChange=True))
        self.msg_text.hide()

        # --- screen flash / fade overlays
        self.flash_frame = self._track(DirectFrame(
            parent=app.render2d, frameSize=(-1, 1, -1, 1),
            frameColor=(1, 0.1, 0.1, 0)))
        self.flash_frame.setTransparency(TransparencyAttrib.MAlpha)
        self.flash_frame.setBin("gui-popup", 40)
        self.fade_frame = self._track(DirectFrame(
            parent=app.render2d, frameSize=(-1, 1, -1, 1),
            frameColor=(0, 0, 0, 0)))
        self.fade_frame.setTransparency(TransparencyAttrib.MAlpha)
        self.fade_frame.setBin("gui-popup", 50)

        # --- start menu
        self.menu_panel = self._panel(0.8, 0.3, 0.55)
        self._label(self.menu_panel, "MISSION: MOON", 0.12, 0.11,
                    (1, 0.9, 0.4, 1))
        self._label(self.menu_panel, "Level 1 - Earth to Moon", 0.03, 0.06)
        self._button(self.menu_panel, "START GAME", -0.15, self._start_boarding)

        # --- pause menu
        self.pause_panel = self._panel(0.6, 0.42)
        self._label(self.pause_panel, "PAUSED", 0.27, 0.11)
        self._button(self.pause_panel, "RESUME", 0.1, self._resume)
        self._button(self.pause_panel, "RESTART LEVEL", -0.06,
                     self._restart_level)
        self._button(self.pause_panel, "QUIT", -0.22, self._quit)

        # --- crash screen
        self.crash_panel = self._panel(0.85, 0.4)
        self._label(self.crash_panel, "SPACESHIP CRASHED!", 0.22, 0.11,
                    (1, 0.3, 0.3, 1))
        self._label(self.crash_panel, "Four asteroid hits used all your hull.", 0.1,
                    0.055)
        self._button(self.crash_panel, "TRY AGAIN", -0.06, self._retry)
        self._button(self.crash_panel, "QUIT", -0.22, self._quit)

        # --- level complete
        self.complete_panel = self._panel(0.92, 0.43, 0.45)
        self._label(self.complete_panel, "LEVEL 1 COMPLETE!", 0.27, 0.105,
                    (0.5, 1.0, 0.6, 1))
        self._label(
            self.complete_panel,
            "You successfully reached the Moon and completed your first level!\n"
            "Wait for further instructions in your next level.",
            0.10, 0.047)
        self._button(self.complete_panel, "CONTINUE TO LEVEL 2", -0.25,
                     self._finish)

    def _set_hud(self, visible):
        for n in self.hud_nodes:
            if visible:
                n.show()
            else:
                n.hide()

    def _set_progress(self, p):
        p = max(0.0, min(1.0, p))
        w = max(0.0001, 1.2 * p)
        if abs(w - self._fill_w) > 0.002:
            self._fill_w = w
            self.prog_fill["frameSize"] = (0, w, -0.014, 0.014)
        pct = int(p * 100)
        if pct != self._pct:
            self._pct = pct
            self.pct_text.setText("JOURNEY %d%%" % pct)

    def _set_hull(self, hull):
        frac = max(0.0, min(1.0, hull / 100.0))
        self.hull_fill["frameSize"] = (0, max(0.0001, 0.5 * frac), -0.014, 0.014)
        self.lives_text.setText("HITS LEFT: %d" % max(0, int(hull / 25)))
        if frac > 0.5:
            col = (0.3, 0.9, 0.4, 1)
        elif frac > 0.25:
            col = (1.0, 0.75, 0.2, 1)
        else:
            col = (1.0, 0.25, 0.2, 1)
        self.hull_fill["frameColor"] = col

    def _say(self, text, seconds=3.0):
        self.msg_text.setText(text)
        self.msg_text.show()
        self.msg_timer = seconds

    def _set_fade(self, a):
        self.fade_frame["frameColor"] = (0, 0, 0, a)

    def _fade(self, duration, a0, a1):
        return LerpFunc(self._set_fade, fromData=a0, toData=a1,
                        duration=duration)

    # ---- input
    def _setup_input(self):
        binds = {
            "arrow_left": "left", "a": "left",
            "arrow_right": "right", "d": "right",
            "arrow_up": "up", "w": "up",
            "arrow_down": "down", "s": "down",
        }
        for key, action in binds.items():
            self.accept(key, self._set_key, [action, True])
            self.accept(key + "-up", self._set_key, [action, False])
        self.accept("escape", self.toggle_pause)
        self.accept("p", self.toggle_pause)
        self.accept("enter", self._on_enter)
        self.accept("space", self._on_enter)

    def _set_key(self, action, value):
        self.keys[action] = value

    def _on_enter(self):
        if self.state == "menu" and not self.paused:
            self._start_boarding()

    # ------------------------------------------------------------ public
    def start(self):
        """Show the launch scene with the Start Game button."""
        self._enter_launch()
        self.app.taskMgr.add(self._update, self.TASK)

    def cleanup(self):
        """Remove everything this level created (safe to call twice)."""
        if self._cleaned:
            return
        self._cleaned = True
        self._stop_seq()
        self.ignoreAll()
        self.app.taskMgr.remove(self.TASK)
        for w in self._gui:
            try:
                w.destroy()
            except Exception:
                pass
        for n in self.hud_nodes:
            n.removeNode()
        self.root.removeNode()
        fov, near, far = self._saved_lens
        self.app.camLens.setFov(fov)
        self.app.camLens.setNearFar(near, far)
        self.app.setBackgroundColor(*self._saved_bg)

    # ------------------------------------------------------------ helpers
    def _play(self, seq):
        self.seq = seq
        seq.start()

    def _stop_seq(self):
        if self.seq is not None:
            self.seq.pause()
            self.seq = None
        self._paused_seq = None

    def _show_scene(self, name):
        for key, np in self.scenes.items():
            if key == name:
                np.show()
            else:
                np.hide()
        r, g, b = self.BG[name]
        self.app.setBackgroundColor(r, g, b)

    def _fx(self, pos, s0, s1, life, color, a0=0.8, vel=None):
        np = self.fx_root.attachNewNode(self.sphere_unit)
        np.setLightOff()
        np.setTransparency(TransparencyAttrib.MAlpha)
        np.setPos(pos)
        np.setScale(s0)
        np.setColor(color[0], color[1], color[2], a0)
        self.fx.append({"np": np, "t": 0.0, "life": life, "s0": s0, "s1": s1,
                        "c": color, "a0": a0, "vel": vel})

    def _clear_fx(self):
        for f in self.fx:
            f["np"].removeNode()
        self.fx = []

    def _clear_asteroids(self):
        for a in self.asteroids:
            a["np"].removeNode()
        self.asteroids = []

    # ------------------------------------------------------------ stage 1
    def _enter_launch(self):
        """Earth launch scene: astronaut, rocket on the pad, Start button."""
        self._stop_seq()
        self._clear_fx()
        self._clear_asteroids()
        self.paused = False
        self.pause_panel.hide()
        self.crash_panel.hide()
        self.complete_panel.hide()
        self.count_text.hide()
        self.msg_text.hide()
        self.flash = 0.0
        self.flash_frame["frameColor"] = (1, 0.1, 0.1, 0)
        self._set_fade(0.0)
        self._show_scene("launch")
        self.ship_model.reparentTo(self.launch_root)
        self.ship_model.setPosHprScale(0, 0, 0.6, 0, 0, 0, 1, 1, 1)
        self.flame.hide()
        self.hatch.setScale(0.01, 1, 1)
        self.astronaut.reparentTo(self.launch_root)
        self.astronaut.show()
        self.astronaut.setPos(-5, -7, 0.6)
        self.astronaut.setH(_heading(5.0, -0.5))
        self._walk_pose(0.0)
        self.camera.setPos(7, -32, 7)
        self.camera.lookAt(Point3(0, 0, 6))
        self._set_hud(False)
        self._set_progress(0.0)
        self._set_hull(100)
        self.hull = 100
        self.progress = 0.0
        self.menu_panel.show()
        self.state = "menu"

    # ------------------------------------------------------------ stage 2
    def _start_boarding(self):
        if self.state != "menu":
            return
        self.state = "boarding"
        self.menu_panel.hide()
        self._set_hud(True)
        a = self.astronaut
        p0 = Point3(-5, -7, 0.6)
        p1 = Point3(0, -7.5, 0.6)
        p2 = Point3(0, -1.5, 1.9)
        d1 = (p1 - p0).length() / 2.4
        d2 = (p2 - p1).length() / 2.0
        self._play(Sequence(
            Func(self._say, "Astronaut boarding...", 3.5),
            Func(a.setH, _heading(p1.x - p0.x, p1.y - p0.y)),
            Parallel(
                LerpPosInterval(a, d1, p1, startPos=p0),
                LerpFunc(self._walk_pose, fromData=0.0, toData=d1 * 7.0,
                         duration=d1)),
            Func(a.setH, 0),
            Parallel(
                LerpPosInterval(a, d2, p2, startPos=p1),
                LerpFunc(self._walk_pose, fromData=0.0, toData=d2 * 7.0,
                         duration=d2)),
            Func(self._walk_pose, 0.0),
            Func(a.hide),
            LerpScaleInterval(self.hatch, 0.8, Vec3(1, 1, 1),
                              startScale=Vec3(0.01, 1, 1)),
            Wait(0.4),
            Func(self._start_countdown)))

    def _set_count(self, label):
        self.count_text.setText(label)
        self.count_text.show()

    def _start_countdown(self):
        self.state = "countdown"
        self.msg_text.hide()
        steps = []
        for label in ("3", "2", "1", "LAUNCH!"):
            hold = 0.7 if label == "LAUNCH!" else 1.0
            steps.append(Func(self._set_count, label))
            steps.append(Parallel(
                LerpScaleInterval(self.count_text, 0.45, 1.0, startScale=1.8,
                                  blendType="easeOut"),
                Wait(hold)))
        steps.append(Func(self.count_text.hide))
        steps.append(Func(self._begin_takeoff))
        self._play(Sequence(*steps))

    def _begin_takeoff(self):
        self.state = "takeoff"
        self.puff_timer = 0.0
        self.flame.show()
        self._play(Sequence(
            Parallel(
                LerpPosInterval(self.ship_model, 7.0, Point3(0, 0, 260),
                                startPos=Point3(0, 0, 0.6),
                                blendType="easeIn"),
                Sequence(Wait(5.8), self._fade(1.2, 0.0, 1.0))),
            Func(self._to_space)))

    def _update_takeoff(self, dt):
        z = self.ship_model.getZ()
        self.puff_timer -= dt
        if self.puff_timer <= 0.0 and z < 60.0:
            self.puff_timer = 0.05
            ang = random.uniform(0, 2 * math.pi)
            c, s = math.cos(ang), math.sin(ang)
            self._fx(Point3(c * 1.5, s * 1.5, 0.9), 1.0,
                     random.uniform(4.0, 6.0), 1.6, (0.85, 0.85, 0.85),
                     a0=0.7, vel=Vec3(c * 4.0, s * 4.0, 1.0))
        amp = 0.25 if z < 40.0 else 0.0
        self.camera.setPos(7 + random.uniform(-amp, amp),
                           -32 + random.uniform(-amp, amp),
                           7 + random.uniform(-amp, amp))
        self.camera.lookAt(Point3(0, 0, min(6.0 + z * 0.9, 110.0)))

    # ------------------------------------------------------------ stage 3
    def _to_space(self):
        self._clear_fx()
        self._show_scene("space")
        self.ship_model.reparentTo(self.ship_np)
        self.ship_model.setPosHprScale(0, -2.15, 0, 0, -90, 0, 0.5, 0.5, 0.5)
        self.flame.show()
        self._reset_flight()
        self.state = "flight"
        self._say(
            "Use ARROW KEYS / WASD to steer and dodge asteroids.\n"
            "Each hit costs 25% hull; 4 hits end the game.", 7.0)
        self._play(self._fade(0.8, 1.0, 0.0))

    def _reset_flight(self):
        self._clear_asteroids()
        self.hull = 100
        self.progress = 0.0
        self.flight_time = 0.0
        self.travelled = 0.0
        self.arrival_t = 0.0
        self.scenery_speed = self.FORWARD_SPEED
        self.moon_y = self.MOON_END_Y + self.FLIGHT_SECONDS * self.FORWARD_SPEED
        self.spawn_timer = 1.0
        self.invuln = 0.0
        self.shake = 0.0
        self.vel = Vec3(0, 0, 0)
        self.ship_np.setPos(0, 0, 0)
        self.ship_np.setHpr(0, 0, 0)
        self.ship_np.show()
        self._set_progress(0.0)
        self._set_hull(100)

    def _spawn_asteroid(self):
        r = random.uniform(1.0, 3.2)
        if random.random() < 0.45:
            sp = self.ship_np.getPos()
            x = sp.x + random.uniform(-4.0, 4.0)
            z = sp.z + random.uniform(-3.0, 3.0)
        else:
            x = random.uniform(-24.0, 24.0)
            z = random.uniform(-14.0, 14.0)
        np = self.ast_root.attachNewNode(random.choice(self.rocks))
        np.setScale(r)
        np.setPos(x, self.SPAWN_Y, z)
        np.setHpr(random.uniform(0, 360), random.uniform(0, 360),
                  random.uniform(0, 360))
        g = random.uniform(0.3, 0.5)
        np.setColor(g, g * 0.88, g * 0.75, 1)
        self.asteroids.append({
            "np": np, "r": r, "drift": random.uniform(0.0, 18.0),
            "spin": Vec3(random.uniform(-60, 60), random.uniform(-60, 60),
                         random.uniform(-60, 60)),
        })

    def _update_flight(self, dt):
        st = self.state
        v = self.FORWARD_SPEED

        # --- progress / scenery speed / moon distance for each state
        if st == "flight":
            self.flight_time += dt
            self.progress = min(1.0, self.flight_time / self.FLIGHT_SECONDS)
            self.scenery_speed = v
            self.moon_y = (self.MOON_END_Y
                           + (1.0 - self.progress) * self.FLIGHT_SECONDS * v)
        elif st == "arrival":
            self.arrival_t += dt
            k = min(1.0, self.arrival_t / self.ARRIVAL_SECONDS)
            e = k * k * (3.0 - 2.0 * k)
            self.scenery_speed = v * (1.0 - 0.75 * e)
            self.moon_y = (self.MOON_END_Y
                           + (self.MOON_NEAR_Y - self.MOON_END_Y) * e)
        elif st == "transition":
            self.scenery_speed = v * 0.25
        elif st == "crashed":
            self.scenery_speed = v * 0.15
        self.travelled += self.scenery_speed * dt

        # --- ship movement (smooth)
        want = Vec3(0, 0, 0)
        if st == "flight":
            want = Vec3(float(self.keys["right"]) - float(self.keys["left"]),
                        0.0,
                        float(self.keys["up"]) - float(self.keys["down"]))
            if want.lengthSquared() > 0.0:
                want.normalize()
                want *= self.SHIP_SPEED
        self.vel += (want - self.vel) * min(1.0, dt * 10.0)
        p = self.ship_np.getPos() + self.vel * dt
        p.x = max(-self.FIELD_X, min(self.FIELD_X, p.x))
        p.z = max(-self.FIELD_Z, min(self.FIELD_Z, p.z))
        p.y = 0.0
        self.ship_np.setPos(p)
        self.ship_np.setR(self.vel.x * 2.0)
        self.ship_np.setP(self.vel.z * 1.2)

        # --- invulnerability blink after a hit
        if st == "flight":
            if self.invuln > 0.0:
                self.invuln -= dt
                if self.invuln > 0.0 and int(self.invuln * 12) % 2 == 0:
                    self.ship_np.hide()
                else:
                    self.ship_np.show()

        # --- scenery
        for d in self.dust:
            d.setY(d.getY() - self.scenery_speed * dt)
            if d.getY() < self.KILL_Y:
                d.setPos(random.uniform(-35, 35), self.SPAWN_Y,
                         random.uniform(-22, 22))
        self.moon.setPos(0, self.moon_y, 0)
        self.moon.setH(self.moon.getH() + 1.5 * dt)
        self.earth.setPos(-60, 200 - self.travelled * 0.35,
                          -380 - self.travelled * 0.35)

        # --- asteroids: spawn, move toward the ship, collide
        if st == "flight" and self.progress < 0.96:
            self.spawn_timer -= dt
            if self.spawn_timer <= 0.0:
                self.spawn_timer = max(0.4, 0.9 - 0.5 * self.progress)
                self._spawn_asteroid()
        can_hit = (st == "flight" and self.invuln <= 0.0)
        ship_pos = self.ship_np.getPos()
        hit = None
        keep = []
        for a in self.asteroids:
            np = a["np"]
            np.setY(np.getY() - (self.scenery_speed + a["drift"]) * dt)
            np.setHpr(np.getHpr() + a["spin"] * dt)
            if np.getY() < self.KILL_Y:
                np.removeNode()
                continue
            if (can_hit and hit is None
                    and (np.getPos() - ship_pos).length() < a["r"] * 0.85 + 1.3):
                hit = a
            keep.append(a)
        self.asteroids = keep
        if hit is not None:
            self._on_hit(hit)

        # --- camera follows the ship, with shake
        sp = self.ship_np.getPos()
        sh = self.shake
        self.camera.setPos(sp.x * 0.55 + random.uniform(-sh, sh), -20.0,
                           sp.z * 0.55 + 3.5 + random.uniform(-sh, sh))
        self.camera.lookAt(Point3(sp.x * 0.35, 40.0, sp.z * 0.35))
        self.shake = max(0.0, self.shake - dt * 1.5)

        # --- HUD + state changes
        self._set_progress(self.progress)
        if st == "flight" and self.progress >= 1.0:
            self._begin_arrival()
        elif st == "arrival" and self.arrival_t >= self.ARRIVAL_SECONDS:
            self._begin_transition()

    def _on_hit(self, a):
        if a in self.asteroids:
            self.asteroids.remove(a)
        self._fx(a["np"].getPos(), a["r"] * 0.6, a["r"] * 2.4, 0.5,
                 (1.0, 0.6, 0.15), a0=0.95)
        a["np"].removeNode()
        self.hull -= 25
        self.invuln = 1.2
        self.shake = 0.6
        self.flash = 0.6
        self._set_hull(self.hull)
        if self.hull <= 0:
            self._crash()

    # ------------------------------------------------------------ crash
    def _crash(self):
        self.state = "crashed"
        self.invuln = 0.0
        pos = self.ship_np.getPos()
        self.ship_np.hide()
        self._fx(pos, 1.0, 9.0, 0.9, (1.0, 0.6, 0.15), a0=1.0)
        self._fx(pos, 0.5, 5.0, 0.6, (1.0, 1.0, 0.6), a0=1.0)
        self.msg_text.hide()
        self.crash_panel.show()

    def _retry(self):
        if self.state != "crashed":
            return
        self.crash_panel.hide()
        self._reset_flight()
        self.state = "flight"
        self._say("Try again - watch out for the asteroids!", 3.0)

    # ------------------------------------------------------------ stage 4
    def _begin_arrival(self):
        self.state = "arrival"
        self.arrival_t = 0.0
        for a in self.asteroids:
            self._fx(a["np"].getPos(), a["r"] * 0.5, a["r"] * 2.0, 0.5,
                     (0.9, 0.9, 1.0), a0=0.7)
        self._clear_asteroids()
        self._say("Approaching the Moon...", 6.0)

    def _begin_transition(self):
        self.state = "transition"
        self._play(Sequence(self._fade(1.0, 0.0, 1.0),
                            Func(self._begin_landing)))

    def _begin_landing(self):
        """Switch to the Moon surface and land the rocket."""
        self.state = "landing"
        self._clear_fx()
        self._show_scene("moon")
        self.msg_text.hide()
        self.ship_model.reparentTo(self.scenes["moon"])
        self.ship_model.setPosHprScale(0, 0, 70, 0, 0, 0, 1, 1, 1)
        self.hatch.setScale(1, 1, 1)
        self.flame.show()
        self.camera.setPos(0, -46, 10)
        self.camera.lookAt(Point3(0, 0, 40))
        a = self.astronaut
        self._play(Sequence(
            Parallel(
                LerpPosInterval(self.ship_model, 8.0, Point3(0, 0, 1.0),
                                startPos=Point3(0, 0, 70),
                                blendType="easeOut"),
                LerpHprInterval(self.ship_model, 8.0, Point3(0, 8, 18),
                                startHpr=Point3(0, 0, 0),
                                blendType="easeOut"),
                self._fade(1.0, 1.0, 0.0)),
            Func(self._touchdown),
            Wait(1.2),
            LerpScaleInterval(self.hatch, 0.8, Vec3(0.01, 1, 1),
                              startScale=Vec3(1, 1, 1)),
            Func(self._astronaut_exit),
            Parallel(
                LerpPosInterval(a, 0.8, Point3(0, -3.8, 0),
                                startPos=Point3(0, -1.3, 1.3),
                                blendType="easeIn"),
                LerpFunc(self._walk_pose, fromData=0.0, toData=4.0,
                         duration=0.8)),
            Func(a.setH, -90),
            Parallel(
                LerpPosInterval(a, 2.5, Point3(5, -3.8, 0),
                                startPos=Point3(0, -3.8, 0)),
                LerpFunc(self._walk_pose, fromData=0.0, toData=17.0,
                         duration=2.5)),
            Func(self._walk_pose, 0.0),
            Func(self.flag.show),
            LerpScaleInterval(self.flag, 0.9, 1.0, startScale=0.01),
            Wait(1.0),
            Func(self._show_complete)))

    def _touchdown(self):
        """Crash-land on the Moon; the astronaut survives the impact."""
        self.flame.hide()
        self.shake = 0.0
        self.ship_model.setHpr(0, 8, 18)
        self._say("CRASH LANDING! The ship is damaged, but the astronaut survived.", 4.0)
        # Dust and small sparks radiate from the impact point.
        for i in range(26):
            ang = 2.0 * math.pi * i / 26.0
            c, s = math.cos(ang), math.sin(ang)
            color = (1.0, 0.55, 0.18) if i % 3 == 0 else (0.7, 0.7, 0.68)
            self._fx(Point3(c * 1.5, s * 1.5, 0.6), 0.8, 4.8, 1.8,
                     color, a0=0.85,
                     vel=Vec3(c * 8.0, s * 8.0, random.uniform(0.3, 1.0)))

    def _astronaut_exit(self):
        a = self.astronaut
        a.reparentTo(self.scenes["moon"])
        a.setPos(0, -1.3, 1.3)
        a.setH(180)
        a.show()

    def _update_landing(self, dt):
        z = self.ship_model.getZ()
        if not self.flame.isHidden() and z < 18.0:
            self.puff_timer -= dt
            if self.puff_timer <= 0.0:
                self.puff_timer = 0.08
                ang = random.uniform(0, 2 * math.pi)
                c, s = math.cos(ang), math.sin(ang)
                self._fx(Point3(c, s, 0.5), 1.0, 4.0, 1.2, (0.7, 0.7, 0.68),
                         a0=0.6, vel=Vec3(c * 7.0, s * 7.0, 0.3))
        self.camera.setPos(0, -46, 10)
        self.camera.lookAt(Point3(0, 0, 6.0 + z * 0.5))

    def _show_complete(self):
        self.state = "complete"
        self.complete_panel.show()

    def _finish(self):
        """Continue button: clean up, then tell the main game Level 1 is done."""
        if self.state != "complete":
            return
        callback = self.on_complete
        self.cleanup()
        try:
            messenger.send("level1-complete")      # noqa: F821 (Panda builtin)
        except NameError:
            pass
        if callback is not None:
            callback()

    # ------------------------------------------------------------ pause
    def toggle_pause(self):
        if self.paused:
            self._resume()
        elif self.state in self.PAUSABLE:
            self._pause()

    def _pause(self):
        self.paused = True
        if self.seq is not None and self.seq.isPlaying():
            self._paused_seq = self.seq
            self._paused_seq.pause()
        else:
            self._paused_seq = None
        self.pause_panel.show()

    def _resume(self):
        if not self.paused:
            return
        self.paused = False
        self.pause_panel.hide()
        if self._paused_seq is not None:
            self._paused_seq.resume()
            self._paused_seq = None

    def _restart_level(self):
        self._enter_launch()

    def _quit(self):
        callback = self.on_exit
        self.cleanup()
        if callback is not None:
            callback()
        else:
            self.app.userExit()

    # ------------------------------------------------------------ main loop
    def _update(self, task):
        if self._cleaned:
            return task.done
        dt = min(self.clock.getDt(), 0.05)
        if self.paused:
            return task.cont
        st = self.state
        if st == "takeoff":
            self._update_takeoff(dt)
        elif st in ("flight", "arrival", "transition", "crashed"):
            self._update_flight(dt)
        elif st == "landing":
            self._update_landing(dt)

        # engine flame flicker
        if st in ("takeoff", "flight", "arrival", "transition", "landing"):
            if not self.flame.isHidden():
                self.flame.setScale(1.0, 1.0, random.uniform(0.85, 1.25))

        # particles
        keep = []
        for f in self.fx:
            f["t"] += dt
            k = f["t"] / f["life"]
            if k >= 1.0:
                f["np"].removeNode()
                continue
            np = f["np"]
            np.setScale(f["s0"] + (f["s1"] - f["s0"]) * k)
            c = f["c"]
            np.setColor(c[0], c[1], c[2], f["a0"] * (1.0 - k))
            if f["vel"] is not None:
                np.setPos(np.getPos() + f["vel"] * dt)
            keep.append(f)
        self.fx = keep

        # red hit flash
        if self.flash > 0.0:
            self.flash = max(0.0, self.flash - dt * 1.8)
            self.flash_frame["frameColor"] = (1, 0.1, 0.1, self.flash * 0.5)

        # on-screen message timeout
        if self.msg_timer is not None:
            self.msg_timer -= dt
            if self.msg_timer <= 0.0:
                self.msg_text.hide()
                self.msg_timer = None
        return task.cont


# ======================================================================
#  Stand-alone test run:  python levels/level1.py
# ======================================================================
if __name__ == "__main__":
    from direct.showbase.ShowBase import ShowBase

    app = ShowBase()
    holder = {}

    def level_done():
        print("Level 1 complete - the main game would start Level 2 now.")
        app.userExit()

    holder["level"] = Level1(app, on_complete=level_done)
    holder["level"].start()
    app.run()
    sys.exit(0)
