"""Patch the saved v04 sample in Blender and save a separate shape revision."""
import hashlib
import runpy
from pathlib import Path

import bmesh
import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parent
SAMPLE = ROOT.parent
BASELINE = SAMPLE / "source" / "frontier-relay-07.blend"
camera_tools = runpy.run_path(str(ROOT / "camera_match.py"))
REVISION = camera_tools["SETTINGS"]["revision"]
OUTPUT = SAMPLE / "source" / f"frontier-relay-07-{REVISION}.blend"
EXPECTED = "c785e5e755608e67eee1919fb66e647ad045c5c69a981f28a79a95bd96b60147"
if OUTPUT.exists():
    raise RuntimeError(f"Version already exists: {OUTPUT}")
if hashlib.sha256(BASELINE.read_bytes()).hexdigest() != EXPECTED:
    raise RuntimeError("The reviewed v04 baseline has changed.")
if bpy.data.filepath or {o.name for o in bpy.context.scene.objects} != {"Cube", "Camera", "Light"}:
    raise RuntimeError("Run in a dedicated, fresh Blender MCP session.")
bpy.ops.wm.open_mainfile(filepath=str(BASELINE), load_ui=False)
scene = bpy.context.scene
assert scene["sample_owner"] == "frontier-relay-07"
roof = bpy.data.collections["02_Roof"]
utility = bpy.data.collections["03_Utility"]
charcoal = bpy.data.materials["FR07 | Charcoal structure"]


def xyz(x, y, z):
    # Same coordinate convention as the approved source. Model space dimensions
    # for the existing walls, deck, door and HVAC remain identical.
    if y > -2.35:
        y = -2.35 + (y + 2.35) * 1.135
    return (x, y, z)


def replace_loft(name, rings, collection, edge_m, material=None):
    sides = len(rings[0])
    assert all(len(ring) == sides for ring in rings)
    vertices = [Vector(p) for ring in rings for p in ring]
    center = sum(vertices, Vector((0,0,0))) / len(vertices)
    faces = [tuple(reversed(range(sides)))]
    for index in range(len(rings)-1):
        offset = index * sides
        for side in range(sides):
            a = offset + side
            b = offset + (side + 1) % sides
            faces.append((a, b, b + sides, a + sides))
    faces.append(tuple(range(len(vertices)-sides, len(vertices))))
    mesh = bpy.data.meshes.new(name + " | " + REVISION)
    mesh.from_pydata([v - center for v in vertices], [], faces)
    bm = bmesh.new()
    try:
        bm.from_mesh(mesh)
        bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
        if any(not e.is_manifold for e in bm.edges) or bm.calc_volume(signed=True) <= 0:
            raise RuntimeError(f"Invalid closed profile: {name}")
        bm.to_mesh(mesh)
    finally:
        bm.free()
    obj = bpy.data.objects.get(name)
    if obj:
        assert collection in obj.users_collection
        previous_mesh = obj.data
        material = previous_mesh.materials[0] if material is None else material
        obj.data = mesh
        bpy.data.meshes.remove(previous_mesh)
        obj.modifiers.clear()
    else:
        obj = bpy.data.objects.new(name, mesh)
        collection.objects.link(obj)
    mesh.materials.append(material)
    obj.location = center
    bevel = obj.modifiers.new("Single edge break", "BEVEL")
    bevel.width = edge_m
    bevel.segments = 1
    bevel.limit_method = "ANGLE"
    return obj


def cut_rectangle(x0, x1, y0, y1, cut):
    return [(x0+cut,y0), (x1-cut,y0), (x1,y0+cut), (x1,y1-cut),
            (x1-cut,y1), (x0+cut,y1), (x0,y1-cut), (x0,y0+cut)]


def roof_ring(bounds, z, cut, grooves=False):
    x0,x1,y0,y1 = bounds
    points = cut_rectangle(x0,x1,y0,y1,cut)
    if grooves:
        seam_x, seam_y = -.58, .91
        front_joint = [(seam_x-.017,y0), (seam_x-.010,y0+.017),
                       (seam_x+.010,y0+.017), (seam_x+.017,y0)]
        side_joint = [(x1,seam_y-.017), (x1-.017,seam_y-.010),
                      (x1-.017,seam_y+.010), (x1,seam_y+.017)]
        points = points[:1] + front_joint + points[1:3] + side_joint + points[3:]
    return [xyz(x,y,z) for x,y in points]


# Crown, outer face and underside chamfer remain readily visible as planes.
# The main eave envelope is inherited from v04.
replace_loft("Continuous clipped fascia", [
    roof_ring((-2.16,2.12,-2.81,2.64), 3.168, .24, True),
    roof_ring((-2.27,2.23,-2.91,2.74), 3.239, .22, True),
    roof_ring((-2.27,2.23,-2.91,2.74), 3.444, .14, True),
    roof_ring((-2.18,2.14,-2.82,2.65), 3.53, .145, True),
], roof, .0045)
replace_loft("Continuous dark soffit", [
    roof_ring((-1.83,1.83,-2.48,2.49), 2.958, .21),
    roof_ring((-2.14,2.12,-2.80,2.66), 3.093, .21),
    roof_ring((-2.20,2.16,-2.85,2.68), 3.172, .20),
], roof, .007)


def underside_plate(name, corners, thickness, edge, existing_material=None):
    rings = [[xyz(x,y,z + dz) for x,y,z in corners] for dz in (0,thickness)]
    return replace_loft(name, rings, roof, edge, existing_material)


for label, left, right in [
    ("Left bay", -1.93, -1.16), ("Entry bay", -1.12, 1.31),
    ("Corner bay", 1.35, 1.78),
]:
    underside_plate("Soffit panel | " + label, [
        (left+.08,-2.785,3.071), (right-.08,-2.785,3.071),
        (right,-2.48,2.940), (left,-2.48,2.940),
    ], .029, .0035, charcoal)
underside_plate("Soffit panel | Right return", [
    (1.815,-2.24,2.944), (2.085,-2.08,3.058),
    (2.085,2.36,3.058), (1.815,2.43,2.944),
], .032, .004, charcoal)
for label, x in [("Left carrier", -1.14), ("Corner carrier", 1.33)]:
    underside_plate("Soffit support | " + label, [
        (x-.035,-2.75,3.043), (x+.035,-2.75,3.043),
        (x+.048,-2.48,2.921), (x-.048,-2.48,2.921),
    ], .045, .005, charcoal)
underside_plate("Entry white underside fixture", [
    (.10,-2.740,3.041), (.90,-2.740,3.041),
    (.90,-2.580,2.971), (.10,-2.580,2.971),
], .028, .0025)
underside_plate("Left red underside fixture", [
    (-1.65,-2.76,3.050), (-1.28,-2.76,3.050),
    (-1.28,-2.67,3.012), (-1.65,-2.67,3.012),
], .026, .0025)


def column_ring(bounds, height, cut):
    points = cut_rectangle(*bounds, cut)
    return [xyz(x,y,height(x) if callable(height) else height) for x,y in points]


toe = (-1.88,-.73,-2.76,-2.06)
middle = (-1.75,-.73,-2.50,-2.06)
ankle = (-1.86,-.73,-2.74,-2.06)


def plinth_top(x):
    return .565 + .255 * (x - toe[0]) / (toe[1] - toe[0])


replace_loft("Equipment column | dark footing", [
    column_ring(ankle, .45, .065),
    column_ring(toe, .492, .052),
    column_ring(toe, plinth_top, .052),
], utility, .012)
replace_loft("Equipment column | flared lower shell", [
    column_ring(toe, lambda x: plinth_top(x) + .005, .052),
    column_ring(toe, 1.085, .052),
    column_ring(middle, 1.365, .050),
    column_ring(middle, 1.545, .050),
], utility, .008)
replace_loft("Equipment column | vertical upper shell", [
    column_ring(middle, z, .050) for z in (1.554, 2.99)
], utility, .006)

camera_tools["apply_camera"](scene)
scene["shape_revision"] = REVISION
scene["art_status"] = "Shape pass / awaiting review"
scene.render.filepath = "//../shape-review/previews/after-colour.png"
bpy.ops.wm.save_as_mainfile(filepath=str(OUTPUT), compress=True)
print(f"Saved {OUTPUT} with {len(scene.objects)} objects")
