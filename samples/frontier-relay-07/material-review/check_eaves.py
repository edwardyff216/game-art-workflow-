"""Isolate the sources of the narrow lines under the v06 eaves."""
import json
from pathlib import Path

import bpy
from mathutils.bvhtree import BVHTree

root = Path(__file__).resolve().parent
target = root / "diagnostics"
target.mkdir(exist_ok=True)
scene = bpy.context.scene
assert scene["shape_revision"] == "shape-v06"
objects = bpy.data.objects
names = [o.name for o in bpy.data.collections["02_Roof"].objects]
depsgraph = bpy.context.evaluated_depsgraph_get()
report = {}
for name in names:
    obj = objects[name]
    evaluated = obj.evaluated_get(depsgraph)
    mesh = evaluated.to_mesh()
    vertices = [evaluated.matrix_world @ v.co for v in mesh.vertices]
    tree = BVHTree.FromPolygons(vertices, [tuple(p.vertices) for p in mesh.polygons])
    report[name] = {"smooth_base_faces": sum(p.use_smooth for p in obj.data.polygons),
                    "materials": [m.name for m in obj.data.materials],
                    "tree": tree}
for i, name in enumerate(names):
    report[name]["intersections"] = {
        other: len(hits)
        for other in names[i+1:]
        if (hits := report[name]["tree"].overlap(report[other]["tree"]))
    }
for record in report.values():
    del record["tree"]
(target/"eave-analysis.json").write_text(json.dumps(report,indent=2),encoding="utf-8")

scene.render.use_border = True
scene.render.use_crop_to_border = True
scene.render.border_min_x, scene.render.border_max_x = .37,.74
scene.render.border_min_y, scene.render.border_max_y = .664,.780
scene.render.resolution_percentage = 170
scene.cycles.samples = 18
for name, hidden in [
    ("v06-eave", []),
    ("v06-eave-without-carriers", ["Soffit support | Left carrier","Soffit support | Corner carrier"]),
    ("v06-eave-core", [n for n in names if n.startswith(("Soffit support", "Soffit panel"))]),
]:
    for candidate in names:
        objects[candidate].hide_render = candidate in hidden
    scene.render.filepath = str(target/(name+".png"))
    bpy.ops.render.render(write_still=True)
