extends SceneTree

const BASELINE := preload("res://review.tscn")
const StudioC = preload("res://studio_c.gd")
const PhysicsReview = preload("res://review_physics.gd")
const Seams = preload("res://seam_capture.gd")
const LightingReview = preload("res://lighting_review.gd")
const VIEWS := [
	["near-stairs", Vector3(2.25, 1.74, 5.50), Vector3(.53, .50, 2.83), 44.0],
	["near-crate", Vector3(4.95, 1.85, .20), Vector3(2.62, .78, -1.48), 42.0],
	["mid-oblique", LightingReview.OBLIQUE_EYE, LightingReview.OBLIQUE_TARGET, 33.5],
	["front", Vector3(.43, 2.82, 10.2), Vector3(.43, 1.56, .25), 38.0],
	["side", Vector3(11.2, 3.15, .25), Vector3(.43, 1.56, .25), 38.0],
	["rear", Vector3(.43, 3.20, -10.5), Vector3(.43, 1.56, .25), 38.0],
	["far", Vector3(14.6, 6.2, 17.5), Vector3(.43, 1.56, .25), 40.0],
]

var output: String
var review: Control


func _initialize() -> void:
	call_deferred("_run")


func _run() -> void:
	var args := OS.get_cmdline_user_args()
	if args.size() != 1 or not args[0].is_absolute_path():
		push_error("Pass one absolute evidence directory after --.")
		quit(2)
		return
	output = args[0]
	var final_path: String = ProjectSettings.get_setting("application/run/main_scene")
	var images_before := await capture_version(BASELINE, "v09")
	var images_after := await capture_version(load(final_path), "v10")
	var report := {
		"baseline": images_before, "final": images_after,
		"same_studio_and_cameras": images_before.studio == images_after.studio and images_before.cameras == images_after.cameras,
		"default_scene": final_path, "orbit_frames": 144, "orbit_fps": 24,
		"driver": RenderingServer.get_current_rendering_driver_name(),
		"gpu": RenderingServer.get_video_adapter_name(),
		"engine": Engine.get_version_info().string,

		"player_traversal": "not tested", "performance": "not tested",
	}
	var valid: bool = report.same_studio_and_cameras
	valid = valid and images_before.faults.is_empty() and images_after.faults.is_empty()
	valid = valid and images_before.roughness_maps.is_empty() and images_after.roughness_maps.size() == 7
	valid = valid and images_after.asset_path.ends_with("-v10.glb")
	var file := FileAccess.open(output.path_join("engine-checks.json"), FileAccess.WRITE)
	if file == null:
		push_error("Could not write engine-checks.json")
		quit(1)
		return
	file.store_string(JSON.stringify(report, "\t", true, true) + "\n")
	print("FR07_FINAL passed=", valid, " faults=", images_before.faults, images_after.faults)
	quit(0 if valid else 1)


func capture_version(scene: PackedScene, label: String) -> Dictionary:
	review = scene.instantiate()
	root.add_child(review)
	if label == "v09":
		StudioC.apply(review)
	await physics_frame
	await physics_frame
	var collision := PhysicsReview.test(review.shot.find_world_3d().direct_space_state)
	for hit: Dictionary in collision:
		if not hit.passed:
			review.faults.append("Static collision: " + hit.test)

	var studio := LightingReview.settings_snapshot(review)
	var directory := output.path_join("previews").path_join(label)
	var cameras := {}
	review.select_comparison()
	cameras["matched"] = LightingReview.camera_snapshot(review.fixed_camera)
	await still(directory.path_join("matched.png"), 16)
	for view: Array in VIEWS:
		var eye: Vector3 = view[1]
		var target: Vector3 = view[2]
		set_inspection(eye, target, view[3])
		var camera := LightingReview.camera_snapshot(review.inspection)
		camera["target"] = str(target)
		camera["distance_to_target_m"] = eye.distance_to(target)
		cameras[view[0]] = camera
		await still(directory.path_join("%s.png" % view[0]))
	for view: Array in Seams.VIEWS:
		var focus: Vector3 = view[1]
		set_inspection(focus + view[2], focus, view[3])
		await still(directory.path_join("%s.png" % view[0]))
	if label == "v10":
		await capture_orbit()

	var record := {
		"asset_path": review.asset_scene.resource_path, "asset": review.inspect_asset(),
		"cameras": cameras, "studio": studio,
		"collision_bodies": review.collision_count, "collision": collision,
		"projection": review.verify_projection(), "roughness_maps": inspect_maps(),
		"faults": Array(review.faults),
	}
	review.queue_free()
	await process_frame
	return record


func set_inspection(eye: Vector3, target: Vector3, fov: float) -> void:
	review.inspection.fov = fov
	review.inspection.look_at_from_position(eye, target)
	review.inspection.make_current()


func still(path: String, frames := 4) -> void:
	for frame in frames:
		await RenderingServer.frame_post_draw
	await review.capture(path)


func capture_orbit() -> void:
	var directory := output.path_join("frames")
	var target := Vector3(.43, 1.56, .25)
	for frame in range(144):
		var time := frame / 143.0
		var azimuth := deg_to_rad(20.0 + 360.0 * time)
		var elevation := deg_to_rad(11.0 + 12.0 * sin(PI * time))
		var distance := 9.2 + 12.0 * pow(sin(PI * time), 4.0)
		var ray := Vector3(sin(azimuth) * cos(elevation), sin(elevation), cos(azimuth) * cos(elevation))
		set_inspection(target + ray * distance, target, 40.0)
		await review.capture(directory.path_join("frame-%04d.jpg" % frame), true)


func inspect_maps() -> Dictionary:
	var maps := {}
	for node in review.model.find_children("*", "MeshInstance3D", true, false):
		var mesh := node as MeshInstance3D
		for index in mesh.mesh.get_surface_count():
			var material := mesh.get_active_material(index) as StandardMaterial3D
			var texture := material.roughness_texture
			if texture == null:
				continue
			var array := mesh.mesh.surface_get_arrays(index)
			if array[Mesh.ARRAY_TEX_UV] == null or array[Mesh.ARRAY_TEX_UV].size() != array[Mesh.ARRAY_VERTEX].size():
				review.faults.append("Finish map has no matching UV: " + String(mesh.name))
			if maps.has(material.resource_name):
				continue
			var image := texture.get_image()
			if not image.has_mipmaps() or material.texture_filter != BaseMaterial3D.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS_ANISOTROPIC:
				review.faults.append("Finish texture is missing mipmapped anisotropic filtering: " + material.resource_name)
			if material.roughness_texture_channel != BaseMaterial3D.TEXTURE_CHANNEL_GREEN or absf(material.roughness - 1.0) > .001:
				review.faults.append("Unexpected imported roughness channel or factor: " + material.resource_name)
			maps[material.resource_name] = {
				"width": texture.get_width(), "height": texture.get_height(),
				"mipmaps": image.has_mipmaps(), "channel": material.roughness_texture_channel,
				"factor": material.roughness, "texture_filter": material.texture_filter,
			}
	return maps
