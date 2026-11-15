"""Check the saved baseline, scope, textures, imported render settings and evidence."""
import hashlib
import json
from pathlib import Path
import struct

ROOT = Path(__file__).resolve().parent
SAMPLE = ROOT.parent
REPORTS = ROOT / "reports"
V08_HASH = "6331413c45c2551777b704a9311c5675c07d8f3e9db48b200d42fb0dc2d6d4c2"
V08_BLEND_HASH = "affb505f1f3df2b721fb06ba721447d4deff09608163bb0f3893954fe09bbb77"
V08_COPY = SAMPLE / "godot-review/project/assets/frontier-relay-07-v08.glb"
VERSIONS = {
    "v08": {
        "blend": SAMPLE / "source/frontier-relay-07-materials-v08.blend",
        "glb": SAMPLE / "material-review/export-check/frontier-relay-07-v08.glb",
    },
    "v09": {
        "blend": SAMPLE / "source/frontier-relay-07-seams-v09.blend",
        "glb": ROOT / "exports/frontier-relay-07-v09.glb",
        "godot_asset": SAMPLE / "godot-review/project/assets/frontier-relay-07-v09.glb",
    },
}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def signatures(path):
    content = path.read_bytes()
    size = struct.unpack_from("<I", content, 12)[0]
    gltf = json.loads(content[20:20+size])
    data = content[28+size:]

    def view_bytes(index):
        info = gltf["bufferViews"][index]
        start = info.get("byteOffset", 0)
        return data[start:start+info["byteLength"]]

    def accessor(index, semantic=""):
        info = gltf["accessors"][index]
        raw = view_bytes(info["bufferView"])
        payload = sha(raw)
        if semantic == "TEXCOORD_0":
            assert info["componentType"] == 5126
            payload = [value for value, in struct.iter_unpack("<f", raw)]
        return ({k: v for k, v in info.items() if k != "bufferView"}, payload)

    mats = {}
    images = set()
    for mat in gltf["materials"]:
        pbr = mat["pbrMetallicRoughness"]
        if "baseColorTexture" in pbr:
            tex = pbr["baseColorTexture"]
            texture = gltf["textures"][tex.pop("index")]
            picture = gltf["images"][texture["source"]]
            digest = sha(view_bytes(picture["bufferView"]))
            images.add(digest)
            tex["data_hash"] = digest
            tex["sampler"] = gltf.get("samplers", [{}])[texture.get("sampler",0)]
        mats[mat["name"]] = mat
    names = [mat["name"] for mat in gltf["materials"]]
    meshes = {}
    for node in gltf["nodes"]:
        if "mesh" not in node:
            continue
        mesh = gltf["meshes"][node["mesh"]]
        meshes[node["name"]] = [
            {key: node.get(key) for key in ("translation", "rotation", "scale", "matrix")},
            [(names[p["material"]], accessor(p["indices"]),
              {name: accessor(idx, name) for name, idx in p["attributes"].items()})
             for p in mesh["primitives"]]
        ]
    return mats, images, meshes


assert sha(VERSIONS["v08"]["blend"].read_bytes()) == V08_BLEND_HASH
assert sha(VERSIONS["v08"]["glb"].read_bytes()) == sha(V08_COPY.read_bytes()) == V08_HASH
assert sha(VERSIONS["v09"]["glb"].read_bytes()) == sha(VERSIONS["v09"]["godot_asset"].read_bytes())
m0, i0, g0 = signatures(VERSIONS["v08"]["glb"])
m1, i1, g1 = signatures(VERSIONS["v09"]["glb"])
assert m0 == m1 and i0 == i1 and len(i1) == 4
uv_deltas = {}
changed = []
for name in sorted(g0.keys() & g1.keys()):
    left, right = g0[name], g1[name]
    if left == right:
        continue
    if left[0] != right[0] or len(left[1]) != len(right[1]):
        changed.append(name)
        continue
    for a,b in zip(left[1],right[1]):
        a0,b0 = [v[:2] for v in (a,b)]
        without_uv = lambda p: {k:v for k,v in p[2].items() if k != "TEXCOORD_0"}
        if a0 != b0 or without_uv(a) != without_uv(b):
            changed.append(name)
            break
        au,bu = [p[2].get("TEXCOORD_0") for p in (a,b)]
        if au == bu:
            continue
        if au is None or bu is None or au[0] != bu[0] or len(au[1]) != len(bu[1]):
            changed.append(name)
            break
        largest = max(abs(x-y) for x,y in zip(au[1],bu[1]))
        if largest > 1e-6:
            changed.append(name)
            break
        uv_deltas[name] = largest
assert set(changed) == {"Entry cutout | return", "Horizontal aperture | return",
                        "Side service aperture | return", "Back enclosed wall"}, changed
assert set(g0) - set(g1) == {"Rear central panel joint"}
assert not set(g1) - set(g0)

before, after = [json.loads((REPORTS / f"seams-{tag}.json").read_text())
                 for tag in ("before", "after")]
assert before["asset_resource"].endswith("-v08.glb")
assert after["asset_resource"].endswith("-v09.glb")
keys = ["resolution","fixed_fov_y","fixed_camera","near_views","sun_transform",
        "renderer","driver","device","tonemap","exposure_multiplier",
        "key_energy","ambient_energy","shadow_bias","shadow_normal_bias",
        "angular_shadow_distance_deg","shadow_blur","shadow_distance_m","msaa","taa",
        "anisotropy_project_level"]
assert all(before[k] == after[k] for k in keys)
assert all(stage["passed"] and len(stage["collisions"]) == 10 for stage in (before, after))
assert before["asset"]["materials"] == after["asset"]["materials"]
assert before["asset"]["textures"] == after["asset"]["textures"]
unrelated_front_objects = {
    "door": {"Access panel housing","Equipment column | flared lower shell","Equipment column | dark footing"},
    "window": set(),
    "service": {"Cargo case lid","Cargo corner guard 1.1.2","Cargo corner guard 1.2.2"},
}
leak_probes = {}
for tag in ("before","after"):
    data = json.loads((REPORTS / f"mesh-rays-{tag}.json").read_text())
    leak_probes[tag] = {}
    for part, excluded in unrelated_front_objects.items():
        assert min(data[part]["reveal_normal_checks"]) > 0
        leak_probes[tag][part] = sum(
            count for hits in data[part]["unintended_hits_by_angle"].values()
            for name,count in hits.items() if name not in excluded
        )
assert all(n == 0 for n in leak_probes["after"].values())
movie = json.loads((REPORTS / "video-file.json").read_text())
assert float(movie["format"]["duration"]) == 7 and movie["streams"][0]["nb_frames"] == "168"
record = {
    "id": "frontier-relay-07", "revision": "v09", "status": "awaiting seam visual approval",
    "baseline": VERSIONS["v08"]["glb"].name,
    "files": {v: {k: {"path_relative_to_sample": p.relative_to(SAMPLE).as_posix(),
                       "sha256": sha(p.read_bytes())} for k,p in files.items()}
              for v,files in VERSIONS.items()},
    "changed_meshes": changed,
    "removed_meshes": sorted(set(g0) - set(g1)),
    "other_meshes_position_index_and_normal_bytes_equal": len(g1) - len(changed),
    "non_edit_uv_export_rounding_max": uv_deltas,
    "materials_identical": len(m1), "basecolor_textures_identical": len(i1),
    "godot_meshes": [before["asset"]["mesh_instances"],after["asset"]["mesh_instances"]],
    "lod0_triangles": [before["asset"]["triangle_count_lod0"],after["asset"]["triangle_count_lod0"]],
    "same_godot_settings": keys,
    "aperture_rays_hitting_unintended_surfaces_excluding_foreground_occluders": leak_probes,
    "asset_comparison": "96 meshes in v08 / 95 in v09; all existing material factors and image bytes match",
    "previews": "../previews/00-matched-before-after.jpg",
    "case_probes": ["mesh-rays-before.json","mesh-rays-after.json","seams-before.json","seams-after.json"],
}
(REPORTS / "asset-v09.json").write_text(json.dumps(record,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
print(json.dumps({k:record[k] for k in ("changed_meshes","non_edit_uv_export_rounding_max","lod0_triangles")}))
