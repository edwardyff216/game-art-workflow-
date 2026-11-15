"""Apply the baked finish to v09 and export a portable, editable v10."""

import argparse
import json
from pathlib import Path
import sys

import bpy

ROOT = Path(__file__).resolve().parent
SETTINGS = json.loads((ROOT / "finish.json").read_text(encoding="utf-8"))
BASELINE = ROOT.parent / "source/frontier-relay-07-seams-v09.blend"
MATERIALS = {
    "FR07 | Deck stone grey": ("concrete", "concrete"),
    "FR07 PBR | Graphics stairs": ("stairs", "stairs"),
    "FR07 | Warm white enamel": ("enamel-white", None),
    "FR07 | Fluorescent yellow green": ("enamel-lime", None),
    "FR07 PBR | Graphics side": ("marked-side", None),
    "FR07 PBR | Graphics roof": ("marked-roof", None),
    "FR07 PBR | Graphics column": ("marked-column", None),
}


def add_image(material, path, color_space, repeat, location):
    image = bpy.data.images.load(str(path))
    image.colorspace_settings.name = color_space
    image.pack()
    image.filepath = "//../final-review/textures/" + path.name
    node = material.node_tree.nodes.new("ShaderNodeTexImage")
    node.image = image
    node.label = path.stem
    node.extension = "REPEAT" if repeat else "EXTEND"
    node.location = location
    return node


def apply_material(name, roughness, basecolor, textures):
    material = bpy.data.materials[name]
    tree = material.node_tree
    shader = next(node for node in tree.nodes if node.type == "BSDF_PRINCIPLED")
    repeat = roughness in {"concrete", "enamel-white", "enamel-lime"}
    image = add_image(material, textures / f"{roughness}-orm.png", "Non-Color", repeat, (-650, -320))
    channels = tree.nodes.new("ShaderNodeSeparateColor")
    channels.location = (-350, -320)
    tree.links.new(image.outputs["Color"], channels.inputs["Color"])
    tree.links.new(channels.outputs["Green"], shader.inputs["Roughness"])
    if basecolor is None:
        return
    old = tree.nodes.get("Graphics base color")
    if old is not None:
        tree.nodes.remove(old)
    image = add_image(material, textures / f"{basecolor}-basecolor.png", "sRGB", repeat, (-650, 240))
    tree.links.new(image.outputs["Color"], shader.inputs["Base Color"])


def surface_uv(obj, name, period):
    mesh = obj.data
    assert not mesh.uv_layers, obj.name
    layer = mesh.uv_layers.new(name=name)
    matrix = obj.matrix_world
    normal_matrix = matrix.to_3x3().inverted_safe().transposed()
    for face in mesh.polygons:
        normal = normal_matrix @ face.normal
        axis = max(range(3), key=lambda index: abs(normal[index]))
        u, v = ((1, 2), (0, 2), (0, 1))[axis]
        for index in face.loop_indices:
            point = matrix @ mesh.vertices[mesh.loops[index].vertex_index].co
            layer.uv[index].vector = (point[u] / period, point[v] / period)


def stair_uv(obj):
    layer = obj.data.uv_layers["Surface graphics"]
    left, right, bottom, top = SETTINGS["stairs_uv_bounds"]
    for loop in obj.data.loops:
        point = obj.matrix_world @ obj.data.vertices[loop.vertex_index].co
        # A tread advances along Y, and a riser advances along Z. The stripe remains fixed in X.
        layer.uv[loop.index].vector = ((point.x - left) / (right - left),
                                      (point.y + point.z - bottom) / (top - bottom))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("textures", type=Path)
    parser.add_argument("blend", type=Path)
    parser.add_argument("glb", type=Path)
    args = parser.parse_args(sys.argv[sys.argv.index("--") + 1:])
    if Path(bpy.data.filepath).resolve() != BASELINE:
        raise ValueError(f"Open the v09 seam baseline {BASELINE} before building.")
    for path in (args.blend, args.glb):
        if path.exists():
            raise FileExistsError(path)
        path.parent.mkdir(parents=True, exist_ok=True)
    bpy.context.view_layer.update()
    for name, (roughness, basecolor) in MATERIALS.items():
        apply_material(name, roughness, basecolor, args.textures)

    projected = {"FR07 | Deck stone grey": SETTINGS["concrete"]["tile_m"],
                 "FR07 | Warm white enamel": SETTINGS["coating"]["tile_m"],
                 "FR07 | Fluorescent yellow green": SETTINGS["coating"]["tile_m"]}
    for obj in bpy.context.view_layer.objects:
        export = obj.type == "MESH" and all(c.name != "90_Review" for c in obj.users_collection)
        obj.select_set(export)
        if not export:
            continue
        names = {slot.material.name for slot in obj.material_slots if slot.material is not None}
        if "FR07 PBR | Graphics stairs" in names:
            stair_uv(obj)
            continue
        applicable = names & projected.keys()
        if applicable:
            surface_uv(obj, "Finish projection", projected[applicable.pop()])

    bpy.context.scene["material_stage"] = "v10 / portable concrete and coating finish"
    bpy.ops.wm.save_as_mainfile(filepath=str(args.blend), compress=True, relative_remap=False)
    bpy.ops.export_scene.gltf(
        filepath=str(args.glb), export_format="GLB", use_selection=True, export_apply=True,
        export_yup=True, export_image_format="AUTO", export_materials="EXPORT",
        export_normals=True, export_texcoords=True, export_animations=False,
        export_cameras=False, export_lights=False,
    )


if __name__ == "__main__":
    main()
