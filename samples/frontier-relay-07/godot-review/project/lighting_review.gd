extends SceneTree

const REVIEW := preload("res://review.tscn")
const SEAMS := preload("res://seam_capture.gd")
const SKY_SHADER := "res://lighting_review_sky.gdshader"
const OUTPUT := "res://../../lighting-review/"
const VARIANTS := ["A", "B", "C", "C-AO"]
const StudioC = preload("res://studio_c.gd")
const OBLIQUE_EYE := Vector3(10.2, 3.1, -7.6)
const OBLIQUE_TARGET := Vector3(.15, 1.43, .10)

var review: Control


func _initialize() -> void:
	call_deferred("_run")


func _run() -> void:
	var args := OS.get_cmdline_user_args()
	var variants := VARIANTS if args.is_empty() else [args[0]]
	if not VARIANTS.has(variants[0]):
		push_error("Lighting preset must be A, B, C or C-AO.")
		quit(2)
		return
	review = REVIEW.instantiate()
	root.add_child(review)

	var initial_asset := review.inspect_asset() as Dictionary
	var initial_glb := review.asset_scene.resource_path as String
	for variant: String in variants:
		apply_variant(variant)
		var folder := OUTPUT + "previews/" + variant + "/"
		review.select_comparison()
		var matched := camera_snapshot(review.fixed_camera)
		await capture(folder + "matched.png", 16)

		set_inspection(OBLIQUE_EYE, OBLIQUE_TARGET, 33.5)
		var oblique := camera_snapshot(review.inspection)
		await capture(folder + "oblique.png")

		if variant in ["A", "C"]:
			for spec: Array in SEAMS.VIEWS:
				var focus: Vector3 = spec[1]
				set_inspection(focus + spec[2], focus, spec[3])
				await capture(folder + spec[0] + ".png")

		var report := settings_snapshot(review)
		report.merge({
			"variant": variant, "asset": initial_glb, "asset_metadata_unchanged":
				review.asset_scene.resource_path == initial_glb and review.inspect_asset() == initial_asset,
			"matched_camera": matched, "oblique_camera": oblique,
		})
		if not report.asset_metadata_unchanged:
			review.faults.append("Imported asset metadata changed.")
		write_report(OUTPUT + "reports/" + variant + ".json", report)

	for fault: String in review.faults:
		push_error(fault)
	print("LIGHTING_CAPTURE ", variants, " faults=", review.faults.size())
	quit(0 if review.faults.is_empty() else 1)


func apply_variant(variant: String) -> void:
	if variant == "A":
		return
	if variant in ["C", "C-AO"]:
		StudioC.apply(review)
	else:
		StudioC.set_direct_and_ambient(review)
	if variant == "C-AO":
		var env := review.environment as Environment
		env.ssao_radius = .55
		env.ssao_intensity = .8
		env.ssao_power = 1.2
		env.ssao_light_affect = 0.0
		env.ssao_enabled = true


func set_inspection(eye: Vector3, target: Vector3, fov: float) -> void:
	review.inspection.fov = fov
	review.inspection.look_at_from_position(eye, target)
	review.inspection.make_current()


func capture(path: String, warmup_frames := 5) -> void:
	for frame in warmup_frames:
		await RenderingServer.frame_post_draw
	await review.capture(path)


static func camera_snapshot(camera: Camera3D) -> Dictionary:
	return {
		"position": str(camera.global_position), "forward": str(-camera.global_transform.basis.z),
		"vertical_fov_deg": camera.fov, "clip_m": [camera.near, camera.far],
		"camera_attributes": camera.attributes != null,
	}


static func settings_snapshot(review: Control) -> Dictionary:
	var env := review.environment as Environment
	var key := review.key as DirectionalLight3D
	var shot := review.shot as SubViewport
	return {
		"engine": Engine.get_version_info().string,
		"renderer": RenderingServer.get_current_rendering_method(),
		"driver": RenderingServer.get_current_rendering_driver_name(),
		"adapter": RenderingServer.get_video_adapter_name(),
		"adapter_api": RenderingServer.get_video_adapter_api_version(),
		"resolution": [shot.size.x, shot.size.y], "msaa_3d_enum": shot.msaa_3d, "taa": shot.use_taa,
		"shadow_map_px": ProjectSettings.get_setting("rendering/lights_and_shadows/directional_shadow/size"),
		"shadow_filter_quality_enum": ProjectSettings.get_setting("rendering/lights_and_shadows/directional_shadow/soft_shadow_filter_quality"),
		"key": {
			"source_vector": str(key.global_position), "light_ray": str(-key.global_transform.basis.z),
			"color": key.light_color.to_html(false), "energy": key.light_energy,
			"sky_mode": key.sky_mode, "shadow": key.shadow_enabled,
			"shadow_blur": key.shadow_blur, "shadow_bias": key.shadow_bias,
			"normal_bias": key.shadow_normal_bias, "angular_distance_deg": key.light_angular_distance,
			"max_distance_m": key.directional_shadow_max_distance, "split_blend": key.directional_shadow_blend_splits,
		},
		"environment": {
			"background_mode_enum": env.background_mode, "background": env.background_color.to_html(false),
			"floor_color": review.floor_material.albedo_color.to_html(false),
			"floor_roughness": review.floor_material.roughness,
			"ambient_source_enum": env.ambient_light_source, "ambient_energy": env.ambient_light_energy,
			"ambient_color": env.ambient_light_color.to_html(false),
			"ambient_sky_contribution_property": env.ambient_light_sky_contribution,
			"reflection_source_enum": env.reflected_light_source,
			"reflection_probes": review.shot.find_children("*", "ReflectionProbe", true, false).size(),
			"sky": SKY_SHADER if env.sky != null else "",
			"radiance_resolution_px": 128 if env.sky != null else 0,
			"tonemap_enum": env.tonemap_mode, "exposure": env.tonemap_exposure,
			"world_camera_attributes": review.shot.find_children("*", "WorldEnvironment", true, false)[0].camera_attributes != null,
			"ssr": env.ssr_enabled, "ssil": env.ssil_enabled, "sdfgi": env.sdfgi_enabled,
			"ssao": env.ssao_enabled, "ssao_radius_m": env.ssao_radius, "ssao_intensity": env.ssao_intensity,
			"ssao_power": env.ssao_power, "ssao_detail": env.ssao_detail, "ssao_horizon": env.ssao_horizon,
			"ssao_sharpness": env.ssao_sharpness, "ssao_light_affect": env.ssao_light_affect,
			"ssao_ao_channel_affect": env.ssao_ao_channel_affect,
			"glow": env.glow_enabled, "fog": env.fog_enabled, "volumetric_fog": env.volumetric_fog_enabled,
			"adjustments": env.adjustment_enabled,
		},
	}


func write_report(path: String, record: Dictionary) -> void:
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(path.get_base_dir()))
	var file := FileAccess.open(path, FileAccess.WRITE)
	if file == null:
		review.faults.append("Failed to write lighting report: " + path)
		return
	file.store_string(JSON.stringify(record, "\t", true, true) + "\n")
