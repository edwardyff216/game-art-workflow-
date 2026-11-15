extends SceneTree

func _initialize() -> void:
    var inputs := OS.get_cmdline_user_args()
    if inputs.size() != 1:
        push_error("Expected one absolute GLB path")
        quit(2)
        return
    var document := GLTFDocument.new()
    var state := GLTFState.new()
    var error := document.append_from_file(inputs[0], state)
    if error != OK:
        push_error("GLB import failed: " + error_string(error))
        quit(1)
        return
    var imported := document.generate_scene(state)
    if imported == null:
        push_error("GLB did not instantiate")
        quit(1)
        return
    var materials := {}
    var graphic_meshes := {}
    var mesh_count := 0
    for node in imported.find_children("*", "MeshInstance3D", true, false):
        var instance := node as MeshInstance3D
        mesh_count += 1
        for index in instance.mesh.get_surface_count():
            var material := instance.mesh.surface_get_material(index) as StandardMaterial3D
            if material == null:
                continue
            var name := material.resource_name
            var data := instance.mesh.surface_get_arrays(index)
            var has_uv: bool = (data[Mesh.ARRAY_TEX_UV] is PackedVector2Array
                           and not data[Mesh.ARRAY_TEX_UV].is_empty())
            if name.contains("Graphics") and material.albedo_texture != null and has_uv:
                graphic_meshes[name] = true
            materials[name] = {
                "metallic": material.metallic,
                "roughness": material.roughness,
                "emission": material.emission_enabled,
                "texture": material.albedo_texture != null,
                "has_uv0": has_uv
            }
    var emission_count := 0
    for name in materials:
        if materials[name]["emission"]:
            emission_count += 1
    var passed: bool = mesh_count > 90 and graphic_meshes.size() == 4 and emission_count == 3
    print(JSON.stringify({
        "version": Engine.get_version_info()["string"],
        "passed": passed,
        "mesh_instances": mesh_count,
        "textured_graphics_materials": graphic_meshes.size(),
        "emissive_materials": emission_count,
        "materials": materials
    }, "  "))
    imported.free()
    quit(0 if passed else 1)
