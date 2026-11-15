"""Export only the verified v09 meshes, with the same settings as v08."""
from pathlib import Path

import bpy

root = Path(__file__).resolve().parent
scene = bpy.context.scene
assert scene.get("seam_revision") == "v09 / geometry joinery only"
target = root / "exports"
target.mkdir(exist_ok=True)
for obj in bpy.context.view_layer.objects:
    obj.select_set(obj.type == "MESH" and all(c.name != "90_Review" for c in obj.users_collection))
bpy.ops.export_scene.gltf(
    filepath=str(target/"frontier-relay-07-v09.glb"), export_format="GLB",
    use_selection=True, export_apply=True, export_yup=True, export_image_format="AUTO",
    export_materials="EXPORT", export_normals=True, export_texcoords=True,
    export_animations=False, export_cameras=False, export_lights=False,
)
