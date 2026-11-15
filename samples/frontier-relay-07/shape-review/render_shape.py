"""Reopen the saved source and render the locked camera on each revision."""
import argparse
import json
import runpy
import sys
from pathlib import Path

import bpy

ROOT = Path(__file__).resolve().parent
camera_tools = runpy.run_path(str(ROOT / "camera_match.py"))
parser = argparse.ArgumentParser()
parser.add_argument("pass_name", choices=["trial", "before", "after"])
args = parser.parse_args(sys.argv[sys.argv.index("--") + 1:])
scene = bpy.context.scene
assert scene.get("sample_owner") == "frontier-relay-07"
scene.cycles.samples = 16 if args.pass_name == "trial" else 40
scene.render.resolution_percentage = 65 if args.pass_name == "trial" else 100
scene.render.resolution_x, scene.render.resolution_y = camera_tools["SETTINGS"]["resolution_px"]
prefs = bpy.context.preferences.addons["cycles"].preferences
for api in ("OPTIX", "CUDA"):
    try:
        prefs.compute_device_type = api
        prefs.refresh_devices()
    except (TypeError, RuntimeError):
        continue
    if any(d.type == api for d in prefs.devices):
        for d in prefs.devices:
            d.use = d.type == api
        scene.cycles.device = "GPU"
        break

directory = ROOT / ("diagnostics" if args.pass_name == "trial" else "previews")
directory.mkdir(exist_ok=True)
camera = bpy.data.objects["Camera_Reference"]


def render(name, layer_name):
    for layer in scene.view_layers:
        layer.use = layer.name == layer_name
    scene.render.filepath = str(directory / (name + ".png"))
    bpy.ops.render.render(write_still=True)


if args.pass_name == "trial":
    render("01-camera-v04", "Base colours")
    config = dict(camera_tools["SETTINGS"]["camera"])
    config.update(elevation_deg=7.3, target_m=[.43, -.49, 1.69])
    camera_tools["apply_camera"](scene, config)
    render("02-camera-low", "Base colours")
    camera_tools["apply_camera"](scene)
    render("03-camera-selected", "Base colours")
    names = [
        "Continuous dark soffit", "Continuous clipped fascia",
        "Equipment column | dark footing", "Equipment column | flared lower shell",
        "Equipment column | vertical upper shell",
    ]
    records = {}
    for name in names:
        obj = bpy.data.objects[name]
        records[name] = {
            "base_smooth_faces": sum(p.use_smooth for p in obj.data.polygons),
            "bevel_width_m": obj.modifiers["Editable edge bevel"].width,
            "bevel_segments": obj.modifiers["Editable edge bevel"].segments,
        }
        obj.modifiers["Weighted normals"].show_render = False
    render("04-camera-selected-no-weighted-normals", "Base colours")
    for name in names:
        obj = bpy.data.objects[name]
        obj.modifiers["Weighted normals"].show_render = True
        obj.modifiers["Editable edge bevel"].segments = 1
        obj.modifiers["Editable edge bevel"].width = .004
    render("05-camera-selected-hard-edges", "Base colours")
    (directory / "baseline-mesh.json").write_text(json.dumps(records, indent=2), encoding="utf-8")
else:
    if args.pass_name == "before":
        camera_tools["apply_camera"](scene)
    render(args.pass_name + "-grey", "Neutral grey")
    render(args.pass_name + "-colour", "Base colours")
    report = {
        "source": bpy.data.filepath, "objects": len(scene.objects),
        "resolution": [scene.render.resolution_x, scene.render.resolution_y],
        "camera_world_matrix": [list(row) for row in camera.matrix_world],
        "lens_mm": camera.data.lens, "sensor_mm": camera.data.sensor_width,
        "lights": {o.name: [o.data.energy, [list(row) for row in o.matrix_world]]
                   for o in scene.objects if o.type == "LIGHT"},
        "world": list(scene.world.node_tree.nodes["Background"].inputs[0].default_value),
        "world_strength": scene.world.node_tree.nodes["Background"].inputs[1].default_value,
        "exposure": scene.view_settings.exposure,
    }
    (directory / (args.pass_name + ".json")).write_text(json.dumps(report, indent=2), encoding="utf-8")
