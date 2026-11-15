extends Node3D

var problems: Array[String] = []

func check(ok: bool, message: String) -> void:
	if not ok:
		problems.append(message)

func _ready() -> void:
	var spec: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://asset.params.json"))
	var dims: Array = spec.dimensions_m
	var packed = load("res://assets/" + str(spec.id) + ".glb") as PackedScene
	if packed == null:
		push_error("GLB could not be loaded as PackedScene")
		get_tree().quit(1)
		return
	var model = packed.instantiate() as Node3D
	add_child(model)
	var meshes = model.find_children("*", "MeshInstance3D", true, false)
	if model is MeshInstance3D:
		meshes.append(model)
	check(meshes.size() == 1, "Expected one mesh")
	var bounds := AABB()
	var first := true
	var tris := 0
	var materials: Array = []
	var marker_front := false
	for mesh_node: MeshInstance3D in meshes:
		var box: AABB = mesh_node.global_transform * mesh_node.get_aabb()
		bounds = box if first else bounds.merge(box)
		first = false
		check(mesh_node.global_position.length() < 0.0001, "Mesh origin shifted")
		for s in mesh_node.mesh.get_surface_count():
			var arrays: Array = mesh_node.mesh.surface_get_arrays(s)
			var verts: PackedVector3Array = arrays[Mesh.ARRAY_VERTEX]
			var normals: PackedVector3Array = arrays[Mesh.ARRAY_NORMAL]
			var indices: PackedInt32Array = arrays[Mesh.ARRAY_INDEX]
			tris += int(indices.size()/3) if not indices.is_empty() else int(verts.size()/3)
			check(normals.size()==verts.size(), "Missing vertex normals")
			for n in normals:
				check(n.is_finite() and abs(n.length()-1)<0.001, "Invalid normal")
			var mat = mesh_node.get_active_material(s) as StandardMaterial3D
			check(mat != null, "Missing StandardMaterial3D")
			if mat:
				materials.append({"name":mat.resource_name,"roughness":mat.roughness,"albedo_srgb":[mat.albedo_color.r,mat.albedo_color.g,mat.albedo_color.b]})
				check(abs(mat.roughness-float(spec.roughness))<0.001, "Roughness changed")
				var expected_color: Array = spec.front_color_linear if mat.resource_name == "FrontMarker" else spec.base_color_linear
				var linear_color: Color = mat.albedo_color.srgb_to_linear()
				check(abs(linear_color.r-float(expected_color[0]))<0.001 and abs(linear_color.g-float(expected_color[1]))<0.001 and abs(linear_color.b-float(expected_color[2]))<0.001, "Base color changed after sRGB conversion")
				if mat.resource_name == "FrontMarker":
					for i in verts.size():
						var world_v: Vector3 = mesh_node.global_transform * verts[i]
						var world_n: Vector3 = mesh_node.global_basis * normals[i]
						if abs(world_v.z-float(dims[1])/2.0)<0.001 and world_n.z > 0.99:
							marker_front = true
	var expected := Vector3(dims[0],dims[2],dims[1])
	check((bounds.size-expected).length()<0.001, "Dimensions changed")
	check(abs(bounds.position.y)<0.001, "Bottom not on ground")
	check(model.position.length()<0.001, "Root origin shifted")
	check(tris<=int(spec.triangle_budget), "Triangle budget exceeded")
	check(materials.size()==2, "Material count changed")
	check(marker_front, "Blender -Y did not map to Godot +Z marker")
	var body := StaticBody3D.new()
	var shape := CollisionShape3D.new()
	var box_shape := BoxShape3D.new()
	box_shape.size = expected
	shape.shape = box_shape
	shape.position.y = expected.y/2
	body.add_child(shape)
	add_child(body)
	var ground := MeshInstance3D.new()
	ground.mesh = PlaneMesh.new()
	ground.mesh.size = Vector2.ONE * float(spec.lighting.godot_ground_size)
	var ground_mat := StandardMaterial3D.new()
	ground_mat.albedo_color = Color(0.36,0.36,0.36)
	ground_mat.roughness = 1.0
	ground.material_override = ground_mat
	ground.position.y = -0.002
	add_child(ground)
	var environment := WorldEnvironment.new()
	environment.environment = Environment.new()
	environment.environment.background_mode = Environment.BG_COLOR
	environment.environment.background_color = Color(0.18,0.18,0.18)
	environment.environment.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	environment.environment.ambient_light_color = Color.WHITE
	environment.environment.ambient_light_energy = float(spec.lighting.godot_ambient_energy)
	environment.environment.tonemap_mode = Environment.TONE_MAPPER_LINEAR
	add_child(environment)
	var light := DirectionalLight3D.new()
	light.rotation_degrees = Vector3(-48,-30,0)
	light.light_energy = float(spec.lighting.godot_key_energy)
	light.shadow_enabled = true
	add_child(light)
	var camera := Camera3D.new()
	camera.projection = Camera3D.PROJECTION_ORTHOGONAL
	camera.size = float(spec.camera.godot_vertical_size)
	camera.far = float(spec.camera.godot_far)
	camera.position = Vector3(2.6,2.4,3.5)
	add_child(camera)
	camera.look_at(Vector3(0,expected.y/2.0,0))
	camera.current = true
	for frame in 12:
		await get_tree().process_frame
	await get_tree().physics_frame
	var hit = get_world_3d().direct_space_state.intersect_ray(PhysicsRayQueryParameters3D.create(Vector3(0,2,0),Vector3(0,-1,0)))
	check(not hit.is_empty() and abs(hit.position.y-expected.y)<0.001, "Collision ray missed top surface")
	await RenderingServer.frame_post_draw
	var screenshot_error = get_viewport().get_texture().get_image().save_png("res://../previews/godot_front.png")
	check(screenshot_error==OK, "Screenshot save failed")
	var report := {"passed":problems.is_empty(),"engine":Engine.get_version_info().string,"triangles":tris,"dimensions_m":[bounds.size.x,bounds.size.y,bounds.size.z],"materials":materials,"front_marker_on_positive_z":marker_front,"collision_ray_hit_top":not hit.is_empty(),"problems":problems,"performance":"not profiled; counts are structural evidence only"}
	var file = FileAccess.open("res://../reports/godot-validation.json",FileAccess.WRITE)
	file.store_string(JSON.stringify(report,"\t"))
	print("GODOT_VALIDATION_", "PASS" if problems.is_empty() else "FAIL", " ", JSON.stringify(report))
	get_tree().quit(0 if problems.is_empty() else 1)
