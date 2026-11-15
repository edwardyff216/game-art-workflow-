# Frontier Relay 07 · Godot 实景验收

已在独立项目中运行 v08，等待用户验收。开工与完成时，工作流仓库均为 `main` 且尚无提交。[v08 Blender 源文件](../source/frontier-relay-07-materials-v08.blend)、[原始 GLB](../material-review/export-check/frontier-relay-07-v08.glb) 的 SHA-256 与开工记录一致。[测试项目里的 GLB](project/assets/frontier-relay-07-v08.glb) 与原始 GLB 逐字节相同，由 Godot 编辑器导入为 PackedScene，再作为单个建筑实例加入测试场景。[校验记录](reports/baseline-sha256.json) · [上轮记录](../material-review/REVIEW.md)

## 观察文件

| 视图 | 文件 |
|---|---|
| 同机位 | [Blender v08 与 Godot 并排](previews/00-blender-godot.jpg) · [Godot 原尺寸](previews/01-godot-matched.png) · [Blender 原尺寸](../material-review/previews/03-materials.png) |
| 三向 | [正面](previews/02-front.png) · [右侧](previews/03-right.png) · [背面](previews/04-rear.png) |
| 尺度与距离 | [1.80 m 人形](previews/05-human-scale.png) · [19 m 斜视](previews/06-oblique-far.png) |
| 运动 | [10 秒环绕与远近观察](previews/07-orbit.mp4) · [逐秒抽帧](previews/08-orbit-contact.png) |
| 原始导入检查 | [主机位](previews/00-import-initial.png) · [后侧](previews/00-import-initial-rear.png) |

Godot 实际输出 240 帧，经 FFmpeg 9.0.2 编为 H.264 MP4，24 fps、10 秒。编码时底部补 1 像素以满足 YUV420 偶数尺寸，图片仍为原生 1280 × 853。轨迹从前侧绕一周，中间贴近到约 8.1 m，再退到约 19.9 m。已完整解码成片并查看逐秒抽帧和代表性近远画面。

## 相机与复现

[相机采集脚本](read_blender_camera.py)从实际 v08 文件读取矩阵、109 mm 焦距、36 mm 传感器宽、水平 Fit、零偏移和方形像素。1280 × 853 画幅下有效传感器高为 23.990625 mm。按 `2 × atan(尺寸 / (2 × 焦距))` 得水平 18.7541°、垂直 12.5601°。Godot 通过 `KEEP_HEIGHT` 使用垂直 FOV，位姿按 Blender `(x,y,z) → (x,z,−y)` 换轴。原始相机数据和 7 个真实网格顶点存于 [camera-reference.json](project/camera-reference.json)。Godot 重新投影这 7 点，最大差 0.00022 像素。这是几何投影复核，材质与灯光另看实景。参考 [Godot Camera3D](https://docs.godotengine.org/en/stable/classes/class_camera3d.html)。

打开 [project.godot](project/project.godot) 并运行 [review.tscn](project/review.tscn)。`1` 切回对照机位并隐藏人形。按 `2` 进入自由观察，左键拖动环绕，滚轮拉近拉远，`R` 切换人形。F、S、B 分别跳到正、右、背方向。人形脚底在地台标高 0.45 m，头顶高于脚底 1.80 m。人形仅用于尺度观察。

PowerShell 可用 [run_review.ps1](run_review.ps1) 的 `-Mode import` 导入，再用 `-Mode stills` 刷新截图，`-Mode video` 输出录像帧。

## 导入、逐项诊断与实景结果

- 第一轮保持初始方向光、环境与默认材质采样，拍下导入原图。看到檐影边缘锯齿、斜视标识较软，以及门框、窗框和设备槽局部偏亮的细缝。
- [关闭阴影的诊断图](previews/diagnostic-no-shadows.png)消除了檐影锯齿，亮细缝仍在。正面能经门框侧隙看到内侧颜色，背面主封板完整，只有原有板缝和裙板。故将门框、窗框和设备槽边缘优先记录为接缝或遮挡差异。素材版 v08 保留待下一轮决定。
- [有角直射光试拍](previews/diagnostic-soft-shadows.png)留下可见颗粒。最终采用无角距离方向光、固定柔化与较高阴影滤波，并调低主光、提高环境补光。硬锯齿显著减弱，地台和檐下仍有结构阴影。测试地面使用独立灰色材质。参考 [方向光](https://docs.godotengine.org/en/stable/classes/class_directionallight3d.html) 和 [阴影设置](https://docs.godotengine.org/en/stable/classes/class_projectsettings.html#class-projectsettings-property-rendering-lights-and-shadows-directional-shadow-soft-shadow-filter-quality)。
- 保持几何和贴图原始数据，单独比较[三线性](previews/diagnostic-trilinear-oblique.png)与[各向异性](previews/diagnostic-aniso-oblique.png)。各向异性使斜视时数字、橙红横条和檐口斜线更干净。最终在测试场景仅对有底色贴图的材质启用 4× 各向异性 mipmap 过滤。代表性运动帧里没有发现明显标识串色或周期性闪烁。极斜角下细接缝仍可出现单像素闪动，物体缩小时小部件随投影尺寸减弱。这些是当前镜头和录像样本的观察。参考 [Godot 过滤设置](https://docs.godotengine.org/en/stable/classes/class_projectsettings.html#class-projectsettings-property-rendering-textures-default-filters-anisotropic-filtering-level)。
- 同机位下，黄绿、灰白、炭灰、青灯和橙红保持可辨。Godot 的漆面与混凝土反光层次更平，暗窗更均匀。后续优先核查门框可见间隙以及窗、设备槽的暗遮挡，再给暗窗补一两层低对比的内部轮廓。当前实景足以评估基础色块与造型，表面变化可在有具体材质目标时另行验证。

## 规模与测试设置

| 项 | 实测 |
|---|---|
| Windows 引擎 | Godot 4.7.2.stable.steam.ed1daf0bf，NVIDIA GeForce RTX 3060 Ti，驱动 621.01，Vulkan 1.4.357，Forward+ |
| 采样 | 1280 × 853，MSAA 4×；TAA 与屏幕空间 AA 关闭；底色贴图有 mipmaps，最终各向异性 4× |
| 灯光 | 方向光 0.86，环境白色补光 0.59，阴影最大距离 48 m，固定柔化 2.5，偏移 0.10，法线偏移 1.0，分割混合开启，方向阴影贴图 4096，高质量滤波，32 位深度选项 |
| 色调 | 线性色调映射，曝光倍数 1.0，自动曝光、泛光、雾和景深关闭 |
| 资产 | 96 个网格实例，10,573 个 LOD0 三角形，16 个材质，4 张 1024 × 1024 sRGB 底色图。GLB 索引三角形数和 Godot 运行结果一致 |
| 着色数据 | 6 个贴图表面均有 UV0，4 张底色图均有 mipmaps；13,120 个顶点法线均为有限的近单位向量。三个发光材质正常读入。暗窗是 v08 的不透明玻璃表现 |

数据来自 [最终运行报告](reports/stills.json) 和 [录像运行报告](reports/video.json)。统计仅计建筑 GLB，排除了人形、地面和测试碰撞。没有运行性能基准。

## 碰撞

v08 的 GLB 导入时有 0 个碰撞形状。独立场景加入 29 个静态测试体，包括封闭建筑盒、试验地面和基于导入件的地台、踏面、货箱与屋檐凸形。实际射线验证 10 项均通过。三阶命中标高为 0.15／0.30／0.45 m，右地台为 0.45 m，货箱盖为 1.16 m；入口受到封闭建筑体阻挡，右墙、背墙和地台外区域也通过。击中位置和对象见 [最终运行报告](reports/stills.json)，代理代码见 [review_physics.gd](project/review_physics.gd)。

已查的其他项目控制器绑定了浮动移动或特定维度映射，本样板没有合用的独立步行控制器。**角色上下台阶及地台通行未测。** 封闭入口的静态代理和门叶实际显示分别记账。室内、真实透射、其他渲染器、碰撞整合及正式游戏性能待测。本轮停在 Godot 实景验收。
