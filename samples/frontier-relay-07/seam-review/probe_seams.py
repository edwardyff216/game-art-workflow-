"""Read-only visual-ray probes and local topology details from the saved sources."""
from collections import Counter
import json
from math import radians, tan
from pathlib import Path

import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

root = Path(__file__).resolve().parent
objects = bpy.data.objects
scene = bpy.context.scene
tag = "after" if scene.get("seam_revision") else "before"
deps = bpy.context.evaluated_depsgraph_get()
surfaces = []
for obj in scene.objects:
    if obj.type != "MESH" or any(c.name == "90_Review" for c in obj.users_collection):
        continue
    ev = obj.evaluated_get(deps)
    data = ev.to_mesh()
    surfaces.append((obj.name, BVHTree.FromPolygons(
        [ev.matrix_world @ v.co for v in data.vertices],
        [tuple(p.vertices) for p in data.polygons])))
    ev.to_mesh_clear()


def cast(origin, direction, exclude=()):
    closest = 50.0
    result = {"object": "no hit"}
    for name, tree in surfaces:
        if name in exclude:
            continue
        point, normal, _, distance = tree.ray_cast(origin, direction, closest)
        if point is not None and distance <= closest:
            closest = distance
            result = {"object": name, "point": list(point), "normal": list(normal)}
    return result


results = {}
for marker, name, target, axis, outward, offsets in [
    ("door", "Entry cutout | return", "Recessed door leaf", 1, -1, [.002,.010,.023,.038]),
    ("window", "Horizontal aperture | return", "Tinted window backing", 0, 1, [.001,.002,.004,.010]),
    ("service", "Side service aperture | return", "Service well dark backing", 0, 1, [.003,.009,.018,.032]),
]:
    obj = objects[name]
    panel = objects[target]
    ring = [obj.matrix_world @ v.co for v in obj.data.vertices[8:16]]
    center = sum(ring, Vector()) / len(ring)
    plane = max((panel.matrix_world @ v.co)[axis]*outward for v in panel.data.vertices)
    lateral = [i for i in (0,1) if i != axis][0]
    own = [name,target]
    if marker == "door":
        own += ["Door leaf inset field","Door lower orange block",
                "Door pull | chamfered inset bezel","Door pull | pocket","Door pull | grip"]
    if marker == "service":
        own += ["Service box","Service orange block","Service return pipe 1","Service return pipe 2"]
    outcomes = {}
    outside = []
    for angle in [-58,-32,0,32,58]:
        vector = Vector()
        vector[axis] = outward
        vector[lateral] = tan(radians(angle))
        vector.z = .05
        counts = Counter()
        for side in range(8):
            a,b = ring[side],ring[(side+1)%8]
            for ratio in (.28,.51,.72):
                edge = a.lerp(b,ratio)
                for d in offsets:
                    aim = edge + (center-edge).normalized()*d
                    direction = -vector.normalized()
                    picked = cast(aim+vector*3,direction)
                    hit = picked["object"]
                    if hit not in own and not hit.endswith("| surround"):
                        counts[hit] += 1
                        if len(outside)<12:
                            outside.append({"angle":angle,"aim":list(aim),**picked})
        outcomes[str(angle)] = dict(counts)
    results[marker] = {
        "front_reveal_faces":8,"total_reveal_faces":len(obj.data.polygons),
        "throat_axis_m":ring[0][axis],"closure_front_axis_m":plane*outward,
        "reveal_normal_checks": [
            round((obj.matrix_world.to_3x3() @ p.normal)
                  .dot((center-obj.matrix_world @ p.center).normalized()),4)
            for p in obj.data.polygons[:8]
        ],
        "rays": len(outcomes)*8*3*len(offsets), "unintended_hits_by_angle":outcomes,
        "sample_hits":outside,
    }

rear = Vector((0,6,1.7))
results["rear"] = {
    "centre":cast(rear,Vector((0,-1,0))),
    "without_raised_trim":cast(rear,Vector((0,-1,0)),["Rear central panel joint"]),
    "beside_joint":cast(rear+Vector((.04,0,0)),Vector((0,-1,0))),
}
(root/"reports"/f"mesh-rays-{tag}.json").write_text(json.dumps(results,indent=2),encoding="utf-8")
for label, data in results.items():
    if label!="rear":
        print(label, sum(sum(row.values()) for row in data["unintended_hits_by_angle"].values()),"of",data["rays"])
print("rear",results["rear"])
