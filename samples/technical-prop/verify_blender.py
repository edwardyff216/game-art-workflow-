"""Fresh-process .blend and GLB round trip; checks are for this convex technical sample."""
import bpy
import bmesh
import json
import math
from pathlib import Path
from mathutils import Vector

base = Path(__file__).resolve().parent
p = json.loads((base/'asset.params.json').read_text(encoding='utf-8'))

def inspect(obj):
    ev = obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
    mesh = ev.to_mesh()
    mesh.calc_loop_triangles()
    coords = [obj.matrix_world @ v.co for v in mesh.vertices]
    low = [min(v[i] for v in coords) for i in range(3)]
    high = [max(v[i] for v in coords) for i in range(3)]
    bm = bmesh.new()
    bm.from_mesh(mesh)
    # glTF splits vertices at normal/UV/material boundaries. Weld ONLY in the QA copy.
    bmesh.ops.remove_doubles(bm, verts=list(bm.verts), dist=1e-6)
    bm.normal_update()
    center = Vector([(a+b)/2 for a,b in zip(low,high)])
    data = {
        'name':obj.name, 'bounds_min':low, 'bounds_max':high,
        'dimensions_m':[b-a for a,b in zip(low,high)],
        'origin_world':list(obj.matrix_world.translation),
        'triangles':len(mesh.loop_triangles),
        'materials':[{'name':m.name,'base_color':list(m.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value),'roughness':m.node_tree.nodes.get('Principled BSDF').inputs['Roughness'].default_value} for m in mesh.materials],
        'nonmanifold_edges_after_qa_weld':sum(not e.is_manifold for e in bm.edges),
        'degenerate_faces':sum(f.calc_area()<1e-10 for f in bm.faces),
        'inward_faces_convex_sample_only':sum(f.normal.dot(f.calc_center_median()-center)<=0 for f in bm.faces),
        'signed_volume_m3':bm.calc_volume(signed=True),
        'finite_unit_normals':all(all(math.isfinite(n) for n in f.normal) and abs(f.normal.length-1)<1e-4 for f in bm.faces),
        'front_marker_normal_y':[f.normal.y for f in bm.faces if f.material_index==1 and f.normal.y < -0.9]
    }
    bm.free()
    ev.to_mesh_clear()
    assert max(abs(a-b) for a,b in zip(data['dimensions_m'],p['dimensions_m']))<1e-4, data
    assert max(abs(v) for v in data['origin_world'])<1e-6
    assert abs(data['bounds_min'][2])<1e-6
    assert data['triangles']<=p['triangle_budget']
    assert data['nonmanifold_edges_after_qa_weld']==0 and data['degenerate_faces']==0
    assert data['inward_faces_convex_sample_only']==0 and data['signed_volume_m3']>0
    assert data['finite_unit_normals'] and data['front_marker_normal_y']
    assert len(data['materials'])==2
    for m, col in zip(data['materials'],[p['base_color_linear'],p['front_color_linear']]):
        assert max(abs(a-b) for a,b in zip(m['base_color'],col))<1e-4
        assert abs(m['roughness']-p['roughness'])<1e-4
    return data

bpy.ops.wm.open_mainfile(filepath=str(base/'source'/(p['id']+'.blend')))
source = inspect(bpy.data.objects[p['id']])
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(base/'exports'/(p['id']+'.glb')))
meshes = [o for o in bpy.context.scene.objects if o.type=='MESH']
assert len(meshes)==1
roundtrip = inspect(meshes[0])
report = {'passed':True,'blender':bpy.app.version_string,'source':source,'glb_roundtrip':roundtrip,'scope':'convex untextured static sample; no general concave-normal validator, no UV/animation/LOD checks'}
(base/'reports'/'blender-roundtrip.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print('BLENDER_ROUNDTRIP_PASS', json.dumps(report))
