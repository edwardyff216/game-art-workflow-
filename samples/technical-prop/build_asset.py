"""Sample-specific parametric geometry. Run in the isolated Blender via MCP."""
import bpy
import json
from pathlib import Path
from mathutils import Vector

base = Path(__file__).resolve().parent if '__file__' in globals() else Path(bpy.context.scene['art_workflow_sample'])
p = json.loads((base / 'asset.params.json').read_text(encoding='utf-8'))
target = Vector((0, 0, p['dimensions_m'][2] / 2))
for folder in ('source', 'exports', 'previews', 'reports', 'textures'):
    (base / folder).mkdir(exist_ok=True)
out = base / 'source' / (p['id'] + '.blend')
if out.exists() or (base / 'exports' / (p['id'] + '.glb')).exists():
    raise RuntimeError('Source or export already exists. Choose a new sample/version before regeneration.')
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
scene = bpy.context.scene
scene.unit_settings.system = 'METRIC'
scene.unit_settings.scale_length = 1.0
bpy.ops.mesh.primitive_cube_add(size=1)
obj = bpy.context.object
obj.name = p['id']
obj.dimensions = p['dimensions_m']
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
for v in obj.data.vertices:
    v.co.z += p['dimensions_m'][2] / 2
for name, color in [('Body',p['base_color_linear']),('FrontMarker',p['front_color_linear'])]:
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = color
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get('Principled BSDF')
    bsdf.inputs['Base Color'].default_value = color
    bsdf.inputs['Roughness'].default_value = p['roughness']
    obj.data.materials.append(mat)
for face in obj.data.polygons:
    face.material_index = 1 if face.normal.y < -0.9 else 0
bevel = obj.modifiers.new('EditableEdgeBevel','BEVEL')
bevel.width = p['bevel_m']
bevel.segments = p['bevel_segments']
obj['purpose'] = p['purpose']
obj['forward'] = p['blender_forward']
obj['origin_policy'] = p['origin']
obj['source_kind'] = 'original_parametric_technical_sample'
bpy.ops.export_scene.gltf(filepath=str(base/'exports'/(p['id']+'.glb')), export_format='GLB', use_selection=True, export_apply=True, export_yup=True, export_extras=True, export_materials='EXPORT')
world = bpy.data.worlds.new('TechnicalNeutralWorld')
world.use_nodes = True
world.node_tree.nodes['Background'].inputs[0].default_value = (0.18,0.18,0.18,1)
world.node_tree.nodes['Background'].inputs[1].default_value = 0.8
scene.world = world
bpy.ops.object.light_add(type='AREA', location=(2,-3,4))
bpy.context.object.name = 'TechnicalKey'
bpy.context.object.data.energy = 450
bpy.context.object.data.shape = 'DISK'
bpy.context.object.data.size = 4
bpy.context.object.rotation_euler = (target-bpy.context.object.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=(2.6,-3.5,2.4))
camera = bpy.context.object
camera.name = 'TechnicalCamera'
camera.data.type = 'ORTHO'
camera.data.ortho_scale = p['camera']['size']
scene.camera = camera
scene.render.engine = 'CYCLES'
scene.cycles.samples = 16
scene.render.resolution_x, scene.render.resolution_y = p['camera']['resolution']
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = 'PNG'
scene.view_settings.view_transform = 'Standard'
for label, pos in [('front',(2.6,-3.5,2.4)),('rear',(-2.6,3.5,2.4))]:
    camera.location = pos
    camera.rotation_euler = (target-camera.location).to_track_quat('-Z','Y').to_euler()
    scene.render.filepath = str(base/'previews'/('blender_'+label+'.png'))
    bpy.ops.render.render(write_still=True)
camera.location = (2.6,-3.5,2.4)
camera.rotation_euler = (target-camera.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.wm.save_as_mainfile(filepath=str(out))
print('BUILD_OK', str(out))
