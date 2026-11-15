"""Build review sheets and verify that the lighting presets changed only intended inputs."""

import json
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageOps, ImageStat

ROOT = Path(__file__).resolve().parent
PREVIEWS = ROOT / "previews"
REPORTS = ROOT / "reports"
PRESETS = ("A", "B", "C", "C-AO")
VIEWS = ("matched", "oblique")


def snapshot(preset, view):
    with Image.open(PREVIEWS / preset / f"{view}.png") as image:
        return image.convert("RGB")


def tile_sheet(name, rows, tile_size):
    tile_width, tile_height = tile_size
    row_height = 29 + tile_height
    column_count = max(len(row) for row in rows)
    canvas = Image.new("RGB", (column_count * tile_width, len(rows) * row_height), "#24262a")
    draw = ImageDraw.Draw(canvas)
    for row_index, row in enumerate(rows):
        for col_index, (label, image) in enumerate(row):
            x = col_index * tile_width
            y = row_index * row_height
            tile = ImageOps.contain(image, tile_size, Image.Resampling.LANCZOS)
            draw.text((x + 12, y + 6), label, fill="white", font_size=15)
            canvas.paste(tile, (x + (tile_width - tile.width) // 2, y + 29))
    canvas.save(PREVIEWS / name)


def changed_keys(before, after):
    return {key for key in before.keys() | after.keys() if before.get(key) != after.get(key)}


def verify_settings():
    settings = {preset: json.loads((REPORTS / f"{preset}.json").read_text()) for preset in PRESETS}
    baseline = settings["A"]
    for record in settings.values():
        assert record["asset_metadata_unchanged"], record["variant"]
        assert not changed_keys(baseline, record) - {"variant", "key", "environment"}, record["variant"]

    a, b, c, ao = (settings[preset] for preset in PRESETS)
    assert changed_keys(a["key"], b["key"]) == {"energy", "source_vector", "light_ray"}
    assert changed_keys(a["environment"], b["environment"]) == {"ambient_energy"}
    assert b["key"] == c["key"] == ao["key"]
    assert changed_keys(b["environment"], c["environment"]) == {
        "sky", "radiance_resolution_px", "reflection_source_enum",
    }
    assert changed_keys(c["environment"], ao["environment"]) == {
        "ssao", "ssao_radius_m", "ssao_intensity", "ssao_power",
    }


def summarize(debug_shots):
    old_shot = ROOT.parent / "seam-review" / "previews" / "after" / "matched.png"
    baseline_equal = None
    if old_shot.is_file():
        with Image.open(old_shot) as old:
            baseline_equal = ImageChops.difference(
                debug_shots["matched"]["A"], old.convert("RGB")
            ).getbbox() is None
        assert baseline_equal, "Preset A does not match the previous v09 baseline."

    patch_boxes = {
        "matched": {
            "window": (796, 312, 859, 350),
            "white_roof": (479, 124, 579, 151),
            "white_wall": (911, 499, 946, 523),
            "eave_rib": (494, 250, 520, 256),
            "column_slant": (176, 505, 234, 520),
            "column_front": (162, 548, 236, 579),
            "column_side": (291, 543, 306, 565),
            "step_tread": (316, 699, 384, 707),
            "step_riser": (318, 713, 382, 722),
        },
        "oblique": {"window": (481, 319, 583, 348)},
    }
    samples = {}
    ao = {}
    for view, shots in debug_shots.items():
        samples[view] = {}
        for label, box in patch_boxes[view].items():
            means = {}
            for preset, shot in shots.items():
                patch = shot.crop(box)
                means[preset] = {
                    "mean_rgb_u8": [round(channel, 2) for channel in ImageStat.Stat(patch).mean],
                    "white_clipped_pixels": sum(pixel == (255, 255, 255) for pixel in patch.get_flattened_data()),
                }
            samples[view][label] = {"roi_xyxy": box, "samples": means}

        difference = ImageChops.difference(shots["C"], shots["C-AO"]).convert("L")
        histogram = difference.histogram()
        ao[view] = {
            "max_abs_luma_delta_u8": difference.getextrema()[1],
            "pixels_luma_delta_ge_4": sum(histogram[4:]),
            "total_image_pixels": difference.width * difference.height,
        }

    record = {
        "A_matches_previous_v09_pixels": baseline_equal,
        "camera_and_settings_delta_checks": "passed",
        "ssao_screen_delta": ao,
        "screen_samples": samples,
    }
    (REPORTS / "image-checks.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")


def main():
    verify_settings()
    shots = {view: {preset: snapshot(preset, view) for preset in PRESETS} for view in VIEWS}
    summarize(shots)
    for view in VIEWS:
        tile_sheet(
            f"01-abc-{view}.png",
            [[(preset, shots[view][preset]) for preset in PRESETS[:3]]],
            (638, 425),
        )

    window_boxes = {"matched": (667, 242, 977, 408), "oblique": (375, 261, 685, 427)}
    tile_sheet(
        "02-window-reflection.png",
        [[(f"{view} / {preset}", shots[view][preset].crop(window_boxes[view]))
          for preset in PRESETS[:3]] for view in VIEWS],
        (310, 166),
    )
    contact_crops = {
        "matched": (88, 615, 680, 810),
        "oblique": (470, 491, 979, 748),
    }
    tile_sheet(
        "03-contact-ao.png",
        [[(f"{view} / {preset}", shots[view][preset].crop(contact_crops[view]))
          for preset in ("C", "C-AO")] for view in VIEWS],
        (600, 260),
    )
    detail_views = ("door-front", "door-oblique", "window-front", "window-oblique",
                    "service-front", "service-oblique", "back")
    tile_sheet(
        "04-seams-a-c.png",
        [[(f"{view} / {preset}", snapshot(preset, view)) for preset in ("A", "C")]
         for view in detail_views],
        (600, 400),
    )
    print("Captured settings and shared cameras verified. Review sheets written.")


if __name__ == "__main__":
    main()
