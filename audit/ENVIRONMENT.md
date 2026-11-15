# 环境与来源核查（2026-11-15）

## 路径与项目身份

实测操作系统为 Windows，PowerShell；不是从任务措辞猜测。初始 cwd 为 `D:\Game 仓库，一些点子`，这是多项目集合，没有自身的 project.godot 或 Git 根。用户本轮没有指定唯一正式目标项目。

本轮已创建维护根目录：`D:\Game 仓库，一些点子\game-art-workflow`；独立样板项目根：`D:\Game 仓库，一些点子\game-art-workflow\samples\technical-prop\godot`。工作流新 Git 仓库分支 `main`，**无提交**、交付文件均未提交。没有向任何已有项目分支合并。

| 已存在游戏项目绝对根目录 | 检查到的项目声明 | Git 状态（开始时） |
|---|---|---|
| `D:\Game 仓库，一些点子\仓库生存` | 4.7，实际渲染设置 gl_compatibility；AGENTS 写 4.7.2 | implementation，`b87d17b0c7fb99e1bbd8f16d04010704d11b38ae`；多个预览、project.godot 已修改，多个 .import 未跟踪 |
| `D:\Game 仓库，一些点子\thebox` | 4.7 / Forward Plus | main，`9ced4bce80169f36d4374ac95f9a29338d14a182`；干净 |
| `D:\Game 仓库，一些点子\水系魔法实验室` | 4.4 / GL Compatibility | 未找到自身 Git 仓库 |
| `D:\Game 仓库，一些点子\game-dev-lessons` | 4.7 / Forward Plus | 未找到自身 Git 仓库 |
| `D:\Game 仓库，一些点子\DynamicWaterDemo-reference` | 旧版 project.godot，未声明 4.x features | master，`cf244484daefa2edfc04b260d0f98997773e8485`；干净；不尝试升级或转换 |

其他现有仓库也保留：dota-personal-coach 的 feat/personal-coach（`03b82348754c9e016c0bc14ef3aa2e91a1bbd649`，有改动）；GPT-SoVITS 的 main（`48b1a0169a28582a8984402f82cf438d3bfa6aca`，干净）；imagination-tools-film 的 main（`02e24b2a9f0212faedf7a5f78025310840e30ba8`，有改动）。完整逐文件未提交列表及 worktree 路径保存在 `D:\Game 仓库，一些点子\game-art-workflow\audit\git-baseline.json`。最终比对见 git-preservation.json。

另外观察到一个已运行的 Godot 编辑器使用 `D:\wxkbactcard`，以及 D 盘有 wxkbactcard-handover 目录；它们不在本轮选定样板中，未修改、未宣称其交接成果进入 main，未把它们当成用户选定目标。

## 已有说明、参考与模型的实际位置

- 全局 `C:\Users\OEM\.codex\AGENTS.md` 存在但为空。`D:\AGENTS.md`、初始 cwd 下 AGENTS.md 未找到。
- `D:\Game 仓库，一些点子\仓库生存\AGENTS.md`：已有协作约束；未用于授权本轮修改其游戏。
- `D:\Game 仓库，一些点子\仓库生存\docs\IMPLEMENTATION.md`：阶段状态/验收约束。
- `D:\Game 仓库，一些点子\仓库生存\docs\ART_DIRECTION.md`：已有角色规范，不是跨项目场景美术规范。
- `D:\Game 仓库，一些点子\仓库生存\docs\ASSET-NOTICES.md`、`DEMO_QA.md`、`ROOM-OBJECTS.md`：来源、验收与场景对象说明。
- `D:\Game 仓库，一些点子\thebox\docs\PROJECT_AUDIT_AND_PLAN.md` 是历史审查，不能用其中“无 Git/无场景”的旧状态替代今天的磁盘/Git 事实。
- `D:\Game 仓库，一些点子\thebox\docs\SAMPLE_AND_ACCEPTANCE.md`、`TWO_D_SPECIAL_DELIVERY.md`、`TWO_D_PROGRESS_DELIVERY.md` 等为已有交付/验收说明；`D:\Game 仓库，一些点子\thebox\docs\art\AI_PUPPET_PARTS_SPEC.md` 为已有美术说明。
- `D:\Game 仓库，一些点子\水系魔法实验室\README.md` 及其 docs/superpowers 内有设计/计划。
- 初始 cwd 游戏项目范围未找到命名为 HANDOFF/交接的专门文件；上述 DELIVERY 文件是实际存在的移交类文档。完整 Markdown 清单见 project-file-inventory.json。
- 现有角色参考：`D:\Game 仓库，一些点子\仓库生存\docs\art-qa\lin-an-anime-concept-v3.png`、`D:\Game 仓库，一些点子\仓库生存\docs\art-qa\anime-residents-v1\xu-qing.png`，以及 v2/v3 子目录。未将它们当成本轮场景方向。
- `D:\Game 仓库，一些点子\thebox\assets\characters\martial_artist` 存在已有角色资产和说明；所有发现的图像绝对路径记录在 project-file-inventory.json（5 个游戏项目共记录 285 个图像/媒体/模型/Markdown 文件）。
- 现有模型位于 `D:\Game 仓库，一些点子\DynamicWaterDemo-reference\assets\meshes`：crate.obj、island.obj、palmtree.obj、surfboard.obj、surfboard_collision.obj、zodiac.obj、zodiac_hull.obj。本轮没有导入或修改这些旧模型。
- 在这 5 个游戏项目内未找到 .blend/.glb/.gltf/.fbx；工作区其他软件的 Duck.glb 是 Gradio 示例，不是本轮项目资产。
- 工作区确有视频，例如 `D:\Game 仓库，一些点子\output\yanghao-video\yanghao-final.mp4` 和 `D:\Game 仓库，一些点子\output\dingbro-video\dingbro-final.mp4`，未确认是场景参考。**本轮正式参考图/视频：待提供。**

## 版本与实际工具位置

| 工具 | 实测版本 | 实际路径/来源 | 本轮使用 |
|---|---|---|---|
| Blender | 5.2.4 LTS，hash cd5dc428cce1 | `F:\SteamLibrary\steamapps\common\Blender\blender.exe`，已有 Steam 安装 | 是，GUI MCP + 后台回读 |
| Blender 旧安装 | 4.0.2 | `C:\Program Files\Blender Foundation\Blender 4.0\blender.exe` | 仅 --version |
| Godot | 4.7.2.stable.steam.ed1daf0bf | `D:\SteamLibrary\steamapps\common\Godot Engine\godot.windows.opt.tools.64.exe` | 是，样板导入与真实渲染 |
| Godot 旧安装 | 4.4.1.stable.official.49a5bc7b6 | `D:\gedot\Godot_v4.4.1-stable_win64.exe\Godot_v4.4.1-stable_win64_console.exe` | 仅 --version |
| Python | 3.12.10 | `C:\Users\OEM\AppData\Local\Programs\Python\Python312\python.exe` | 审查/图像 QA |
| MCP Python | 3.13.16（pyvenv.cfg） | `E:\local-ai\cache\uv\archive-v0\1E7WG7QOrgAKTFVA\Scripts\python.exe` | MCP SDK 客户端 |
| mcp-for-blender | 2.2.9 | 同一 uv 环境 Scripts/mcp-for-blender.exe；已有 PyPI 包，仓库 ahujasid/mcp-for-blender | 复用，没有再 pip/uv 安装 |
| MCP SDK | 1.30.0 | 同一环境 Lib/site-packages/mcp | 真正 stdio initialize/list_tools/call_tool |
| uv | 0.13.0 | WinGet 的 astral-sh.uv 包目录；Get-Command 精确路径见 tool-paths.json | 仅核查 |
| Pillow | 12.3.0 | Python 3.12 已有环境 | 预览 PNG 尺寸/元数据 QA |

已安装 Blender 全局插件：`C:\Users\OEM\AppData\Roaming\Blender Foundation\Blender\5.2\scripts\addons\blender_mcp.py`，addon 1.8 / 协议 15；服务器要求协议 16。全局文件保留原样。

本轮复制**同一已安装服务器包 bundled/addon.py**到 `D:\Game 仓库，一些点子\game-art-workflow\adapters\vendor\blender_mcp.py`（addon 2.0 / 协议 16），附 MIT LICENSE。仅由独立 Blender 实例临时注册，不写全局插件或首选项。这是配套插件副本，不是第二套 MCP 服务器安装。

初始观察到 8 个既有 mcp-for-blender 进程，均指向同一缓存安装；当时 9876 没有监听且没有 Blender GUI。它们的启动配置来源未找到，未停止。新样板固定 127.0.0.1:9877，每次调用只运行一个短时 stdio 会话并正常关闭。进程数量不能当作服务已可用的证据。

## skills、MCP、插件及配置范围

- 用户配置 `C:\Users\OEM\.codex\config.toml` 已只读审查，直接 mcp_servers 只有 node_repl，没有 blender/godot；完整敏感环境变量不导出。已启用插件名与已验证 skill 文件位置见 tool-inventory.json。
- Codex 插件缓存实际根为 `C:\Users\OEM\.codex\plugins\cache`，包括 openai-bundled、openai-curated、openai-curated-remote、openai-primary-runtime。会话暴露的连接器/skill 列表与磁盘 config 不是同一份状态，不能互相冒充。
- 已有相关 skill：`C:\Users\OEM\.codex\skills\generate2dmap\SKILL.md`、`generate2dsprite\SKILL.md`、`spa\SKILL.md`、`game-analysis\SKILL.md`；系统 `C:\Users\OEM\.codex\skills\.system\imagegen\SKILL.md`、`skill-creator\SKILL.md`。文件存在，但本轮没有验证其各自执行器，不把 2D 资产技能等同 Blender 3D 流程。
- 本轮精简安装范围：`D:\Game 仓库，一些点子\game-art-workflow\.agents\skills\create-game-assets`，仅这一个 skill 及其引用/脚本/模板/Apache-2.0 LICENSE 和 NOTICE。未安装整个 79-skill 仓库或 router，未装 DSmereski skill。
- skill 来源固定于 audit/upstream/gamedev-skills 的提交；本地安装副本维持上游内容，项目约束在 AGENTS.md。工作流新增内容在本库维护，**没有另建自定义 skill**。
- 本轮配置文件：`D:\Game 仓库，一些点子\game-art-workflow\tools.local.json`、`D:\Game 仓库，一些点子\game-art-workflow\.codex\config.toml`。前者供已验证适配脚本使用，后者按官方格式仅供此项目原生工具接入。
- MCP 原生注册状态：普通 CLI 未加载项目配置，当前会话没有热加载出 Blender 工具；原因未确认，不能说“原生接入已完成”。同样配置以 CLI 单次 `-c` 传入后 `mcp get blender` 成功，记录在 audit/logs/codex-command-scoped-config.json。真实 Blender 通信由 mcp_call.py 已验证，无须全局配置变更。
- 插件目录搜索 Blender/Godot 返回空列表，未安装其他同类插件。Godot AI 和 Material Maker 未在本轮安装或连接。现有项目未找到 Godot AI 的 plugin.cfg（搜索范围为初始 cwd 项目，不代表全机不存在）。

## 候选来源审查与采纳范围

所有上游文档作为待审材料，不执行管道下载脚本。版本提交详见 upstream-revisions.json，原文保留在 audit/upstream。

| 候选来源 | 实际审查 | 结论 |
|---|---|---|
| [MCP for Blender](https://github.com/ahujasid/mcp-for-blender) | README 的 Codex/手动安装/Telemetry，pyproject，服务与 addon 启动代码；2.2.9；MIT；Python ≥3.10，mcp ≥1.26,<2，httpx ≥0.27；README 写 Blender ≥3.0 | 复用安装，配套 addon 单独加载；关闭遥测与第三方服务；没有购买 Premium。未运行会配置多个客户端的 setup/install 脚本 |
| [Godot AI](https://github.com/hi-godot/godot-ai) | README、pyproject、plugin.cfg、LICENSE；当前 4.4.1，MIT，Godot ≥4.7，Python ≥3.11,<3.15，固定 fastmcp/mcp 等依赖 | 本机 4.7.2 满足；4.4 项目不能直接套当前版本。其 Configure 默认全局且会迁移条目，本轮不需要编辑器接口，使用 CLI/GDScript；不升级任何项目 |
| [create-game-assets](https://github.com/gamedev-skills/awesome-gamedev-agent-skills/tree/main/skills/disciplines/create-game-assets) | SKILL、3D reference、安装说明、LICENSE、两个 QA 脚本；Apache-2.0；Python/Pillow>=10,<14，现有 12.3 满足 | 仅手动复制这一个目录。采纳规范、家族、清单、技术与游戏内验收；用户五步及项目规则优先。图像生成/2D检查不是本轮模型制作条件 |
| [DSmereski blender-asset](https://github.com/DSmereski/agent-skills/blob/main/skills/blender-asset.md) | 实际 skill 和仓库全文件清单；MIT | make_asset.py、verify_asset.py、cleanup_asset.py、build_manifest.py 未找到；不宣称可运行。仅借鉴参数化与回读思想，独立编写本轮样板。不采纳“文件存在/标志字符串即完成美术”的标准 |
| [Material Maker](https://github.com/RodZill4/material-maker) | 固定 commit 的 README、LICENSE.md；MIT（例外文件从其声明） | 样板只有常量 PBR，无程序纹理系列需求；不引入。未测试安装、纹理生成或与 Blender 材质互转 |

Codex 项目级 MCP 设置和需重启/受信任项目的说明见 [OpenAI 官方 MCP 文档](https://learn.chatgpt.com/docs/extend/mcp?surface=cli)。本轮没有修改全局信任或其他项目配置。Godot 正交阴影诊断参考 [DirectionalLight3D 官方文档](https://docs.godotengine.org/en/stable/classes/class_directionallight3d.html)，结论同时由实际前后截图支持。

## 通过、限制与未执行

通过：MCP 实际连接与场景读取、Blender 创建/修改材质、.blend 保存、GLB 导出、新进程回读、源/导出尺寸与原点/法线/材质、Godot 导入与真实运行、轴向/颜色空间/粗糙度/碰撞、实际渲染截图人工观察、输出已存在时拒绝覆盖且源 SHA256 不变、PNG QA。

未执行：正式项目集成与实际玩法镜头验收、风格批准、纹理/UV/烘焙/动画/骨骼/LOD 全流程、性能基准、Godot AI 操作、Material Maker、付费图生 3D。源模型凸体法线检查不是泛用凹形网格检查器。

skill-creator quick_validate.py 未通过执行：当前两个 Python 环境都缺 PyYAML；本轮未为了验证未修改的上游 skill 再安装依赖。skill 原文件完整复制和引用路径另行核对，两个图像脚本依赖 Pillow 可用，asset_report 已实跑。

没有凭据或费用阻碍本地技术链路。唯一原生工具接入待办是桌面/CLI 对项目级 MCP 的加载确认；已验证适配脚本可直接继续工作。全局旧 addon 协议升级会影响其他使用者，未擅自覆盖。

收尾时已关闭本任务启动的独立 Blender，保留源文件和证据；未停止初始观察到的其他 MCP 进程。启动器重复实例保护实测通过。最终交付核对记录在 audit/delivery-check.json。
