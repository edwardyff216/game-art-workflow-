"""Bake low-frequency surface fields to portable sRGB color and linear ORM PNGs."""

import argparse
import json
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent
SETTINGS = json.loads((ROOT / "finish.json").read_text(encoding="utf-8"))


def periodic_field(u, v, count, generator):
    grid = generator.uniform(-1.0, 1.0, (count, count))
    x, y = (u % 1.0) * count, (v % 1.0) * count
    ix, iy = x.astype(int), y.astype(int)
    sx, sy = x - ix, y - iy
    sx, sy = sx * sx * (3 - 2 * sx), sy * sy * (3 - 2 * sy)
    jx, jy = (ix + 1) % count, (iy + 1) % count
    bottom = grid[iy, ix] * (1 - sx) + grid[iy, jx] * sx
    top = grid[jy, ix] * (1 - sx) + grid[jy, jx] * sx
    return bottom * (1 - sy) + top * sy


def field(size, bounds, repeat_m, seed, scales):
    left, right, bottom, top = bounds
    line = (np.arange(size) + .5) / size
    u, v = np.meshgrid(left + line * (right - left), top - line * (top - bottom), sparse=True)
    rng = np.random.default_rng(seed)
    return np.clip(sum(weight * periodic_field(u / repeat_m, v / repeat_m, count, rng)
                       for count, weight in scales), -1.0, 1.0)


def save_rgb(folder, name, values):
    Image.fromarray(np.rint(np.clip(values, 0, 255)).astype(np.uint8)).save(folder / f"{name}.png")


def save_orm(folder, name, roughness):
    # glTF uses G for linear roughness and B for metallic. R is neutral (unused AO).
    save_rgb(folder, name, np.stack((np.full_like(roughness, 255),
                                    255 * roughness, np.zeros_like(roughness)), axis=-1))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("output", type=Path)
    output = parser.parse_args().output
    output.mkdir(parents=True, exist_ok=True)
    concrete = SETTINGS["concrete"]
    seed = concrete["seed"]
    size = 1024
    period = concrete["tile_m"]
    variants = {"concrete": (0, period, 0, period), "stairs": SETTINGS["stairs_uv_bounds"]}
    stairs_source = ROOT.parent / "material-review/textures/finish/stairs-basecolor.png"
    with Image.open(stairs_source) as image:
        stripes = np.asarray(image.convert("RGB"))[size // 2]
    marked = (stripes.max(axis=1).astype(int) - stripes.min(axis=1)) > 15
    for name, bounds in variants.items():
        broad = field(size, bounds, period, seed, ((7, .48), (19, .39), (41, .16)))
        rough = field(size, bounds, period, seed + 19, ((8, .70), (24, .40)))
        color = np.array(concrete["swatch_rgb"])[None, None, :] + broad[:, :, None] * concrete["color_max_delta_u8"]
        roughness = concrete["roughness"] + rough * concrete["roughness_max_delta"]
        if name == "stairs":
            color[:, marked, :] = stripes[marked]
            roughness[:, marked] = concrete["roughness"]
        save_rgb(output, name + "-basecolor", color)
        save_orm(output, name + "-orm", roughness)

    coating = SETTINGS["coating"]
    period = coating["tile_m"]
    surfaces = {
        "enamel-white": ((0, period, 0, period), coating["white_roughness"]),
        "enamel-lime": ((0, period, 0, period), coating["lime_roughness"]),
        "marked-side": ((-2.36, 1.51, .40, 3.08), coating["white_roughness"]),
        "marked-roof": ((-3, 3.70, -.22, 1), coating["white_roughness"]),
        "marked-column": ((-1.77, -.71, 1.50, 3.02), coating["lime_roughness"]),
    }
    for name, (bounds, mean) in surfaces.items():
        variation = field(512, bounds, period, seed + 53, ((4, .69), (11, .43)))
        save_orm(output, name + "-orm", mean + coating["roughness_max_delta"] * variation)


if __name__ == "__main__":
    main()
