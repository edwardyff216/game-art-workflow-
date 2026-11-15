# 工作流版本管理

v09 建立了首个本地检查点 `330fc62`。v1 继续保留 v09 源、GLB、原场景和验收记录，v10 另存并作为默认样板。可用 `git log -1 --oneline` 和 `git status --short --branch` 查看当前提交与工作区。

| 入库 | 留在本机或可重建 |
| --- | --- |
| 流程、模板、脚本、项目配置和导入设置 | Godot 缓存、Blender 自动备份、日志、PID、本机配置 |
| 可编辑检查点、回退 GLB、默认场景使用的 GLB 与小型依赖 | 用户原始参考附件、上游审查克隆与临时诊断 |
| 资产版本记录、报告和精选验收图 | 全尺寸截图序列、逐帧素材和录像 |

已交付的二进制源和运行资产使用普通 Git。v10 GLB 嵌入运行材质贴图，Godot 采用提取模式并保存提取的 PNG 和导入配置。用于 Blender 的生成贴图也随源保存。精选验收图放在样板的 `final-review/evidence/`，完整的图和录像用入口复现。参见 [忽略规则](.gitignore) 和 [二进制属性](.gitattributes)。

单个制作源或发布资产达到 10 MiB，或频繁更新的二进制明显推高体积时，先评估具体路径，再考虑使用 Git LFS。该机器已检测到 Git LFS 3.6.1。可按需执行 `git lfs install --local` 与 `git lfs track "相对资产路径"`，将规则纳入 `.gitattributes`。使用本地工作区备份保存对象库和独立媒体。

检出后从 [tools.example.json](tools.example.json) 复制填写 `tools.local.json`，启动脚本也可指定外部配置。旧轮次实验使用样板自己的 `tools.session.json` 时，按同结构提供其 Godot 路径。原生 MCP 的项目配置样例见 [.codex/config.example.toml](.codex/config.example.toml)。Godot 导入会重建 `.godot`。工作流本地检查点按明确范围提交，远程操作另行授权。
