"""Extend the v08 jambs into their mating parts and recess the rear joint."""
import hashlib
from pathlib import Path

import bmesh
import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT.parent / "source"
BASELINE = SOURCE / "frontier-relay-07-materials-v08.blend"
DESTINATION = SOURCE / "frontier-relay-07-seams-v09.blend"
EXPECTED_HASH = "affb505f1f3df2b721fb06ba721447d4deff09608163bb0f3893954fe09bbb77"
if DESTINATION.exists() or hashlib.sha256(BASELINE.read_bytes()).hexdigest() != EXPECTED_HASH:
    raise RuntimeError("Expected the approved v08 input and a new output path.")
if bpy.data.filepath or {o.name for o in bpy.context.scene.objects} != {"Cube", "Camera", "Light"}:
    raise RuntimeError("Start a fresh isolated Blender MCP session.")
bpy.ops.wm.open_mainfile(filepath=str(BASELINE), load_ui=False)
scene = bpy.context.scene
assert scene.get("material_stage") == "v08 / graphics and base materials"
objects = bpy.data.objects
shadow = bpy.data.materials["FR07 | Recess shadow"]
charcoal = bpy.data.materials["FR07 | Charcoal structure"]


def stop_ring(name, closure, depth_axis, overlap):
    """Keep the original eight reveal faces and join a sleeve + seating lip."""
    obj = objects[name]
    panel = objects[closure]
    original = obj.data
    assert len(original.vertices) == 16 and len(original.polygons) == 8
    points = [obj.matrix_world @ vertex.co for vertex in original.vertices]
    throat = points[8:16]
    closure_points = [panel.matrix_world @ v.co for v in panel.data.vertices]
    segment = [p[depth_axis] for p in closure_points]
    seat = (min(segment) + max(segment)) / 2
    assert abs(seat - throat[0][depth_axis]) > .006
    straight = [p.copy() for p in throat]
    for p in straight:
        p[depth_axis] = seat
    lip = [p.copy() for p in straight]
    for axis in range(3):
        if axis == depth_axis:
            continue
        throat_low, throat_high = min(p[axis] for p in throat), max(p[axis] for p in throat)
        edge_low = min(p[axis] for p in closure_points) + overlap
        edge_high = max(p[axis] for p in closure_points) - overlap
        assert throat_low < edge_low < edge_high < throat_high
        for v in lip:
            v[axis] = edge_low + (v[axis] - throat_low) / (throat_high - throat_low) * (edge_high - edge_low)
    points += straight + lip
    faces = [tuple(poly.vertices) for poly in original.polygons]
    for offset in (8, 16):
        for index in range(8):
            a = offset + index
            b = offset + (index + 1) % 8
            faces.append((a, b, b + 8, a + 8))
    mesh = bpy.data.meshes.new(name + " | v09 reveal and stop")
    inverse = obj.matrix_world.inverted()
    mesh.from_pydata([inverse @ p for p in points], [], faces)
    mesh.update()
    mesh.materials.append(original.materials[0])
    mesh.materials.append(shadow)
    for p in mesh.polygons:
        p.material_index = 0 if p.index < 8 else 1
    obj.data = mesh
    obj["seat_depth_m"] = seat
    obj["mate_overlap_m"] = overlap
    obj["mating_part"] = closure
    print(f"{name}: throat {throat[0][depth_axis]:.5f} m, seat {seat:.5f} m, lip overlap {overlap:.3f} m")


stop_ring("Entry cutout | return", "Recessed door leaf", 1, .028)
stop_ring("Horizontal aperture | return", "Tinted window backing", 0, .014)
stop_ring("Side service aperture | return", "Service well dark backing", 0, .016)

# The rear skin is already closed. Remove the raised dark strip and replace it
# with a shallow blind recess machined into that same skin.
wall = objects["Back enclosed wall"]
raised = objects["Rear central panel joint"]
rear_plane = max((wall.matrix_world @ vertex.co).y for vertex in wall.data.vertices)
bpy.data.objects.remove(raised, do_unlink=True)
width = .018
depth = .012
cut_mesh = bpy.data.meshes.new("Temporary rear joint cutter")
bm = bmesh.new()
bmesh.ops.create_cube(bm, size=1)
for vertex in bm.verts:
    vertex.co.x *= width
    vertex.co.y *= depth + .03
    vertex.co.z *= 3.02 - .92
bm.to_mesh(cut_mesh)
bm.free()
cutter = bpy.data.objects.new(cut_mesh.name, cut_mesh)
scene.collection.objects.link(cutter)
cutter.location = (0, rear_plane + (.03-depth)/2, (3.02 + .92)/2)
cutter.data.materials.append(charcoal)
groove = wall.modifiers.new("Blind panel joint, 18 mm by 12 mm", "BOOLEAN")
groove.operation = "DIFFERENCE"
groove.solver = "EXACT"
groove.material_mode = "TRANSFER"
groove.object = cutter
bpy.context.view_layer.update()

# Realize only the rear wall's stack. The front, glazing and equipment
# also retain their original normals, material values and transforms.
evaluated = wall.evaluated_get(bpy.context.evaluated_depsgraph_get())
rear_mesh = bpy.data.meshes.new_from_object(evaluated)
rear_mesh.name = "Back enclosed wall | v09 blind joint"
bm = bmesh.new()
try:
    bm.from_mesh(rear_mesh)
    if not all(e.is_manifold for e in bm.edges) or bm.calc_volume(signed=True) <= 0:
        raise RuntimeError("Rear wall is not a closed solid after groove subtraction.")
finally:
    bm.free()
assert any(
    abs((wall.matrix_world @ vertex.co).y - (rear_plane - depth)) < .0002
    for vertex in rear_mesh.vertices
)
wall.modifiers.clear()
wall.data = rear_mesh
bpy.data.objects.remove(cutter, do_unlink=True)
wall["blind_joint_width_m"] = width
wall["blind_joint_depth_m"] = depth
scene["seam_revision"] = "v09 / geometry joinery only"
scene["art_status"] = "Seam revision / awaiting visual review"
bpy.ops.wm.save_as_mainfile(filepath=str(DESTINATION), compress=True)
print(f"Saved {DESTINATION}")
