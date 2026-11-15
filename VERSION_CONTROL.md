# 工作流版本管理

本库最初只有 Git 元数据和未跟踪文件。v09 开工时没有任何历史提交或远程，提交者配置可用，未发现阻止本地提交的配置问题。此前各轮保留的是工作区文件，本轮建立首个本地检查点。可用 `git log -1 --oneline` 查询实际提交。

| 入库 | 留在当前工作区 |
|---|---|
| 通用文档、项目模板、脚本、测试场景、导入配置、资产和验收记录 | Godot 缓存、Blender 自动备份、工具临时日志、进程 PID |
| 已选用的 `.blend` 检查点、可回退 GLB、测试场景依赖的 GLB 和底色 PNG | 可重建的渲染、参考附件、录像、逐帧素材、临时诊断图和形体 v05 草稿 |
| 示例工具配置、必要第三方许可和固定版本记录 | 带绝对安装路径的本机 JSON/TOML、上游审查克隆及涉及其他项目的临时清单 |

当前投入检查点的 `.blend` 与 `.glb` 均小于 1 MiB，使用普通 Git 二进制文件保存，便于本地回退。小型运行时 PNG 也入库。渲染和录像继续留在各轮交付的本机路径，可按验收脚本重建。原始参考图随用户附件保存，重新检出时需自行放回。见 [忽略规则](.gitignore) 与 [二进制属性](.gitattributes)。

将来单件制作源或发布资产达到 10 MiB，或频繁更新的大资产明显推高仓库体积，先选定资产路径、再在添加到索引前启用该路径的 Git LFS。此机器已检测到 Git LFS 3.6.1。可用 `git lfs install --local` 和 `git lfs track "相对资产路径"`，同时纳入更新后的 `.gitattributes`。本检查点可从本地 Git 对象恢复。对象库及本机预览可通过常规工作区备份保存。

重新检出时从 [tools.example.json](tools.example.json) 复制并填写 `tools.local.json`。样板启动脚本需要时可再复制为样板自己的 `tools.session.json`。原生 Codex MCP 配置用 [.codex/config.example.toml](.codex/config.example.toml) 作为样例。测试场景打开后由 Godot 重新生成 `.godot` 导入缓存。
