"""Apply UV markings, clean material presets and limited mesh details to v06."""
import hashlib
from math import cos, pi, sin
from pathlib import Path
import runpy

import bmesh
import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parent
SOURCES = ROOT.parent / "source"
BASE = SOURCES / "frontier-relay-07-shape-v06.blend"
MARKS = SOURCES / "frontier-relay-07-markings-v07.blend"
FINAL = SOURCES / "frontier-relay-07-materials-v08.blend"
PAINT = runpy.run_path(str(ROOT / "paint_maps.py"))
if any(p.exists() for p in (MARKS, FINAL)):
    raise RuntimeError("A destination already exists. Preserve it before generating a new iteration.")
if hashlib.sha256(BASE.read_bytes()).hexdigest() != "5d448f3bba603a28e9c95989e1d685bc96b666367b6e274b23280d1015b85848":
    raise RuntimeError("v06 differs from the approved source.")
if bpy.data.filepath or {o.name for o in bpy.context.scene.objects} != {"Cube","Light","Camera"}:
    raise RuntimeError("Start a fresh isolated Blender MCP session.")
bpy.ops.wm.open_mainfile(filepath=str(BASE),load_ui=False)
scene = bpy.context.scene
assert scene["shape_revision"] == "shape-v06"
objects = bpy.data.objects

def original(name):
    return bpy.data.materials["FR07 | " + name]


def shader(material):
    return material.node_tree.nodes.get("Principled BSDF")


def srgb(value):
    if isinstance(value,str):
        s = value.lstrip("#")
        value = [int(s[i:i+2],16)/255 for i in (0,2,4)]
    return tuple(c/12.92 if c <= .04045 else ((c+.055)/1.055)**2.4 for c in value) + (1.0,)


def apply_pbr(mat, color=None, roughness=None, glow=None):
    bsdf = shader(mat)
    bsdf.inputs["Metallic"].default_value = 0
    if color:
        mat.diffuse_color = srgb(color)
        bsdf.inputs["Base Color"].default_value = mat.diffuse_color
    if roughness is not None:
        bsdf.inputs["Roughness"].default_value = roughness
    if glow is not None:
        bsdf.inputs["Emission Color"].default_value = mat.diffuse_color
        bsdf.inputs["Emission Strength"].default_value = glow
    return mat


def map_image(stage, surface, mat):
    image = bpy.data.images.load(str(ROOT / "textures" / stage / (surface+"-basecolor.png")),
                                check_existing=True)
    image.colorspace_settings.name = "sRGB"
    image.pack()
    nodes = mat.node_tree.nodes
    tex = nodes.get("Graphics base color") or nodes.new("ShaderNodeTexImage")
    tex.name = "Graphics base color"
    tex.label = "Baked opaque surface graphics • sRGB"
    tex.image = image
    tex.extension = "EXTEND"
    mat.node_tree.links.new(tex.outputs["Color"],shader(mat).inputs["Base Color"])


def painted_uv(obj, surface, coordinates, mat):
    uv = obj.data.uv_layers.new(name="Surface graphics")
    obj.data.uv_layers.active = uv
    uv.active_render = True
    x0,x1,y0,y1 = PAINT["BOUNDS"][surface]
    for loop in obj.data.loops:
        p = obj.matrix_world @ obj.data.vertices[loop.vertex_index].co
        u,v = coordinates(p)
        uv.data[loop.index].uv = ((u-x0)/(x1-x0),(v-y0)/(y1-y0))
    obj.data.materials[0] = mat


maps = {
    "side": ("Warm white enamel", ["Horizontal aperture | surround"], lambda p: (p.y,p.z)),
    "roof": ("Warm white enamel", ["Continuous clipped fascia"], lambda p: (p.y,p.z-3.239+2.23-p.x)),
    "column": ("Fluorescent yellow green", ["Equipment column | vertical upper shell"], lambda p: (p.x,p.z)),
    "stairs": ("Deck stone grey", [f"Entry tread {i}" for i in (1,2,3)], lambda p: (p.x,p.y)),
}
painted = {}
for surface,(material_name,names,projection) in maps.items():
    mat = original(material_name).copy()
    mat.name = "FR07 PBR | Graphics " + surface
    painted[surface] = mat
    map_image("marks",surface,mat)
    for name in names:
        painted_uv(objects[name],surface,projection,mat)

scene["material_stage"] = "v07 / graphics only"
scene.render.filepath = "//../material-review/previews/02-markings.png"
bpy.ops.wm.save_as_mainfile(filepath=str(MARKS), compress=True)

# Fit the visible ends into the 40 mm gaps between the underside bays.
# Their upper parts still join the backing soffit.
for label in ("Left carrier","Corner carrier"):
    carrier = objects["Soffit support | " + label]
    for vertex in carrier.data.vertices:
        vertex.co.x *= .32 if vertex.co.y > 0 else .66
    carrier.data.update()

colors = PAINT["SWATCHES"]["finish"]
presets = {
    "Warm white enamel": (colors["enamel"], .39),
    "Fluorescent yellow green": (colors["lime"], .43),
    "Deck stone grey": (colors["deck"], .89),
    "Charcoal structure": ("#303337", .60),
    "Recess shadow": ("#202225", .76),
    "Door graphite": ("#42464a", .47),
    "Door graphite inset": ("#373b3f", .51),
    "Tinted window block": ("#233642", .19),
    "Signal orange red": (colors["signal"], .43),
}
for name,(color,roughness) in presets.items():
    apply_pbr(original(name),color,roughness)
for surface,mat in painted.items():
    material_name = maps[surface][0]
    color,roughness = presets[material_name]
    apply_pbr(mat,color,roughness)
    map_image("finish",surface,mat)

apply_pbr(original("Access cyan"),"#54d4ed",.29,.78)
apply_pbr(original("White fixture"),"#dce5e8",.32,.65)
indicator = original("Signal orange red").copy()
indicator.name = "FR07 PBR | Red position lamp"
apply_pbr(indicator,"#e94724",.34,.65)
objects["Left red underside fixture"].data.materials[0] = indicator


def feature(name, vertices, faces, collection, mat, bevel=0, smooth=False):
    data = bpy.data.meshes.new(name)
    center = sum((Vector(p) for p in vertices),Vector((0,0,0)))/len(vertices)
    data.from_pydata([Vector(v)-center for v in vertices],[],faces)
    bm = bmesh.new()
    try:
        bm.from_mesh(data)
        bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
        assert all(e.is_manifold for e in bm.edges)
        bm.to_mesh(data)
    finally:
        bm.free()
    obj = bpy.data.objects.new(name,data)
    collection.objects.link(obj)
    obj.location = center
    data.materials.append(mat)
    for poly in data.polygons:
        poly.use_smooth = smooth and len(poly.vertices)==4
    if bevel:
        mod = obj.modifiers.new("Fine edge break","BEVEL")
        mod.width = bevel
        mod.segments = 1
    return obj


def handle_profile(name, x0,x1,z0,z1, y0,y1, cut, material):
    corners = [(x0+cut,z0),(x1-cut,z0),(x1,z0+cut),(x1,z1-cut),
               (x1-cut,z1),(x0+cut,z1),(x0,z1-cut),(x0,z0+cut)]
    points = [(x,y,z) for y in (y0,y1) for x,z in corners]
    faces = [tuple(range(7,-1,-1)),tuple(range(8,16))]
    faces += [(i,(i+1)%8,(i+1)%8+8,i+8) for i in range(8)]
    return feature(name,points,faces,bpy.data.collections["04_Openings"],material,.005)


handle_profile("Door pull | chamfered inset bezel", 1.006,1.157,1.305,1.675,
               -2.238,-2.213,.024,original("Charcoal structure"))
handle_profile("Door pull | pocket", 1.033,1.130,1.335,1.646,
               -2.244,-2.236,.013,original("Recess shadow"))
handle_profile("Door pull | grip", 1.064,1.104,1.368,1.610,
               -2.264,-2.242,.009,original("Door graphite"))


# Two small folded returns replace the provisional vertical blocks.
for n,u in enumerate((1.51,1.80),1):
    obj = objects[f"Service upper stub {n}"]
    bpy.data.objects.remove(obj,do_unlink=True)
    y = -2.35 + (u+2.35)*1.135
    centers = [Vector((x,y,z)) for x,z in [
        (1.42,2.352),(1.465,2.352),(1.517,2.332),(1.553,2.295),
        (1.568,2.246),(1.568,2.16),(1.568,1.990)
    ]]
    radial = 12
    vertices = []
    for i,center in enumerate(centers):
        tangent = (centers[min(i+1,len(centers)-1)]-centers[max(0,i-1)]).normalized()
        across = Vector((0,1,0))
        other = tangent.cross(across)
        vertices.extend(center + .049*(cos(j*2*pi/radial)*across+sin(j*2*pi/radial)*other)
                        for j in range(radial))
    faces = [tuple(range(radial-1,-1,-1))]
    for i in range(len(centers)-1):
        for j in range(radial):
            a,b = i*radial+j,i*radial+(j+1)%radial
            faces.append((a,b,b+radial,a+radial))
    faces.append(tuple(range(len(vertices)-radial,len(vertices))))
    feature(f"Service return pipe {n}",vertices,faces,bpy.data.collections["03_Utility"],
            original("Charcoal structure"),smooth=True)

scene["art_status"] = "Clean markings and base materials / awaiting review"
scene["material_stage"] = "v08 / graphics and base materials"
scene.render.filepath = "//../material-review/previews/03-materials.png"
bpy.ops.wm.save_as_mainfile(filepath=str(FINAL),compress=True)
print(f"Saved {MARKS.name} and {FINAL.name}")
