extends Control

const PhysicsReview = preload("res://review_physics.gd")
const SeamCapture = preload("res://seam_capture.gd")
const RENDER_SIZE := Vector2i(1280, 853)
const TARGET := Vector3(0.43, 1.56, 0.25)
const EVIDENCE := "res://../"

@export var asset_scene: PackedScene
var shot: SubViewport
var model: Node3D
var fixed_camera: Camera3D
var inspection: Camera3D
var figure: Node3D
var environment: Environment
var key: DirectionalLight3D
var floor_material: StandardMaterial3D
var hud: Label
var camera_record: Dictionary
var mode := ""
var yaw := 35.4
var pitch := 14.0
var distance := 10.4
var dragging := false
var scale_visible := true
var comparison := true
var collision_count := 0
var faults: Array[String] = []


func _ready() -> void:
	var arguments := OS.get_cmdline_user_args()
	if arguments.has("initial"):
		mode = "initial"
	elif arguments.has("diagnostics"):
		mode = "diagnostics"
	elif arguments.has("stills"):
		mode = "stills"
	elif arguments.has("video"):
		mode = "video"
	elif arguments.has("seams-before"):
		mode = "seams-before"
		asset_scene = load("res://assets/frontier-relay-07-v08.glb") as PackedScene
	elif arguments.has("seams-after"):
		mode = "seams-after"
	shot = SubViewport.new()
	shot.size = RENDER_SIZE
	shot.own_world_3d = true
	shot.msaa_3d = Viewport.MSAA_4X
	shot.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	add_child(shot)
	var display := TextureRect.new()
	display.texture = shot.get_texture()
	display.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	display.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
	display.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(display)
	display.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)

	model = asset_scene.instantiate() as Node3D
	shot.add_child(model)
	var imported_stats := inspect_asset()
	collision_count = PhysicsReview.build(shot, model)
	create_studio()
	if mode in ["", "stills", "video", "seams-before", "seams-after"]:
		use_final_studio()
		use_anisotropic_marks()
		imported_stats = inspect_asset()
	create_cameras()
	create_figure()
	if mode.is_empty():
		create_hud()
	select_comparison()
	if not mode.is_empty():
		await get_tree().process_frame
		await get_tree().physics_frame
		await get_tree().physics_frame
		await run_evidence(imported_stats)


func inspect_asset() -> Dictionary:
	var materials := {}
	var textures := {}
	var mesh_count := 0
	var triangles := 0
	var normals_checked := 0
	var invalid_normals := 0
	var marked_surfaces := 0
	var initial_colliders := 0
	for node in model.find_children("*", "CollisionShape3D", true, false):
		initial_colliders += 1
	for node in model.find_children("*", "MeshInstance3D", true, false):
		var mesh := node as MeshInstance3D
		mesh_count += 1
		for index in mesh.mesh.get_surface_count():
			if mesh.mesh.surface_get_primitive_type(index) != Mesh.PRIMITIVE_TRIANGLES:
				faults.append("Unexpected primitive: " + String(mesh.name))
				continue
			var arrays: Array = mesh.mesh.surface_get_arrays(index)
			var vertices: PackedVector3Array = arrays[Mesh.ARRAY_VERTEX]
			var indices: Variant = arrays[Mesh.ARRAY_INDEX]
			triangles += int((indices.size() if indices != null else vertices.size()) / 3.0)
			var normals: Variant = arrays[Mesh.ARRAY_NORMAL]
			if normals == null or normals.size() != vertices.size():
				faults.append("Missing normals on " + String(mesh.name))
			else:
				for normal: Vector3 in normals:
					normals_checked += 1
					if not normal.is_finite() or absf(normal.length() - 1.0) > .025:
						invalid_normals += 1
			var material := mesh.get_active_material(index) as StandardMaterial3D
			if material == null:
				faults.append("Missing PBR material on " + String(mesh.name))
				continue
			var id := material.resource_name
			materials[id] = {"roughness": material.roughness, "metallic": material.metallic,
				"emission": material.emission_enabled, "energy": material.emission_energy_multiplier,
				"cull_mode": material.cull_mode, "filter": material.texture_filter}
			if material.albedo_texture != null:
				var tex := material.albedo_texture
				var uv: Variant = arrays[Mesh.ARRAY_TEX_UV]
				marked_surfaces += 1
				if uv == null or uv.size() != vertices.size():
					faults.append("Missing UV0 on " + String(mesh.name))
				textures[id] = {"width": tex.get_width(), "height": tex.get_height(),
					"mipmaps": tex.get_image().has_mipmaps()}
	var expected_meshes := 96 if asset_scene.resource_path.ends_with("-v08.glb") else 95
	if mesh_count != expected_meshes or materials.size() != 16 or textures.size() != expected_base_color_maps() or invalid_normals > 0:
		faults.append("Import counts or normals differ from expectation.")
	return {"mesh_instances": mesh_count, "triangle_count_lod0": triangles,
		"material_count": materials.size(), "materials": materials, "textures": textures,
		"textured_surfaces": marked_surfaces, "normals_checked": normals_checked,
		"invalid_normals": invalid_normals, "imported_collision_shapes": initial_colliders}


func expected_base_color_maps() -> int:
	return 4


func create_studio() -> void:
	environment = Environment.new()
	environment.background_mode = Environment.BG_COLOR
	environment.background_color = Color("#848487")
	environment.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	environment.ambient_light_color = Color.WHITE
	environment.ambient_light_energy = .48
	environment.tonemap_mode = Environment.TONE_MAPPER_LINEAR
	environment.tonemap_exposure = 1.0
	var world := WorldEnvironment.new()
	world.environment = environment
	shot.add_child(world)

	key = DirectionalLight3D.new()
	key.light_energy = 1.05
	key.shadow_enabled = true
	key.directional_shadow_max_distance = 48.0
	key.shadow_bias = .08
	key.shadow_normal_bias = .85
	shot.add_child(key)
	key.look_at_from_position(Vector3(2.4, 6, 4), Vector3.ZERO)

	var floor_mesh := PlaneMesh.new()
	floor_mesh.size = Vector2(150, 150)
	var floor_visual := MeshInstance3D.new()
	floor_visual.mesh = floor_mesh
	floor_visual.position.y = -.002
	floor_material = StandardMaterial3D.new()
	floor_material.albedo_color = Color("#8c8a89")
	floor_material.roughness = .94
	floor_visual.material_override = floor_material
	shot.add_child(floor_visual)


func use_soft_shadows() -> void:
	key.shadow_enabled = true
	key.light_angular_distance = 4.0
	key.directional_shadow_blend_splits = true
	key.shadow_bias = .10
	key.shadow_normal_bias = 1.0


func use_final_studio() -> void:
	key.shadow_enabled = true
	key.light_angular_distance = 0.0
	key.shadow_blur = 2.5
	key.directional_shadow_blend_splits = true
	key.shadow_bias = .10
	key.shadow_normal_bias = 1.0
	key.light_energy = .86
	environment.ambient_light_energy = .59
	floor_material.albedo_color = Color("#747373")


func use_anisotropic_marks() -> void:
	for node in model.find_children("*", "MeshInstance3D", true, false):
		var mesh := node as MeshInstance3D
		for index in mesh.mesh.get_surface_count():
			var material := mesh.get_active_material(index) as StandardMaterial3D
			if material != null and (material.albedo_texture != null or material.roughness_texture != null):
				material.texture_filter = BaseMaterial3D.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS_ANISOTROPIC


func create_cameras() -> void:
	camera_record = JSON.parse_string(FileAccess.get_file_as_string("res://camera-reference.json"))
	fixed_camera = Camera3D.new()
	shot.add_child(fixed_camera)
	fixed_camera.keep_aspect = Camera3D.KEEP_HEIGHT
	fixed_camera.fov = float(camera_record.vertical_fov_deg)
	fixed_camera.near = float(camera_record.clip_m[0])
	fixed_camera.far = float(camera_record.clip_m[1])
	var cols: Array = camera_record.godot_basis_columns
	fixed_camera.transform = Transform3D(Basis(vector(cols[0]), vector(cols[1]), vector(cols[2])),
		vector(camera_record.godot_origin))
	inspection = Camera3D.new()
	inspection.keep_aspect = Camera3D.KEEP_HEIGHT
	inspection.fov = 40
	inspection.near = .1
	inspection.far = 160
	shot.add_child(inspection)
	update_orbit()


func vector(values: Array) -> Vector3:
	return Vector3(values[0], values[1], values[2])


func create_figure() -> void:
	figure = Node3D.new()
	figure.name = "ScaleFigure_1_80m"
	figure.position = Vector3(2.33, .45, 1.89)
	shot.add_child(figure)
	var suit := StandardMaterial3D.new()
	suit.albedo_color = Color("#536dc5")
	suit.roughness = .78
	var face := StandardMaterial3D.new()
	face.albedo_color = Color("#9ba9bf")
	face.roughness = .68
	human_part(Vector3(0, 1.665, 0), Vector3(.23, .27, .22), face)
	human_part(Vector3(0, 1.19, 0), Vector3(.43, .62, .24), suit)
	for side in [-1, 1]:
		human_part(Vector3(side * .30, 1.15, 0), Vector3(.135, .54, .145), suit, side * .13)
		human_part(Vector3(side * .11, .48, 0), Vector3(.18, .86, .18), suit)
		human_part(Vector3(side * .11, .055, .037), Vector3(.18, .11, .27), suit)


func human_part(at: Vector3, size: Vector3, material: Material, tilt := 0.0) -> void:
	var mesh := BoxMesh.new()
	mesh.size = size
	var obj := MeshInstance3D.new()
	obj.mesh = mesh
	obj.material_override = material
	obj.position = at
	obj.rotation.z = tilt
	figure.add_child(obj)


func create_hud() -> void:
	hud = Label.new()
	hud.mouse_filter = Control.MOUSE_FILTER_IGNORE
	hud.position = Vector2(15, 10)
	hud.add_theme_color_override("font_color", Color.WHITE)
	hud.add_theme_color_override("font_shadow_color", Color.BLACK)
	hud.add_theme_constant_override("shadow_offset_x", 1)
	hud.add_theme_constant_override("shadow_offset_y", 2)
	add_child(hud)


func select_comparison() -> void:
	comparison = true
	fixed_camera.make_current()
	figure.hide()
	if hud:
		hud.text = "1  Match Blender   |   2  Orbit   |   F / S / B  Front / Right / Back"


func select_orbit() -> void:
	comparison = false
	inspection.make_current()
	figure.visible = scale_visible
	update_orbit()
	if hud:
		hud.text = "Drag  Orbit   |   Wheel  Zoom   |   R  1.8 m figure   |   1  Match Blender"


func update_orbit() -> void:
	var az := deg_to_rad(yaw)
	var el := deg_to_rad(pitch)
	var ray := Vector3(sin(az) * cos(el), sin(el), cos(az) * cos(el))
	inspection.look_at_from_position(TARGET + ray * distance, TARGET)


func _input(event: InputEvent) -> void:
	if not mode.is_empty():
		return
	if event is InputEventKey and event.pressed and not event.echo:
		match event.keycode:
			KEY_1: select_comparison()
			KEY_2: select_orbit()
			KEY_F: orbit_preset(0.0)
			KEY_S: orbit_preset(90.0)
			KEY_B: orbit_preset(180.0)
			KEY_R:
				if not comparison:
					scale_visible = not scale_visible
					figure.visible = scale_visible
	if comparison:
		return
	if event is InputEventMouseButton:
		if event.button_index == MOUSE_BUTTON_LEFT:
			dragging = event.pressed
		elif event.pressed and event.button_index in [MOUSE_BUTTON_WHEEL_UP, MOUSE_BUTTON_WHEEL_DOWN]:
			distance = clampf(distance * (.89 if event.button_index == MOUSE_BUTTON_WHEEL_UP else 1.12), 5.0, 37.0)
			update_orbit()
	elif event is InputEventMouseMotion and dragging:
		yaw -= event.relative.x * .36
		pitch = clampf(pitch + event.relative.y * .26, 2.0, 73.0)
		update_orbit()


func orbit_preset(azimuth: float, pitch_deg := 8.5, range_m := 10.2) -> void:
	yaw = azimuth
	pitch = pitch_deg
	distance = range_m
	select_orbit()


func capture(path: String, video_frame := false) -> void:
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(path.get_base_dir()))
	await RenderingServer.frame_post_draw
	var frame := shot.get_texture().get_image()
	var status := frame.save_jpg(path, .94) if video_frame else frame.save_png(path)
	if status != OK:
		faults.append("Capture failed: " + path)


func verify_projection() -> Array[Dictionary]:
	var rows: Array[Dictionary] = []
	for item: Dictionary in camera_record.landmarks:
		var point := fixed_camera.unproject_position(vector(item.godot_point))
		var expected := Vector2(item.blender_pixel[0], item.blender_pixel[1])
		var error_px := point.distance_to(expected)
		if error_px > .35:
			faults.append("Camera projection delta > 0.35 px: " + String(item.object))
		rows.append({"object": item.object, "godot_pixel": [point.x, point.y],
			"blender_pixel": item.blender_pixel, "delta_px": error_px})
	return rows


func run_evidence(asset: Dictionary) -> void:
	var projection := verify_projection()
	var collisions := PhysicsReview.test(shot.find_world_3d().direct_space_state)
	for row in collisions:
		if not row.passed:
			faults.append("Collision query failed: " + row.test)
	if mode.begins_with("seams-"):
		await SeamCapture.capture(self, mode.trim_prefix("seams-"))
	elif mode == "initial":
		await capture(EVIDENCE + "previews/00-import-initial.png")
		scale_visible = false
		orbit_preset(168, 16)
		await capture(EVIDENCE + "previews/00-import-initial-rear.png")
	elif mode == "diagnostics":
		key.shadow_enabled = false
		await capture(EVIDENCE + "previews/diagnostic-no-shadows.png")
		use_soft_shadows()
		await capture(EVIDENCE + "previews/diagnostic-soft-shadows.png")
		scale_visible = false
		orbit_preset(124, 12, 13.5)
		await capture(EVIDENCE + "previews/diagnostic-trilinear-oblique.png")
		use_anisotropic_marks()
		await capture(EVIDENCE + "previews/diagnostic-aniso-oblique.png")
	elif mode == "stills":
		await capture(EVIDENCE + "previews/01-godot-matched.png")
		scale_visible = false
		for view in [[0.0, "02-front"], [90.0, "03-right"], [180.0, "04-rear"]]:
			orbit_preset(view[0])
			await capture(EVIDENCE + "previews/" + view[1] + ".png")
		scale_visible = true
		orbit_preset(32, 11, 9.35)
		await capture(EVIDENCE + "previews/05-human-scale.png")
		scale_visible = false
		orbit_preset(70, 17, 19)
		await capture(EVIDENCE + "previews/06-oblique-far.png")
	else:
		var frame_folder := EVIDENCE + "frames"
		DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(frame_folder))
		scale_visible = false
		orbit_preset(25.0, 10.0)
		for frame in 240:
			var t := float(frame) / 239.0
			yaw = 25.0 + 360.0 * t
			pitch = 10.0 + 8.0 * sin(PI * t)
			distance = 10.1 - 2.0 * sin(PI * clampf(t / .60, 0.0, 1.0)) + 9.8 * sin(PI * clampf((t - .60) / .40, 0.0, 1.0))
			update_orbit()
			await capture(frame_folder + ("/frame-%04d.jpg" % frame), true)
		print("VIDEO_FRAMES 240")
	var evidence := {
		"asset": asset, "camera_projection": projection, "collisions": collisions,
		"test_collision_bodies": collision_count, "player_traversal": "not tested",
		"engine": Engine.get_version_info().string,
		"device": RenderingServer.get_video_adapter_name(),
		"driver": RenderingServer.get_current_rendering_driver_name(),
		"renderer": RenderingServer.get_current_rendering_method(),
		"resolution": [RENDER_SIZE.x, RENDER_SIZE.y], "msaa": "4x", "taa": shot.use_taa,
		"tonemap": int(environment.tonemap_mode), "exposure_multiplier": environment.tonemap_exposure,
		"ambient_energy": environment.ambient_light_energy, "key_energy": key.light_energy,
		"angular_shadow_distance_deg": key.light_angular_distance,
		"shadow_bias": key.shadow_bias, "shadow_normal_bias": key.shadow_normal_bias,
		"shadow_distance_m": key.directional_shadow_max_distance,
		"shadow_blur": key.shadow_blur,
		"anisotropy_project_level": ProjectSettings.get_setting("rendering/textures/default_filters/anisotropic_filtering_level"),
		"faults": faults, "passed": faults.is_empty()
	}
	var report_path := EVIDENCE + "reports/" + mode + ".json"
	if mode.begins_with("seams-"):
		report_path = SeamCapture.OUTPUT + "reports/" + mode + ".json"
		evidence["asset_resource"] = asset_scene.resource_path
		evidence["fixed_fov_y"] = fixed_camera.fov
		evidence["fixed_camera"] = str(fixed_camera.transform)
		evidence["sun_transform"] = str(key.transform)
		evidence["near_views"] = SeamCapture.VIEWS.map(func(view): return str(view))
	var file := FileAccess.open(report_path, FileAccess.WRITE)
	if file != null:
		file.store_string(JSON.stringify(evidence, "  "))
		file.close()
	else:
		faults.append("Could not write report")
	print("REVIEW ", mode, " failures: ", faults)
	get_tree().quit(0 if faults.is_empty() else 1)
