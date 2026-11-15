"""Read the approved v08 camera and project real mesh vertices for Godot comparison."""
import json
import math
from pathlib import Path

import bpy
from bpy_extras.object_utils import world_to_camera_view

scene = bpy.context.scene
assert scene["material_stage"] == "v08 / graphics and base materials"
camera = scene.camera
data = camera.data
width, height = scene.render.resolution_x, scene.render.resolution_y
assert scene.render.resolution_percentage == 100
assert scene.render.pixel_aspect_x == scene.render.pixel_aspect_y
assert data.type == "PERSP" and data.sensor_fit == "HORIZONTAL"
assert data.shift_x == data.shift_y == 0


def godot(point):
    return [point.x, point.z, -point.y]


vertical_sensor = data.sensor_width * height / width
result = {
    "blender_version": bpy.app.version_string,
    "source": bpy.data.filepath,
    "resolution": [width, height],
    "focal_mm": data.lens,
    "sensor_width_mm": data.sensor_width,
    "effective_sensor_height_mm": vertical_sensor,
    "horizontal_fov_deg": math.degrees(2 * math.atan(data.sensor_width / (2 * data.lens))),
    "vertical_fov_deg": math.degrees(2 * math.atan(vertical_sensor / (2 * data.lens))),
    "godot_origin": godot(camera.matrix_world.translation),
    "godot_basis_columns": [godot(camera.matrix_world.col[i].to_3d()) for i in range(3)],
    "clip_m": [data.clip_start, data.clip_end],
    "landmarks": [],
}
for name in ("Continuous clipped fascia", "Entry tread 1", "Entry tread 3",
             "Horizontal aperture | surround", "Independent cargo case shell",
             "Equipment column | vertical upper shell", "HVAC housing top"):
    obj = bpy.data.objects[name]
    point = obj.matrix_world @ obj.data.vertices[0].co
    ndc = world_to_camera_view(scene, camera, point)
    result["landmarks"].append({
        "object": name,
        "godot_point": godot(point),
        "blender_pixel": [ndc.x * width, (1.0 - ndc.y) * height],
    })
out = Path(__file__).resolve().parent / "project" / "camera-reference.json"
out.write_text(json.dumps(result, indent=2), encoding="utf-8")
print(f"Verified Blender camera and {len(result['landmarks'])} points: {out}")
