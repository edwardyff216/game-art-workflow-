"""Build the editable exterior in the dedicated Blender MCP session."""
import json
import math
from pathlib import Path

import bmesh
import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
SETTINGS = json.loads((ROOT / "scene-settings.json").read_text(encoding="utf-8"))
SOURCE = ROOT / "source" / "frontier-relay-07.blend"
OWNER = "frontier-relay-07"
scene = bpy.context.scene
if bpy.data.filepath and Path(bpy.data.filepath).resolve() != SOURCE:
    raise RuntimeError("Open a fresh dedicated session or this sample source before building.")
if scene.get("sample_owner") != OWNER:
    if SOURCE.exists() or {obj.name for obj in scene.objects} != {"Cube", "Camera", "Light"}:
        raise RuntimeError("Expected an unused factory scene and a new sample source.")
    for obj in list(scene.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
else:
    for collection in list(scene.collection.children):
        if collection.get("sample_owner") != OWNER:
            continue
        for obj in list(collection.objects):
            data = obj.data
            bpy.data.objects.remove(obj, do_unlink=True)
            if data is not None and not data.users:
                bpy.data.batch_remove([data])
        bpy.data.collections.remove(collection)
scene["sample_owner"] = OWNER
scene["art_status"] = "Greybox / awaiting review"
scene.unit_settings.system = "METRIC"
scene.unit_settings.scale_length = 1.0


def collection(name):
    group = bpy.data.collections.new(name)
    group["sample_owner"] = OWNER
    scene.collection.children.link(group)
    return group


shell, roof, utility, openings, rooftop, platform, crate, review = [
    collection(name) for name in (
        "01_Shell", "02_Roof", "03_Utility", "04_Openings",
        "05_Rooftop", "06_Platform", "07_Crate", "90_Review"
    )
]


def material(name, rgb, roughness=0.7, glow=0):
    def linear(v):
        return ((v + .055) / 1.055) ** 2.4 if v > .04045 else v / 12.92

    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.diffuse_color = (*[linear(v) for v in rgb], 1)
    mat.use_nodes = True
    shader = mat.node_tree.nodes.get("Principled BSDF")
    shader.inputs["Base Color"].default_value = mat.diffuse_color
    shader.inputs["Roughness"].default_value = roughness
    shader.inputs["Emission Color"].default_value = mat.diffuse_color
    shader.inputs["Emission Strength"].default_value = glow
    return mat


white = material("FR07 | Warm white enamel", (.82, .81, .77))
lime = material("FR07 | Fluorescent yellow green", (.81, .91, .042))
dark = material("FR07 | Charcoal structure", (.21, .22, .23))
inner = material("FR07 | Recess shadow", (.105, .11, .12))
door_mat = material("FR07 | Door graphite", (.32, .33, .34))
door_field = material("FR07 | Door graphite inset", (.24, .25, .26))
glass = material("FR07 | Tinted window block", (.115, .19, .23), .39)
deck = material("FR07 | Deck stone grey", (.51, .50, .48))
red = material("FR07 | Signal orange red", (.83, .18, .08))
cyan = material("FR07 | Access cyan", (.21, .78, .88), .38, .35)
lamp = material("FR07 | White fixture", (.80, .84, .84), .4, .25)
grey = material("FR07 | Neutral review clay", (.61, .61, .61), .76)
ground_mat = material("FR07 | Studio ground", (.57, .56, .56))


def mesh(name, points, faces, group, mat, bevel=0, face_mats=None, recalc=True):
    if group != review:
        factor = SETTINGS["geometry"]["side_depth_multiplier"]
        # Preserve entry stair placement while deepening the station behind it.
        points = [(x, y if y < -2.35 else -2.35+(y+2.35)*factor, z)
                  for x, y, z in points]
    center = sum((Vector(p) for p in points), Vector()) / len(points)
    data = bpy.data.meshes.new(name)
    data.from_pydata([Vector(p) - center for p in points], [], faces)
    if recalc:
        bm = bmesh.new()
        bm.from_mesh(data)
        bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
        bm.to_mesh(data)
        bm.free()
    obj = bpy.data.objects.new(name, data)
    group.objects.link(obj)
    obj.location = center
    data.materials.append(mat)
    if face_mats:
        for index, m in face_mats.items():
            if m.name not in data.materials:
                data.materials.append(m)
            data.polygons[index].material_index = data.materials.find(m.name)
    if bevel:
        mod = obj.modifiers.new("Editable edge bevel", "BEVEL")
        mod.width = bevel
        mod.segments = 2
        obj.modifiers.new("Weighted normals", "WEIGHTED_NORMAL")
    return obj


def loft(name, rings, group, mat, bevel=0, cap=True, face_mats=None):
    n = len(rings[0])
    faces = []
    if cap:
        faces.append(tuple(reversed(range(n))))
    for ring in range(len(rings) - 1):
        for i in range(n):
            a = ring * n + i
            b = ring * n + (i + 1) % n
            faces.append((a, b, b + n, a + n))
    if cap:
        faces.append(tuple(range(n * (len(rings) - 1), n * len(rings))))
    return mesh(name, [p for ring in rings for p in ring], faces, group, mat,
                bevel, face_mats, recalc=cap)


def outline(x0, x1, y0, y1, cut):
    return [(x0+cut,y0), (x1-cut,y0), (x1,y0+cut), (x1,y1-cut),
            (x1-cut,y1), (x0+cut,y1), (x0,y1-cut), (x0,y0+cut)]


def horizontal(bounds, z, clip):
    return [(x, y, z) for x, y in outline(*bounds, clip)]


def box(name, x0, x1, y0, y1, z0, z1, group, mat, bevel=.018):
    corners = [(x0,y0), (x1,y0), (x1,y1), (x0,y1)]
    return loft(name, [[(x, y, z) for x, y in corners] for z in (z0, z1)],
                group, mat, bevel)


def front(u, z, depth):
    return (u, -2.35 + depth, z)


def right(u, z, depth):
    return (1.70 - depth, u, z)


def ring_points(axis, bounds, clip, depth):
    return [axis(u, z, depth) for u, z in outline(*bounds, clip)]


def profile(name, axis, bounds, clip, depths, group, mat, bevel=.008):
    return loft(name, [ring_points(axis, bounds, clip, d) for d in depths],
                group, mat, bevel)


def recess(name, axis, outer, center, cut, inner_bounds, inner_cut,
           group, face, lining, depth, at=0):
    # A face annulus around an actual hole. The second annulus returns into
    # the shell, with a separate dark back panel added by the caller.
    perimeter = ring_points(axis, outer, .00001, at)
    opening = ring_points(axis, center, cut, at)
    throat = ring_points(axis, inner_bounds, inner_cut, at + depth)
    loft(name + " | surround", [perimeter, opening], group, face, cap=False)
    loft(name + " | return", [opening, throat], group, lining, cap=False)


# Three treads between two paving wings. The upper tread is flush with the
# station floor, so the doorway has no extra curb.
for index, (y0, y1, z) in enumerate([
    (-3.59, -3.25, .15), (-3.25, -2.91, .30), (-2.91, -2.35, .45)
], 1):
    box(f"Entry tread {index}", -1.23, 2.02, y0, y1, 0, z, platform, deck, .019)

for label, xs, ys in [
    ("Left", [-2.19, -1.236], [-3.57, -2.47, -2.35]),
    ("Core", [-2.19, -1.05, .15, 2.02], [-2.35, -.68, .99, 2.66]),
]:
    for ix, (x0, x1) in enumerate(zip(xs, xs[1:]), 1):
        for iy, (y0, y1) in enumerate(zip(ys, ys[1:]), 1):
            box(f"{label} deck {ix}.{iy}", x0+.006, x1-.006, y0+.006, y1-.006,
                0, .45, platform, deck, .027)

# The side apron widens toward the steps. Its paving follows the same
# footprint, with the inner edge aligned to the entrance tread.
right_tiles = [-3.57, -2.45, -1.05, .37, 1.61, 2.66]
for i, (a,b) in enumerate(zip(right_tiles,right_tiles[1:]), 1):
    def side_point(fraction, y):
        width = 2.08 - 1.14 * (y-right_tiles[0])/(right_tiles[-1]-right_tiles[0])
        return (2.028 + fraction*width, y + fraction*.65*max(0,1-(y+3.57)/2.6))
    for j, (left_edge,right_edge) in enumerate(((.004,.496),(.504,.996)), 1):
        corners = [side_point(f,y) for f,y in (
            (left_edge,a+.007),(right_edge,a+.007),(right_edge,b-.007),(left_edge,b-.007)
        )]
        loft(f"Right apron tile {i}.{j}", [[(x,y,z) for x,y in corners] for z in (0,.45)],
             platform, deck, .027)

# Outer wall skins and heavy base; the doorway is left open in the skin.
box("Left enclosed flank", -1.70, -1.57, -2.34, 2.34, .45, 3.04, shell, white)
box("Back enclosed wall", -1.68, 1.69, 2.23, 2.35, .45, 3.04, shell, white)
box("Left continuous base strip", -1.719, -1.699, -2.32, 2.30, .46, .91, shell, lime, .009)
box("Rear continuous base strip", -1.68, 1.69, 2.35, 2.37, .46, .91, shell, lime, .009)
box("Rear central panel joint", -.014, .014, 2.348, 2.356, .92, 3.02, shell, dark, .003)

def door_axis(u, z, depth):
    return front(.50 + (u-.50)*SETTINGS["geometry"]["door_width_multiplier"], z, depth)


def door_bounds(bounds):
    left, right_edge, bottom, top = bounds
    return (door_axis(left, 0, 0)[0], door_axis(right_edge, 0, 0)[0], bottom, top)


door_outer = door_bounds((-.49, 1.49, .45, 2.71))
door_throat = door_bounds((-.40, 1.40, .49, 2.63))
recess("Entry cutout", front, (-1.69, 1.69, .45, 3.04), door_outer, .16,
       door_throat, .13, shell, white, dark, .11)
profile("Recessed door leaf", door_axis, (-.34, 1.33, .49, 2.59), .125,
        (.13, .19), openings, door_mat, .014)
profile("Door leaf inset field", door_axis, (-.24, 1.23, .61, 2.46), .13,
        (.115, .132), openings, door_field, .01)
mesh("Door lower orange block", [door_axis(u,z,.111) for u,z in
     [(0.54,.615),(1.23,.615),(1.23,1.22)]], [(0,1,2)], openings, red)
profile("Access panel housing", door_axis, (1.57, 1.74, 1.96, 2.52), .045,
        (-.07, .012), openings, dark)
profile("Access panel cyan face", door_axis, (1.605, 1.705, 2.01, 2.47), .021,
        (-.079, -.068), openings, cyan, .004)

win_outer = (-1.78, .87, 2.04, 2.64)
recess("Horizontal aperture", right, (-2.34, 1.04, .45, 3.04), win_outer, .105,
       (-1.73,.82,2.09,2.59), .087, shell, white, dark, .135)
profile("Tinted window backing", right, (-1.73,.82,2.09,2.59), .086,
        (.137,.18), openings, glass)

service_outer = (1.20, 2.17, 1.08, 2.48)
recess("Side service aperture", right, (1.055, 2.34, .45, 3.04), service_outer, .095,
       (1.235,2.135,1.115,2.445), .073, shell, white, dark, .12)
profile("Service well dark backing", right, (1.235,2.135,1.115,2.445), .073,
        (.29,.32), utility, inner)
profile("Service box", right, (1.34,2.015,1.19,2.00), .055,
        (.10,.30), utility, dark, .017)
profile("Service orange block", right, (1.42,1.93,1.75,1.91), .009,
        (.094,.10), utility, red, .002)
for num, u in enumerate([1.51, 1.80], 1):
    profile(f"Service upper stub {num}", right, (u-.065,u+.065,1.98,2.34), .047,
            (.17,.23), utility, dark, .011)
for ix, (u0,u1) in enumerate([(-2.34,-1.55),(-1.54,.00),(.01,1.04),(1.055,2.33)], 1):
    top = .89 if ix != 1 else .94
    contour = [(u0,.46),(u1,.46),(u1,.88),(u1-.14,top),(u0,top)]
    loft(f"Side base enamel panel {ix}", [[right(u,z,d) for u,z in contour]
         for d in (-.04,.005)], shell, lime, .010)

# Front column has a real angled toe. Its top and lower shell are separate.
def column_shape(name, z0, knee, z1, level, mat):
    rings = []
    for z,y in [(z0,-2.69),(knee,-2.69),(z1,-2.49)]:
        rings.append(horizontal((-1.78,-.73,y,-2.06), z, level))
    return loft(name, rings, utility, mat, .018)


column_shape("Equipment column | dark footing", .45, .53, .72, .07, dark)
column_shape("Equipment column | flared lower shell", .66, 1.10, 1.44, .073, lime)
loft("Equipment column | vertical upper shell", [
     horizontal((-1.78,-.73,-2.49,-2.06), z, .068) for z in (1.452,3.035)],
     utility, lime, .022)

# Thick lid assembled as a continuous set of closed polygon rings.
loft("Continuous dark soffit", [
    horizontal((-2.00,2.02,-2.64,2.50), 2.975, .19),
    horizontal((-2.23,2.18,-2.86,2.69), 3.135, .15),
], roof, dark, .021)
loft("Continuous clipped fascia", [
    horizontal((-2.235,2.185,-2.865,2.695), 3.13, .16),
    horizontal((-2.27,2.23,-2.91,2.74), 3.215, .17),
    horizontal((-2.27,2.23,-2.91,2.74), 3.46, .17),
    horizontal((-2.20,2.16,-2.84,2.67), 3.53, .16),
], roof, white, .017)
box("Entry white underside fixture", .12, .94, -2.78, -2.64, 3.017, 3.038, roof, lamp, .012)
box("Left red underside fixture", -1.60, -1.22, -2.798, -2.67, 3.03, 3.06, roof, red, .014)

# Roof HVAC uses a shallow housing opening with actual individual slats.
def vent_face(u, z, d):
    return (u, -.38 + d, z)


recess("Roof HVAC intake", vent_face, (.02,1.54,3.53,4.06),
       (.18,1.38,3.60,3.99), .035, (.20,1.36,3.62,3.97), .026,
       rooftop, white, dark, .08)
box("HVAC structure rear", .02, 1.54, -.20, .59, 3.53, 4.06, rooftop, white, .035)
box("HVAC housing left cheek", .02, .17, -.38, -.20, 3.53, 4.06, rooftop, white)
box("HVAC housing right cheek", 1.40, 1.54, -.38, -.20, 3.53, 4.06, rooftop, white)
box("HVAC housing top", .17, 1.40, -.38, -.18, 3.985, 4.06, rooftop, white, .013)
box("HVAC housing sill", .17, 1.40, -.38, -.18, 3.53, 3.603, rooftop, white, .012)
box("HVAC louver shadow well", .195, 1.37, -.278, -.251, 3.61, 3.98, rooftop, inner, .004)
for i in range(4):
    z = 3.645 + i * .087
    box(f"HVAC louver {i+1}", .21, 1.35, -.346, -.267, z, z+.038, rooftop, dark, .006)
box("HVAC lime inspection band", 1.541, 1.549, .055, .21, 3.548, 4.045, rooftop, lime, .003)
for obj in rooftop.objects:
    obj.location.x += .08
    obj.location.y += .34
loft("Yellow roof utility cover", [
    horizontal((-1.90,-.75,-2.15,-1.37), z, clip)
    for z,clip in [(3.53,.06),(3.93,.065),(4.04,.18)]
], rooftop, lime, .02)
box("Roof utility dark end", -.75,-.53,-2.15,-1.37,3.53,3.70,rooftop,dark,.016)
box("Roof utility yellow end", -.75,-.53,-2.15,-1.37,3.71,4.03,rooftop,lime,.02)
for obj in rooftop.objects:
    if obj.name.startswith(("Yellow roof utility", "Roof utility")):
        obj.location.x -= .15
        obj.location.y -= .26

# Crate sits on the side paving. Centerline accent is a material region
# represented by surface faces at this resolution.
cx, cy = 2.74, 1.18
x0,x1,y0,y1 = cx-.40,cx+.40,cy-.51,cy+.51
box("Independent cargo case shell", x0,x1,y0,y1,.47,.99,crate,white,.06)
box("Cargo case lid gasket", x0-.018,x1+.018,y0-.018,y1+.018,.977,1.015,crate,dark,.031)
box("Cargo case lid", x0-.028,x1+.028,y0-.028,y1+.028,1.012,1.16,crate,white,.041)
box("Cargo case central lime face", x0+.29,x0+.52,y0-.003,y0+.002,.51,.973,crate,lime,.001)
box("Cargo case central lime top", x0+.29,x0+.52,y0+.01,y1-.01,1.160,1.164,crate,lime,.001)
for i, x in enumerate([x0+.047,x1-.047],1):
    for j, y in enumerate([y0+.047,y1-.047],1):
        for k, z in enumerate([.51,1.111],1):
            guard = .080 if k == 2 else .067
            box(f"Cargo corner guard {i}.{j}.{k}",x-guard,x+guard,y-guard,y+guard,z-.06,z+.06,crate,dark,.023)
box("Cargo latch block",cx-.126,cx+.126,y0-.047,y0+.007,.92,1.035,crate,dark,.014)


def oriented(name, datablock, position, target):
    obj = bpy.data.objects.new(name, datablock)
    review.objects.link(obj)
    obj.location = position
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()
    return obj


def camera(name, position, target, projection):
    data = bpy.data.cameras.new(name)
    data.type = projection
    data.clip_start, data.clip_end = SETTINGS["hero_camera"]["clip_m"]
    data.dof.use_dof = False
    return oriented(name, data, position, target)


config = SETTINGS["hero_camera"]
target = Vector(config["target_m"])
azimuth, elevation = [math.radians(config[key]) for key in
                      ("azimuth_from_front_deg", "elevation_deg")]
direction = Vector((math.sin(azimuth)*math.cos(elevation),
                    -math.cos(azimuth)*math.cos(elevation), math.sin(elevation)))
hero = camera("Camera_Reference", target + direction * config["distance_m"],
              target, config["projection"])
hero.data.lens = config["lens_mm"]
hero.data.sensor_width = config["sensor_width_mm"]
hero.data.sensor_fit = "HORIZONTAL"
scene.camera = hero
z = SETTINGS["inspection_camera"]["target_z_m"]
for name, position, focus in [
    ("Front",(.9,-16,z),(.9,0,z)), ("Right",(16,-.37,z),(0,-.37,z)),
    ("Back",(.9,16,z),(.9,0,z)),
    ("Rear_ThreeQuarter",(-11,14,9),(.1,0,1.9))
]:
    view = camera("Camera_" + name, position, focus, "ORTHO")
    scale_key = "rear_three_quarter_scale_m" if name == "Rear_ThreeQuarter" else "orthographic_scale_m"
    view.data.ortho_scale = SETTINGS["inspection_camera"][scale_key]

lighting = SETTINGS["lighting"]
world = bpy.data.worlds.get("FR07 | Neutral world") or bpy.data.worlds.new("FR07 | Neutral world")
scene.world = world
world.use_nodes = True
background = world.node_tree.nodes.get("Background")
background.inputs[0].default_value = (.52,.54,.58,1)
background.inputs[1].default_value = lighting["world_strength"]
key = bpy.data.lights.new("Sun key", "SUN")
key.energy = lighting["sun_energy"]
key.angle = math.radians(lighting["sun_angle_deg"])
oriented("Sun key", key, lighting["sun_direction_from_m"], (0,0,0))
fill = bpy.data.lights.new("Large bounce fill", "AREA")
fill.energy = lighting["fill_energy_w"]
fill.shape = "DISK"
fill.size = lighting["fill_size_m"]
oriented("Large bounce fill", fill, lighting["fill_position_m"], (0,0,1.7))
box("Studio floor", -500,500,-500,500,-.115,-.001,review,ground_mat,0)

scene.render.engine = "CYCLES"
scene.cycles.samples = 32
scene.cycles.use_denoising = True
scene.render.resolution_x, scene.render.resolution_y = SETTINGS["resolution_px"]
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.view_settings.view_transform = lighting["view_transform"]
scene.view_settings.exposure = lighting["exposure_ev"]
scene.render.filepath = "//../previews/02-colour.png"
scene.view_layers[0].name = "Base colours"
grey_layer = scene.view_layers.get("Neutral grey") or scene.view_layers.new("Neutral grey")
grey_layer.material_override = grey
grey_layer.use = False
for area in bpy.context.screen.areas:
    if area.type == "VIEW_3D":
        area.spaces.active.region_3d.view_perspective = "CAMERA"
        area.spaces.active.shading.color_type = "MATERIAL"

bpy.context.preferences.filepaths.save_version = 0
bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE))
print(f"RELAY_SAVED objects={len(scene.objects)} meshes={sum(o.type == 'MESH' for o in scene.objects)}")
