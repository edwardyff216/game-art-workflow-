# 通用场景美术工作流 v1

通用场景美术工作流 v1，已通过一个科幻硬表面建筑样板验证，用户已确认本样板最终视觉。

## 从这里打开样板

| 文件 | 用途 |
| --- | --- |
| [最终 Blender 源](samples/frontier-relay-07/source/frontier-relay-07-finish-v10.blend) | 可编辑 v10，打包全部使用的贴图 |
| [最终 GLB](samples/frontier-relay-07/godot-review/project/assets/frontier-relay-07-v10.glb) | 资产及嵌入贴图，Godot 默认场景直接实例化此文件 |
| [Godot 项目](samples/frontier-relay-07/godot-review/project/project.godot) · [默认样板场景](samples/frontier-relay-07/godot-review/project/frontier_relay.tscn) | v10 和固定照明 C，F6 运行该场景或 F5 运行项目 |
| [同机位材质对比](samples/frontier-relay-07/final-review/evidence/01-material-comparison.jpg) · [最终验收记录](samples/frontier-relay-07/final-review/REVIEW.md) | 参数、截图、限制、源文件到引擎实例的版本关系 |
| [v09 接缝基线与回退](samples/frontier-relay-07/seam-review/REVIEW.md) · [照明选择依据](samples/frontier-relay-07/lighting-review/REVIEW.md) | 历史基线和 A/B/C 对照 |

### 工具与复现入口

从仓库根目录用 PowerShell 运行。首次检出时，将 [tools.example.json](tools.example.json) 复制为 `tools.local.json`，填写当前机器的路径。`Open` 只需要 `godot_executable`，`Check` 还需要 Python 3.12、NumPy 2.5.3、Pillow 12.3.0 和 FFmpeg 9.0.2（PATH 或参数指定），`Rebuild` 使用 Python 依赖和 `blender_executable`。样板已实测 Blender 5.2.4 LTS 与 Godot 4.7.2 Steam / Forward+。全部模式可用 `-ConfigPath` 指向已有本机配置。

```powershell
$sample = './samples/frontier-relay-07/final-review/run_final.ps1'
& $sample -Mode Open
& $sample -Mode Check
& $sample -Mode Rebuild
```

- `Open` 首次导入后打开项目默认场景。按 1 回对照镜头，按 2 后可拖动环绕，F / S / B 切换正、侧、背面。
- `Check` 运行真实 Godot 导入与固定机位捕获、静态碰撞、源/GLB 范围核对和实机证据生成。打开输出中的对比、近远景和录像进行视觉验收。
- `Rebuild` 从 v09 生成贴图、可编辑 v10 和 GLB，在新的目录比较场景数据、几何属性及嵌入图片。两种检查默认写到忽略的 `final-review/previews/<新目录>`，也可通过 `-OutputDirectory` 给出尚不存在的路径。
- GLB 提供网格和材质数据。照明 C、镜头、天空反射着色器及静态碰撞代理由项目场景提供。独立打开 GLB 时需要在目标引擎配置对应环境。

### Blender 交互制作

填写本机配置的 Blender、插件和 MCP 路径后，从仓库根目录运行以下命令。MCP 经已有本地服务器和回环端口接入，版本和首次核查见 [环境记录](audit/ENVIRONMENT.md)。

```powershell
./adapters/start-blender.ps1
$toolConfig = Get-Content -Raw ./tools.local.json | ConvertFrom-Json
& $toolConfig.mcp_python ./adapters/mcp_call.py --config ./tools.local.json --tool get_scene_info
```

先读场景和文件路径再修改，另存已批准源文件。本样板的批量复建已验证可从 Blender 命令行执行。另有 [最小技术方块](samples/technical-prop/ACCEPTANCE.md) 与 `./adapters/validate-sample.ps1`，用于单独检查通用工具连接。Codex 桌面原生自动注册仍待验证。

## 为新项目开始第一步

1. 阅读 [通用五步流程](WORKFLOW.md)。复制 [项目美术说明](templates/PROJECT_ART.md)，按需采用 [JSON 配置模板](templates/project-art.template.json) 和 [资产记录模板](templates/asset-record.template.json)。
2. 提供目标项目绝对路径、代表参考和使用场景。填写已知的尺度、镜头、材质、平台与预算。未知项标记为待确定。
3. 在第一步审核参考的直接观察、尺寸估算和补充设计，选定一个代表资产或小场景。随后在形体与模块关系、最终引擎实景两个节点确认。具体配色和光照参数随项目选择。
4. 对目标项目做一次独立验证后，再扩大批量。复用 [create-game-assets skill](.agents/skills/create-game-assets/SKILL.md) 的清单与审查方法，项目配置留在目标项目。素材入库方式见 [版本管理](VERSION_CONTROL.md)。

启动示例可说“请按通用工作流开始第一步。项目位于 `<绝对路径>`，参考位于 `<实际文件>`。先梳理方向、尺寸假设和代表资产。”
