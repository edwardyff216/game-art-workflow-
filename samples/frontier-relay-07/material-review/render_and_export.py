"""Read the three saved scenes, render the locked view, and export the final asset."""
import argparse
import json
import sys
from pathlib import Path

import bpy
from mathutils.bvhtree import BVHTree

ROOT = Path(__file__).resolve().parent
parser = argparse.ArgumentParser()
parser.add_argument("--export", action="store_true")
args = parser.parse_args(sys.argv[sys.argv.index("--")+1:] if "--" in sys.argv else [])
out = ROOT / "previews"
out.mkdir(exist_ok=True)
report = {}
for version, stem in (
    ("shape-v06","01-v06"),("markings-v07","02-markings"),("materials-v08","03-materials")
):
    source = ROOT.parent / "source" / f"frontier-relay-07-{version}.blend"
    bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False)
    scene = bpy.context.scene
    assert scene["shape_revision"] == "shape-v06"
    scene.cycles.samples = 48
    prefs = bpy.context.preferences.addons["cycles"].preferences
    for api in ("OPTIX", "CUDA"):
        try:
            prefs.compute_device_type = api
            prefs.refresh_devices()
        except (TypeError, RuntimeError):
            continue
        if any(d.type == api for d in prefs.devices):
            for device in prefs.devices:
                device.use = device.type == api
            scene.cycles.device = "GPU"
            break
    scene.render.filepath = str(out / (stem+".png"))
    bpy.ops.render.render(write_still=True)
    bg = scene.world.node_tree.nodes.get("Background")
    report[version] = {
        "file": str(source),
        "camera": [list(row) for row in scene.camera.matrix_world],
        "lens": scene.camera.data.lens,
        "resolution": [scene.render.resolution_x,scene.render.resolution_y,scene.render.resolution_percentage],
        "lights": {o.name: [o.data.energy, [list(row) for row in o.matrix_world]]
                   for o in scene.objects if o.type=="LIGHT"},
        "ambient": [list(bg.inputs[0].default_value),bg.inputs[1].default_value],
        "exposure": scene.view_settings.exposure, "transform": scene.view_settings.view_transform,
    }

settings = ("camera","lens","resolution","lights","ambient","exposure","transform")
assert all(report["shape-v06"][key] == report[rev][key]
           for key in settings for rev in ("markings-v07","materials-v08"))

depsgraph = bpy.context.evaluated_depsgraph_get()
def tree(name):
    obj = bpy.data.objects[name].evaluated_get(depsgraph)
    mesh = obj.to_mesh()
    result = BVHTree.FromPolygons([obj.matrix_world @ v.co for v in mesh.vertices],
                                  [tuple(p.vertices) for p in mesh.polygons])
    obj.to_mesh_clear()
    return result

hits = {}
for carrier, panels in (("Left carrier",("Left bay","Entry bay")),
                        ("Corner carrier",("Entry bay","Corner bay"))):
    carrier_tree = tree("Soffit support | "+carrier)
    hits[carrier] = {p:len(carrier_tree.overlap(tree("Soffit panel | "+p))) for p in panels}

scene.render.use_border = scene.render.use_crop_to_border = True
scene.render.border_min_x, scene.render.border_max_x = .37,.74
scene.render.border_min_y, scene.render.border_max_y = .664,.780
scene.render.resolution_percentage = 170
scene.render.filepath = str(ROOT / "diagnostics" / "v08-eave.png")
bpy.ops.render.render(write_still=True)
if args.export:
    export_path = ROOT / "export-check"
    export_path.mkdir(exist_ok=True)
    for obj in bpy.context.view_layer.objects:
        obj.select_set(obj.type=="MESH" and all(c.name!="90_Review" for c in obj.users_collection))
    bpy.ops.export_scene.gltf(
        filepath=str(export_path/"frontier-relay-07-v08.glb"), export_format="GLB",
        use_selection=True, export_apply=True, export_yup=True, export_image_format="AUTO",
        export_materials="EXPORT", export_normals=True, export_texcoords=True,
        export_animations=False, export_cameras=False, export_lights=False,
    )
(ROOT/"render-verification.json").write_text(
    json.dumps({"matched":settings,"after_carrier_panel_triangle_hits":hits,"stages":report},indent=2),
    encoding="utf-8"
)
