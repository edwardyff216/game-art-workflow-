"""Render consistent composition passes from the saved sample, using Blender CLI."""
import argparse
import json
import sys
from pathlib import Path

import bpy
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Vector

parser = argparse.ArgumentParser()
parser.add_argument("--draft", action="store_true")
args = parser.parse_args(sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else [])
root = Path(__file__).resolve().parents[1]
scene = bpy.context.scene
if scene.get("sample_owner") != "frontier-relay-07":
    raise RuntimeError("This script expects the saved Frontier Relay 07 sample.")

scene.cycles.samples = 14 if args.draft else 40
scene.render.resolution_percentage = 65 if args.draft else 100
cycles = bpy.context.preferences.addons["cycles"].preferences
for api in ("OPTIX", "CUDA"):
    try:
        cycles.compute_device_type = api
        cycles.refresh_devices()
        devices = [device for device in cycles.devices if device.type == api]
        if devices:
            for device in cycles.devices:
                device.use = device.type == api
            scene.cycles.device = "GPU"
            break
    except (TypeError, RuntimeError):
        continue

passes = [("01-grey", "Reference", "Neutral grey"), ("02-colour", "Reference", "Base colours")]
if not args.draft:
    passes += [("03-front", "Front", "Base colours"), ("04-right", "Right", "Base colours"),
               ("05-back", "Back", "Base colours")]
    passes += [("06-rear-three-quarter", "Rear_ThreeQuarter", "Base colours")]
report = {"blender": bpy.app.version_string, "render_device": scene.cycles.device, "passes": []}
for filename, camera_name, layer_name in passes:
    camera = bpy.data.objects["Camera_" + camera_name]
    scene.camera = camera
    bpy.data.objects["Studio floor"].hide_render = camera_name in {"Front", "Right", "Back"}
    for layer in scene.view_layers:
        layer.use = layer.name == layer_name
    tag = "draft-" if args.draft else ""
    scene.render.filepath = str(root / "previews" / (tag + filename + ".png"))
    bpy.ops.render.render(write_still=True)
    report["passes"].append({
        "file": scene.render.filepath,
        "camera": camera.name,
        "layer": layer_name,
        "position_m": list(camera.location),
        "rotation_deg_xyz": [v * 180 / 3.14159265359 for v in camera.rotation_euler],
        "projection": camera.data.type,
    })

hero = bpy.data.objects["Camera_Reference"]
settings = json.loads((root / "scene-settings.json").read_text(encoding="utf-8"))
back_fascia_y = -2.35 + (2.57 + 2.35) * settings["geometry"]["side_depth_multiplier"]
roof_corners = {
    "fascia_front_left": (-2.10,-2.91,3.46), "fascia_front_right": (2.06,-2.91,3.46),
    "fascia_back_right": (2.23,back_fascia_y,3.46), "entry_threshold": (.50,-2.35,.45),
}
width, height = scene.render.resolution_x, scene.render.resolution_y
report["projected_landmarks_at_full_size_px"] = {}
for name, point in roof_corners.items():
    ndc = world_to_camera_view(scene, hero, Vector(point))
    report["projected_landmarks_at_full_size_px"][name] = [
        round(ndc.x*width, 1), round((1-ndc.y)*height, 1)
    ]
(root / "reports" / ("draft-render.json" if args.draft else "render.json")).write_text(
    json.dumps(report, indent=2), encoding="utf-8"
)
