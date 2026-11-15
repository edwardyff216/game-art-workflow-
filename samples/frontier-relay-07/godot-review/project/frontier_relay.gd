extends "res://review.gd"

const StudioC = preload("res://studio_c.gd")


func use_final_studio() -> void:
	super()
	StudioC.apply(self)


func expected_base_color_maps() -> int:
	return 5
