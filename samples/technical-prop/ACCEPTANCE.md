# 技术验证样板验收

结论：本地 Blender MCP → 可编辑 .blend → GLB → Godot 4.7.2 独立场景链路通过。**技术验证用，不是正式美术风格提案，也不代表生产资产或性能达标。**

根目录：`D:\Game 仓库，一些点子\game-art-workflow\samples\technical-prop`。

| 检查 | 实际证据与观察 |
|---|---|
| MCP 连接 | audit/logs/mcp-initial-scene.json 读到初始 Cube/Light/Camera；mcp-build.json 创建资产；mcp-final-scene.json 读到技术块、灯和相机。已使用 stdio 协议，不是只测 TCP 端口 |
| 插件匹配 | 独立加载 addon 2.0 / protocol 16；服务器 2.2.9；旧全局 addon 仍保留，服务器磁盘扫描可能继续提示其旧版本，但运行握手记录为协议 16 |
| 可编辑源 | source/technical_block_v001.blend；保留单体网格及 EditableEdgeBevel 修改器，2 个材质。没有穿插零件拼出正面假轮廓 |
| GLB | exports/technical_block_v001.glb；只导出资产，没有预览灯、相机或地面 |
| 尺度/原点 | Blender X/Y/Z = 1.2/0.8/0.6 m，底中心 (0,0,0)；Godot X/Y/Z = 1.2/0.6/0.8 m；误差 <0.001 m |
| 轴向 | 橙色正面 Blender -Y → Godot +Z，有顶点位置和法线检测；这是样板约定，不强制其他项目用此正面 |
| 网格 | 108 triangles；预算 500。重新导入后仅在 QA 副本焊接硬边拆分顶点，非流形边 0、退化面 0、凸体向内面 0，法线有限且单位长度，体积正 |
| 材质 | Body / FrontMarker，粗糙度 0.72。Blender 回读颜色不变；Godot sRGB 转回线性后与源数据相符。没有纹理，不宣称验证 UV/贴图 |
| 碰撞 | 独立场景中 BoxShape3D 1.2×0.6×0.8，射线命中 y=0.6 顶面。倒角未用于复杂碰撞，符合此尺寸块测试需求 |
| 渲染 | Blender Cycles 16 samples、800×600 正/背面；Godot Compatibility/OpenGL 3.3、RTX 3060 Ti、800×600、MSAA 4×、正交镜头、无景深/泛光/模糊 |
| 视觉观察 | 正反面轮廓连贯，矩形比例一致，倒角可读，橙色正面标记正确。Godot 硬方向光比 Blender 大面积光更平、更硬，不要求逐像素一致 |
| 问题诊断 | 初始 Godot 截图有顶面过亮和前面三角阴影条纹。保持模型/材质不变，仅把正交相机 far 改为 20 时条纹消失，见 shadow-probe 日志；再调 key=0.5、ambient=0.3 后顶面可读。初始图保留为 godot_initial_rejected.png，不混入通过图 |
| 文件保护 | 再次执行生成脚本返回 exit 1，说明已有 .blend 拒绝覆盖；源 SHA256 前后相同。不是生成失败后忽略错误 |

通过截图：

- `D:\Game 仓库，一些点子\game-art-workflow\samples\technical-prop\previews\blender_front.png`
- `D:\Game 仓库，一些点子\game-art-workflow\samples\technical-prop\previews\blender_rear.png`
- `D:\Game 仓库，一些点子\game-art-workflow\samples\technical-prop\previews\godot_front.png`

自动报告：reports/blender-roundtrip.json、godot-validation.json、image-qa.json。用 `adapters/validate-sample.ps1` 可刷新 Blender/Godot 报告和引擎截图。当前结果不是仅依据脚本无错误；上述 3 张图片已由 Codex 实际打开观察。

明确未验收：用户正式参考与风格、正式项目镜头/玩法、贴图和 UV、动画/LOD、不同渲染后端、设备性能。108 三角形和一次截图不能推出帧率、显存或同屏数量上限。
