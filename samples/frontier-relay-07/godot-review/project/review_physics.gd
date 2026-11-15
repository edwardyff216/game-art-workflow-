extends RefCounted
## Test-scene collision proxies and physics queries for the unchanged visual GLB.

const ASSET_LAYER := 1
const FLOOR_LAYER := 2


static func box(parent: Node3D, label: String, center: Vector3, size: Vector3, layer: int) -> void:
	var shape := BoxShape3D.new()
	shape.size = size
	var member := CollisionShape3D.new()
	member.shape = shape
	var body := StaticBody3D.new()
	body.name = label
	body.collision_layer = layer
	body.collision_mask = 0
	parent.add_child(body)
	body.position = center
	body.add_child(member)


static func build(parent: Node, model: Node3D) -> int:
	var group := Node3D.new()
	group.name = "ReviewCollision"
	parent.add_child(group)
	# Closed shell proxy, including the closed doorway, with no interior.
	box(group, "ClosedBuilding", Vector3(0, 1.745, -0.3875),
		Vector3(3.40, 2.59, 5.215), ASSET_LAYER)
	box(group, "TestFloor", Vector3(0, -.102, 0), Vector3(160, .2, 160), FLOOR_LAYER)
	var count := 2
	for node in model.find_children("*", "MeshInstance3D", true, false):
		var mesh := node as MeshInstance3D
		var id := String(mesh.name).replace("_", " ")
		if not (id.begins_with("Entry tread") or id.begins_with("Left deck")
			or id.begins_with("Right apron tile") or id.begins_with("Core deck")
			or id == "Independent cargo case shell" or id == "Cargo case lid"
			or id == "Continuous clipped fascia"):
			continue
		var hull := mesh.mesh.create_convex_shape(true, false)
		if hull == null:
			continue
		var body := StaticBody3D.new()
		body.name = String(mesh.name) + "Collision"
		body.collision_layer = ASSET_LAYER
		body.collision_mask = 0
		group.add_child(body)
		body.global_transform = mesh.global_transform
		var member := CollisionShape3D.new()
		member.shape = hull
		body.add_child(member)
		count += 1
	return count


static func test(space: PhysicsDirectSpaceState3D) -> Array[Dictionary]:
	var probes := [
		["tread_1", Vector3(.43, 1, 3.42), Vector3(.43, -.2, 3.42), 1, .15, ASSET_LAYER],
		["tread_2", Vector3(.43, 1, 3.08), Vector3(.43, -.2, 3.08), 1, .30, ASSET_LAYER],
		["tread_3", Vector3(.43, 1, 2.62), Vector3(.43, -.2, 2.62), 1, .45, ASSET_LAYER],
		["right_deck", Vector3(2.6, 1, 2.04), Vector3(2.6, -.2, 2.04), 1, .45, ASSET_LAYER],
		["cargo_lid", Vector3(2.74, 2, -1.65), Vector3(2.74, .5, -1.65), 1, 1.16, ASSET_LAYER],
		["closed_entry", Vector3(.49, 1.4, 4), Vector3(.49, 1.4, 0), 2, 2.22, ASSET_LAYER],
		["right_wall", Vector3(4, 1.5, 0), Vector3(0, 1.5, 0), 0, 1.70, ASSET_LAYER],
		["rear_wall", Vector3(0, 1.5, -5), Vector3(0, 1.5, 0), 2, -2.995, ASSET_LAYER],
		["outside_deck_is_clear", Vector3(5, 1, 0), Vector3(5, -.1, 0), 0, null, ASSET_LAYER],
		["test_floor", Vector3(5, 1, 0), Vector3(5, -.1, 0), 1, -.002, FLOOR_LAYER],
	]
	var checks: Array[Dictionary] = []
	for probe in probes:
		var query := PhysicsRayQueryParameters3D.create(probe[1], probe[2], probe[5])
		var hit := space.intersect_ray(query)
		var measured: Variant = null if hit.is_empty() else hit.position[probe[3]]
		var expected: Variant = probe[4]
		var label: String = "" if hit.is_empty() else String(hit.collider.name)
		var passed: bool = (measured == null) if expected == null else (
			measured != null and absf(measured - expected) <= .017)
		checks.append({"test": probe[0], "expected_m": expected, "measured_m": measured,
			"collider": label, "passed": passed})
	return checks
