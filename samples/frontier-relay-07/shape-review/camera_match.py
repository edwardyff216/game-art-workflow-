"""Apply the sample's shared front-right review camera."""
import json
from math import cos, radians, sin
from pathlib import Path

import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parent
SETTINGS = json.loads((ROOT / "shape-settings.json").read_text(encoding="utf-8"))


def apply_camera(scene, config=None):
    config = SETTINGS["camera"] if config is None else config
    camera = bpy.data.objects["Camera_Reference"]
    target = Vector(config["target_m"])
    az, el = radians(config["azimuth_deg"]), radians(config["elevation_deg"])
    ray = Vector((sin(az) * cos(el), -cos(az) * cos(el), sin(el)))
    camera.location = target + ray * config["distance_m"]
    camera.rotation_euler = (-ray).to_track_quat("-Z", "Y").to_euler()
    camera.data.type = "PERSP"
    camera.data.sensor_fit = "HORIZONTAL"
    camera.data.lens = config["lens_mm"]
    camera.data.sensor_width = config["sensor_width_mm"]
    camera.data.dof.use_dof = False
    scene.camera = camera
    return camera
