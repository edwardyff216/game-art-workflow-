"""Start the EXISTING addon in a disposable GUI instance; never save user preferences."""
import bpy
import importlib.util
import json
import sys
from pathlib import Path

config = json.loads(Path(sys.argv[sys.argv.index('--') + 1]).read_text(encoding='utf-8'))
spec = importlib.util.spec_from_file_location('blender_mcp', config['blender_addon'])
addon = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = addon
spec.loader.exec_module(addon)
addon.register()
bpy.context.scene.blendermcp_auto_start_server = False
if bpy.app.timers.is_registered(addon._addon_update_check_on_startup):
    bpy.app.timers.unregister(addon._addon_update_check_on_startup)
for name in ('polyhaven', 'hyper3d', 'sketchfab', 'tripo', 'meshy', 'polypizza', 'hunyuan3d'):
    setattr(bpy.context.scene, 'blendermcp_use_' + name, False)
bpy.context.scene.blendermcp_port = config['blender_port']
server = addon.BlenderMCPServer(host='127.0.0.1', port=config['blender_port'])
bpy.types.blendermcp_server = server
server.start()
print('ART_WORKFLOW_BLENDER_READY', bpy.app.version_string, flush=True)
