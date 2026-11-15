# 可复用的游戏场景美术工作流

已建立独立工作流，并用 Blender → GLB → Godot 跑通一个**技术验证用**资产。正式游戏项目、最终美术方向、参考图均待指定；没有改造已有游戏美术。

维护根目录：`D:\Game 仓库，一些点子\game-art-workflow`。
工作流维护分支为 `main`。本地检查点和素材管理方式见 [版本管理说明](VERSION_CONTROL.md)。

## 入口

- [五步流程与返修规则](WORKFLOW.md)
- [项目美术说明模板](templates/PROJECT_ART.md)
- [机器可读项目配置模板](templates/project-art.template.json)
- [资产记录模板](templates/asset-record.template.json)
- [环境、兼容性、安装范围与来源审查](audit/ENVIRONMENT.md)
- [本轮实测结果](samples/technical-prop/ACCEPTANCE.md)
- [Frontier Relay 07 最新接缝验收](samples/frontier-relay-07/seam-review/REVIEW.md)
- [所有重要文件的绝对路径](DELIVERABLES.md)
- [技术样板资产记录](samples/technical-prop/asset-record.json)
- [复用的 create-game-assets skill](.agents/skills/create-game-assets/SKILL.md)

## 使用方式

在新项目中，把 `templates/PROJECT_ART.md` 和 `project-art.template.json` 复制到该项目约定的文档目录，填写项目特有内容。引用本目录的 WORKFLOW.md 和 skill 绝对路径即可跨项目使用；不必全局安装。若希望该项目自动发现 skill，只复制这一个 skill 目录到目标项目 `.agents/skills/`，保留 LICENSE，再添加项目自己的约束。

工具路径仅存于 `tools.local.json` 和项目内 `.codex/config.toml`。换机器后重新核查并调整这些文件。现有 uv 缓存可被清理，届时按 ENVIRONMENT.md 的来源与版本恢复，不能假设缓存路径永久存在。

本轮通过的是 Codex 调用本地适配脚本，经 MCP SDK stdio 协议访问官方 MCP 服务器，再访问 Blender 插件的真实连接。**不是单纯用后台 Blender 代替 MCP。** 当前会话未动态出现原生 Blender 工具；CLI 普通 `mcp get blender` 也未加载项目配置，故桌面原生自动注册仍待新会话/项目配置加载验证。可立即使用已经通过实测的 `mcp_call.py`，无需改全局配置。

### 连接和读取

从工作流根目录执行（PowerShell）：

```powershell
./adapters/start-blender.ps1
$toolConfig = Get-Content -Raw ./tools.local.json | ConvertFrom-Json
& $toolConfig.mcp_python ./adapters/mcp_call.py --config ./tools.local.json --tool get_scene_info --log ./audit/logs/mcp-current-scene.json
```

启动器使用 `--factory-startup` 独立实例、回环端口 9877、现有 MCP 安装配套插件。已有端口会拒绝重复启动；先核查其所属实例。不开启外部素材服务，不保存用户 Blender 首选项。`.blend` 内保留建模修改器；交互编辑时用此源文件另存新版本。

本轮结束时已保存源文件并关闭本任务启动的独立 Blender；用户原先的服务器进程未触碰。下次使用先执行启动器。直接操作系统打开 .blend 不等于已启动这套独立 MCP 配置。

在 Codex 中作为受信任项目打开此根目录后，可按官方方式重启客户端尝试加载 `.codex/config.toml`，再确认工具实际出现。不要为解决局部加载问题直接运行自动安装器去改所有客户端。

### 复查已交付样板

```powershell
./adapters/validate-sample.ps1
```

它重新打开 .blend、重新导入 GLB，再执行 Godot 原生导入、运行独立场景、检查材质/尺寸/碰撞并截图。会刷新样板的 reports、previews 和 Godot 导入缓存，不修改正式游戏。还必须打开图片人工观察。脚本超时和错误均算失败，不以缓存文件存在冒充成功。

### 新建另一个技术样板

复制 `samples/technical-prop` 到一个新目录，只保留脚本、参数和 Godot 文本场景；不要沿用 source/exports/previews/reports/.godot 的旧结果。设置新 id，核查 Godot 版本和目录。启动独立 Blender 后调用：

```powershell
& $toolConfig.mcp_python ./adapters/mcp_call.py --config ./tools.local.json --tool execute_blender_code --script '<新样板绝对路径>/build_asset.py' --log '<新样板绝对路径>/reports/mcp-build.json'
./adapters/validate-sample.ps1 -Sample '<新样板绝对路径>'
```

这个生成器仅是尺寸块示例，不是通用建筑生成器；它拒绝覆盖已存在的 .blend。对应凸体法线检测不可直接套在凹形、开口或有骨骼的模型上。

## 第一轮正式制作的启动语句

“请按 `D:\Game 仓库，一些点子\game-art-workflow\WORKFLOW.md` 开始第一轮。目标项目是 `<绝对路径>`；参考图位于 `<实际文件>`；先读取项目美术说明，完成参考分析、资产清单、镜头和灰盒。第一批只做 `<一个代表模块或小场景>`，在游戏镜头确认后再成组扩展。”

镜头、尺度依据、目标平台和已有预算若尚未确定，先列待决项及低成本试验。正式风格不能由技术尺寸块推导。
