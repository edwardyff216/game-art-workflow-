# 实际交付文件与位置

下列文件已实际存在；目标正式游戏内的美术配置、场景和资产仍未创建。没有全局配置变更，也没有合并到既有游戏 main。

| 已创建文件 | 绝对路径 |
|---|---|
| README.md | `D:\Game 仓库，一些点子\game-art-workflow\README.md` |
| WORKFLOW.md | `D:\Game 仓库，一些点子\game-art-workflow\WORKFLOW.md` |
| AGENTS.md | `D:\Game 仓库，一些点子\game-art-workflow\AGENTS.md` |
| tools.local.json | `D:\Game 仓库，一些点子\game-art-workflow\tools.local.json` |
| .codex/config.toml | `D:\Game 仓库，一些点子\game-art-workflow\.codex\config.toml` |
| templates/PROJECT_ART.md | `D:\Game 仓库，一些点子\game-art-workflow\templates\PROJECT_ART.md` |
| templates/project-art.template.json | `D:\Game 仓库，一些点子\game-art-workflow\templates\project-art.template.json` |
| templates/asset-record.template.json | `D:\Game 仓库，一些点子\game-art-workflow\templates\asset-record.template.json` |
| audit/ENVIRONMENT.md | `D:\Game 仓库，一些点子\game-art-workflow\audit\ENVIRONMENT.md` |
| audit/git-baseline.json | `D:\Game 仓库，一些点子\game-art-workflow\audit\git-baseline.json` |
| audit/git-preservation.json | `D:\Game 仓库，一些点子\game-art-workflow\audit\git-preservation.json` |
| audit/project-file-inventory.json | `D:\Game 仓库，一些点子\game-art-workflow\audit\project-file-inventory.json` |
| audit/tool-inventory.json | `D:\Game 仓库，一些点子\game-art-workflow\audit\tool-inventory.json` |
| audit/upstream-revisions.json | `D:\Game 仓库，一些点子\game-art-workflow\audit\upstream-revisions.json` |
| .agents/skills/create-game-assets/SKILL.md | `D:\Game 仓库，一些点子\game-art-workflow\.agents\skills\create-game-assets\SKILL.md` |
| adapters/start-blender.ps1 | `D:\Game 仓库，一些点子\game-art-workflow\adapters\start-blender.ps1` |
| adapters/blender_start.py | `D:\Game 仓库，一些点子\game-art-workflow\adapters\blender_start.py` |
| adapters/mcp_call.py | `D:\Game 仓库，一些点子\game-art-workflow\adapters\mcp_call.py` |
| adapters/validate-sample.ps1 | `D:\Game 仓库，一些点子\game-art-workflow\adapters\validate-sample.ps1` |
| adapters/vendor/blender_mcp.py | `D:\Game 仓库，一些点子\game-art-workflow\adapters\vendor\blender_mcp.py` |
| samples/technical-prop/asset-record.json | `D:\Game 仓库，一些点子\game-art-workflow\samples\technical-prop\asset-record.json` |
| samples/technical-prop/asset.params.json | `D:\Game 仓库，一些点子\game-art-workflow\samples\technical-prop\asset.params.json` |
| samples/technical-prop/build_asset.py | `D:\Game 仓库，一些点子\game-art-workflow\samples\technical-prop\build_asset.py` |
| samples/technical-prop/verify_blender.py | `D:\Game 仓库，一些点子\game-art-workflow\samples\technical-prop\verify_blender.py` |
| samples/technical-prop/ACCEPTANCE.md | `D:\Game 仓库，一些点子\game-art-workflow\samples\technical-prop\ACCEPTANCE.md` |
| samples/technical-prop/source/technical_block_v001.blend | `D:\Game 仓库，一些点子\game-art-workflow\samples\technical-prop\source\technical_block_v001.blend` |
| samples/technical-prop/exports/technical_block_v001.glb | `D:\Game 仓库，一些点子\game-art-workflow\samples\technical-prop\exports\technical_block_v001.glb` |
| samples/technical-prop/godot/project.godot | `D:\Game 仓库，一些点子\game-art-workflow\samples\technical-prop\godot\project.godot` |
| samples/technical-prop/godot/validation.tscn | `D:\Game 仓库，一些点子\game-art-workflow\samples\technical-prop\godot\validation.tscn` |
| samples/technical-prop/godot/validation.gd | `D:\Game 仓库，一些点子\game-art-workflow\samples\technical-prop\godot\validation.gd` |
| samples/technical-prop/previews/blender_front.png | `D:\Game 仓库，一些点子\game-art-workflow\samples\technical-prop\previews\blender_front.png` |
| samples/technical-prop/previews/blender_rear.png | `D:\Game 仓库，一些点子\game-art-workflow\samples\technical-prop\previews\blender_rear.png` |
| samples/technical-prop/previews/godot_front.png | `D:\Game 仓库，一些点子\game-art-workflow\samples\technical-prop\previews\godot_front.png` |
| samples/technical-prop/reports/blender-roundtrip.json | `D:\Game 仓库，一些点子\game-art-workflow\samples\technical-prop\reports\blender-roundtrip.json` |
| samples/technical-prop/reports/godot-validation.json | `D:\Game 仓库，一些点子\game-art-workflow\samples\technical-prop\reports\godot-validation.json` |

上游仓库仅作为审查副本保存在 audit/upstream，记录了固定提交；不作为已安装插件。完整版本、来源、未执行项和原生 MCP 注册限制见 audit/ENVIRONMENT.md。

首轮样板建立时工作流 main 尚无提交。后续本地检查点的文件范围见 [版本管理说明](VERSION_CONTROL.md)，当前默认样板版本见 [Frontier Relay 07 v10 最终记录](samples/frontier-relay-07/final-review/REVIEW.md)，回退基线见 [v09 接缝验收](samples/frontier-relay-07/seam-review/REVIEW.md)。
