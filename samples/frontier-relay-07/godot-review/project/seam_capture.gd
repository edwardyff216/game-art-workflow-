extends RefCounted

const OUTPUT := "res://../../seam-review/"
const VIEWS := [
	["door-front", Vector3(.50, 1.56, 2.24), Vector3(0, .04, 3.82), 36.0],
	["door-oblique", Vector3(.50, 1.56, 2.24), Vector3(2.15, .06, 3.35), 36.0],
	["window-front", Vector3(1.66, 2.32, .20), Vector3(4.5, .02, 0), 35.0],
	["window-oblique", Vector3(1.66, 2.32, .20), Vector3(3.85, .19, -2.33), 35.0],
	["service-front", Vector3(1.59, 1.78, -2.24), Vector3(3.1, 0, 0), 37.0],
	["service-oblique", Vector3(1.59, 1.78, -2.24), Vector3(2.65, .06, -1.66), 37.0],
	["back", Vector3(.01, 1.63, -2.97), Vector3(.04, .36, -5.6), 39.0],
]


static func capture(review: Control, tag: String) -> void:
	var folder := OUTPUT + "previews/" + tag + "/"
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(folder))
	review.select_comparison()
	await review.capture(folder + "matched.png")
	review.figure.hide()
	review.inspection.make_current()
	for spec in VIEWS:
		var focus: Vector3 = spec[1]
		review.inspection.fov = spec[3]
		review.inspection.look_at_from_position(focus + spec[2], focus)
		await review.capture(folder + spec[0] + ".png")
	if tag != "after":
		return
	var frames := OUTPUT + "frames/"
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(frames))
	review.inspection.fov = 43.0
	var target := Vector3(.43, 1.63, .12)
	for frame in 168:
		var t := float(frame) / 167.0
		var yaw := deg_to_rad(-40.0 + 360.0 * t)
		var range_m := 9.25 + .9 * sin(PI * t)
		var pos := target + Vector3(sin(yaw) * range_m, .88 + sin(PI*t)*.55, cos(yaw) * range_m)
		review.inspection.look_at_from_position(pos, target)
		await review.capture(frames + ("frame-%04d.jpg" % frame), true)
	print("SEAM_ORBIT_FRAMES 168")
