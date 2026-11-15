extends RefCounted

const RADIANCE := preload("res://lighting_review_sky.gdshader")
const SOURCE := Vector3(5.4, 8.4, 4.3)
const KEY_ENERGY := 1.07
const AMBIENT_ENERGY := .51


static func set_direct_and_ambient(review: Control) -> void:
	review.key.look_at_from_position(SOURCE, Vector3.ZERO)
	review.key.light_energy = KEY_ENERGY
	review.environment.ambient_light_energy = AMBIENT_ENERGY


static func apply(review: Control) -> void:
	set_direct_and_ambient(review)
	var sky_material := ShaderMaterial.new()
	sky_material.shader = RADIANCE
	var sky := Sky.new()
	sky.sky_material = sky_material
	sky.process_mode = Sky.PROCESS_MODE_QUALITY
	sky.radiance_size = Sky.RADIANCE_SIZE_128
	review.environment.sky = sky
	review.environment.reflected_light_source = Environment.REFLECTION_SOURCE_SKY
	review.environment.ssao_enabled = false
