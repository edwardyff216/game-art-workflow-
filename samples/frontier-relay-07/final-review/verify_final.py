"""Check the v09-to-v10 export and record evidence from the final Godot run."""

import argparse
from collections import Counter
import hashlib
import io
import json
from pathlib import Path
import struct

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageOps

ROOT = Path(__file__).resolve().parent
SAMPLE = ROOT.parent
PROJECT = SAMPLE / "godot-review/project"
BASE_GLB = SAMPLE / "seam-review/exports/frontier-relay-07-v09.glb"
FINAL_GLB = PROJECT / "assets/frontier-relay-07-v10.glb"
BASE_BLEND = SAMPLE / "source/frontier-relay-07-seams-v09.blend"
FINAL_BLEND = SAMPLE / "source/frontier-relay-07-finish-v10.blend"
BASE_HASH = "4bfa2ae6df8c824e836ebbf31512957cc8a1e2eee8f0ca5c30e9312dcdc2a88a"
BASE_BLEND_HASH = "e39898ea299ed915310d3e68723465f496b80110651958b5aaf9ae7c385c646f"
FINISH = {
    "FR07 | Deck stone grey", "FR07 | Warm white enamel", "FR07 | Fluorescent yellow green",
    "FR07 PBR | Graphics roof", "FR07 PBR | Graphics column", "FR07 PBR | Graphics side",
    "FR07 PBR | Graphics stairs",
}
BASE_COLOR_CHANGED = {"FR07 | Deck stone grey", "FR07 PBR | Graphics stairs"}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class Glb:
    def __init__(self, path):
        raw = path.read_bytes()
        assert raw[:8] == b"glTF\x02\0\0\0", path
        size = struct.unpack_from("<I", raw, 12)[0]
        self.doc = json.loads(raw[20:20 + size])
        self.data = raw[28 + size:]
        self.materials = self.doc["materials"]

    def view(self, index):
        view = self.doc["bufferViews"][index]
        start = view.get("byteOffset", 0)
        return self.data[start:start + view["byteLength"]]

    def read(self, index):
        accessor = self.doc["accessors"][index]
        data = self.view(accessor["bufferView"])[accessor.get("byteOffset", 0):]
        width = {"SCALAR": 1, "VEC2": 2, "VEC3": 3}[accessor["type"]]
        dtype = {5126: "<f4", 5123: "<u2", 5125: "<u4"}[accessor["componentType"]]
        return np.frombuffer(data, dtype=dtype, count=accessor["count"] * width).reshape(-1, width)

    def image(self, texture):
        index = self.doc["textures"][texture["index"]]["source"]
        return self.view(self.doc["images"][index]["bufferView"])

    def material_info(self):
        records = {}
        for material in self.materials:
            item = dict(material)
            pbr = item["pbrMetallicRoughness"] = dict(item["pbrMetallicRoughness"])
            for channel in ("baseColorTexture", "metallicRoughnessTexture"):
                if channel in pbr:
                    data = self.image(pbr[channel])
                    pbr[channel] = hashlib.sha256(data).hexdigest()
            records[material["name"]] = item
        return records

    def geometry(self):
        result = {}
        for node in self.doc["nodes"]:
            if "mesh" not in node:
                continue
            transform = tuple(node.get(key) for key in ("matrix", "translation", "rotation", "scale"))
            primitives = self.doc["meshes"][node["mesh"]]["primitives"]
            surfaces = {}
            for primitive in primitives:
                name = self.materials[primitive["material"]]["name"]
                attrs = primitive["attributes"]
                indices = self.read(primitive["indices"]).reshape(-1, 3)
                attributes = ["POSITION", "NORMAL"]
                if "TEXCOORD_0" in attrs and name.startswith("FR07 PBR | Graphics"):
                    attributes.append("TEXCOORD_0")
                values = np.concatenate([self.read(attrs[key]) for key in attributes], axis=1)
                if name == "FR07 PBR | Graphics stairs":
                    # Reproject stair depth/height while preserving the transverse stripe coordinate.
                    values = values[:, :-1]
                # Corner attributes survive UV-induced vertex splitting. Preserve triangle winding.
                triangles = Counter()
                for triangle in values[indices]:
                    corners = tuple(tuple(round(float(v), 6) for v in corner) for corner in triangle)
                    triangles[min(corners, corners[1:] + corners[:1], corners[2:] + corners[:2])] += 1
                assert name not in surfaces, node["name"]
                surfaces[name] = triangles
            result[node["name"]] = (transform, surfaces)
        return result


def check_export():
    assert sha(BASE_BLEND) == BASE_BLEND_HASH
    assert sha(BASE_GLB) == BASE_HASH == sha(PROJECT / "assets/frontier-relay-07-v09.glb")
    old, new = Glb(BASE_GLB), Glb(FINAL_GLB)
    before, after = old.geometry(), new.geometry()
    assert before.keys() == after.keys()
    assert len(after) == 95
    assert before == after, [name for name in before if before[name] != after[name]]
    old_mats, new_mats = old.material_info(), new.material_info()
    assert old_mats.keys() == new_mats.keys()
    assert {key for key in old_mats if old_mats[key] != new_mats[key]} == FINISH
    for name in FINISH - BASE_COLOR_CHANGED:
        for key in ("baseColorFactor", "baseColorTexture"):
            assert old_mats[name]["pbrMetallicRoughness"].get(key) == new_mats[name]["pbrMetallicRoughness"].get(key), name

    ranges = {}
    for material in new.materials:
        name = material["name"]
        pbr = material["pbrMetallicRoughness"]
        if name not in FINISH:
            continue
        assert pbr["metallicFactor"] == 0 and pbr.get("roughnessFactor", 1) == 1
        with Image.open(io.BytesIO(new.image(pbr["metallicRoughnessTexture"]))) as image:
            pixels = np.asarray(image.convert("RGB"))
            r, g, b = pixels.transpose(2, 0, 1)
            assert r.min() == 255 and b.min() == b.max() and g.max() > g.min(), name
            ranges[name] = {"size": image.size, "roughness_range": [float(g.min()) / 255, float(g.max()) / 255]}
    assert len(new.doc["images"]) == 12
    return {
        "source_sha256": sha(FINAL_BLEND), "glb_sha256": sha(FINAL_GLB),
        "baseline_source_sha256": BASE_BLEND_HASH, "baseline_glb_sha256": BASE_HASH,
        "mesh_nodes_matching_positions_triangle_winding_normals_and_transforms": len(after),
        "existing_marked_uv_unchanged_except_stair_v": True,
        "materials_changed": sorted(FINISH), "packed_images": 12, "roughness_maps": ranges,
    }


def check_rebuild(rebuilt):
    shipped, regenerated = Glb(FINAL_GLB), Glb(rebuilt)
    assert shipped.doc == regenerated.doc, "GLB scene, materials or buffer layout changed."
    for index, accessor in enumerate(shipped.doc["accessors"]):
        expected, actual = shipped.read(index), regenerated.read(index)
        if accessor["componentType"] == 5126:
            np.testing.assert_allclose(actual, expected, rtol=0, atol=1e-6)
        else:
            assert np.array_equal(actual, expected), index
    for image in shipped.doc["images"]:
        assert shipped.view(image["bufferView"]) == regenerated.view(image["bufferView"]), image["name"]
    return {
        "glb_sha256": sha(rebuilt), "byte_identical": sha(rebuilt) == sha(FINAL_GLB),
        "scene_metadata_and_embedded_images_match": True, "float_attribute_abs_tolerance": 1e-6,
    }


def check_engine(engine):
    assert engine["default_scene"] == "res://frontier_relay.tscn"
    assert engine["same_studio_and_cameras"]
    stored_c = json.loads((SAMPLE / "lighting-review/reports/C.json").read_text())
    for run in (engine["baseline"], engine["final"]):
        assert not run["faults"], run["faults"]
        assert len(run["collision"]) == 10 and all(probe["passed"] for probe in run["collision"])
        assert run["asset"]["triangle_count_lod0"] == 10577 and run["asset"]["invalid_normals"] == 0
        assert run["asset"]["material_count"] == 16
        for key, current in run["studio"].items():
            if key not in {"engine", "adapter", "adapter_api"}:
                assert current == stored_c[key], (key, current, stored_c[key])
        assert run["cameras"]["matched"] == stored_c["matched_camera"]
    final = engine["final"]
    assert len(final["asset"]["textures"]) == 5
    assert all(texture["mipmaps"] for texture in final["asset"]["textures"].values())
    assert set(final["roughness_maps"]) == FINISH
    assert all(final["asset"]["materials"][name]["metallic"] == 0 for name in FINISH)
    assert engine["baseline"]["asset"]["materials"]["FR07 | Tinted window block"] == final["asset"]["materials"]["FR07 | Tinted window block"]


def rgb(path):
    with Image.open(path) as image:
        return image.convert("RGB")


def sheet(path, rows, size):
    width, height = size
    result = Image.new("RGB", (width * max(len(row) for row in rows), (height + 27) * len(rows)), "#232528")
    draw = ImageDraw.Draw(result)
    for row, items in enumerate(rows):
        for col, (label, image) in enumerate(items):
            x, y = col * width, row * (height + 27)
            tile = ImageOps.contain(image, size, Image.Resampling.LANCZOS)
            result.paste(tile, (x + (width - tile.width) // 2, y + 27))
            draw.text((x + 12, y + 5), label, fill="white", font_size=15)
    result.save(path, quality=93, subsampling=0, optimize=True)


def make_sheets(output):
    previews = output / "previews"
    def pair(view):
        return [(f"{view} / {version} / Studio C", rgb(previews / version / f"{view}.png"))
                for version in ("v09", "v10")]

    sheet(output / "01-material-comparison.jpg", [pair("matched")], (900, 600))
    sheet(output / "02-near-stairs-crate.jpg", [pair("near-stairs"), pair("near-crate")], (750, 500))
    checks = ["front", "side", "mid-oblique", "rear", "far"]
    rendered = {name: rgb(previews / "v10" / f"{name}.png") for name in checks}
    sheet(output / "03-views.jpg", [[(name, rendered[name]) for name in row]
          for row in (checks[:3], checks[3:])], (610, 406))
    seams = ("door-front", "door-oblique", "window-front", "window-oblique",
             "service-front", "service-oblique", "back")
    sheet(output / "04-seam-comparison.jpg", [pair(view) for view in seams], (570, 380))
    frames = sorted((output / "frames").glob("frame-*.jpg"))
    assert len(frames) == 144
    rows = [[(f"{index / 24:.2f} s", rgb(frames[index])) for index in row]
            for row in (range(0, 72, 12), range(72, 144, 12))]
    sheet(output / "05-orbit-frames.jpg", rows, (400, 266))

    base_png = SAMPLE / "lighting-review/previews/C/matched.png"
    if not base_png.is_file():
        return None
    return ImageChops.difference(rgb(base_png), pair("matched")[0][1]).getbbox() is None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("output", type=Path)
    parser.add_argument("--export-only", action="store_true")
    parser.add_argument("--rebuilt", type=Path)
    args = parser.parse_args()
    report = check_export()
    if args.rebuilt:
        report['rebuild'] = check_rebuild(args.rebuilt)
    if not args.export_only:
        check_engine(json.loads((args.output / "engine-checks.json").read_text()))
        report["v09_matches_original_C_pixels_where_available"] = make_sheets(args.output)
        assert report["v09_matches_original_C_pixels_where_available"] is not False
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / "export-checks.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print("Export verified" + ("" if args.export_only else "; Godot settings, collision and captures verified"))


if __name__ == "__main__":
    main()
