"""One bounded stdio MCP session using the existing installation, no second service install."""
import argparse
import asyncio
import datetime
import json
import os
from pathlib import Path
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def main():
    p = argparse.ArgumentParser()
    p.add_argument('--config', required=True)
    p.add_argument('--tool', default='get_scene_info', choices=['get_scene_info','get_addon_status','execute_blender_code','look'])
    p.add_argument('--script')
    p.add_argument('--args-json', default='{}')
    p.add_argument('--log', required=True)
    a = p.parse_args()
    c = json.loads(Path(a.config).read_text(encoding='utf-8'))
    args = json.loads(a.args_json)
    if a.script:
        script = str(Path(a.script).resolve())
        args['code'] = 'import runpy\nrunpy.run_path(' + repr(script) + ', run_name="__main__")'
    env = {**os.environ, 'BLENDER_HOST':'127.0.0.1', 'BLENDER_PORT':str(c['blender_port']), 'DISABLE_TELEMETRY':'true'}
    server = StdioServerParameters(command=c['mcp_server'], args=[], env=env)
    async with stdio_client(server) as (read, write):
        async with ClientSession(read, write, read_timeout_seconds=datetime.timedelta(seconds=180)) as session:
            init = await session.initialize()
            listed = await session.list_tools()
            result = await session.call_tool(a.tool, args)
            record = {'server':init.model_dump(mode='json'), 'tools':[t.name for t in listed.tools], 'called':a.tool, 'result':result.model_dump(mode='json')}
            Path(a.log).write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding='utf-8')
            for item in result.content:
                if item.type == 'text':
                    print(item.text)
            if result.isError or any(item.type=='text' and (item.text.startswith('Error') or 'Traceback (most recent' in item.text) for item in result.content):
                raise SystemExit(1)

if __name__ == '__main__':
    asyncio.run(main())
