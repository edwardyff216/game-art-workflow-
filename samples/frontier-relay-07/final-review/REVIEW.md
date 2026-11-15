# Frontier Relay 07 · v10 最终样板

通用场景美术工作流 v1，已通过一个科幻硬表面建筑样板验证，最终视觉待用户确认。

- [原材质与细化材质同机位](evidence/01-material-comparison.jpg) · [台阶与货箱近景](evidence/02-near-stairs-crate.jpg)
- [正、侧、斜、背、远景](evidence/03-views.jpg) · [门窗、设备槽和背墙复查](evidence/04-seam-comparison.jpg) · [环绕抽帧](evidence/05-orbit-frames.jpg)
- 本机完整输出在 `D:\Game 仓库，一些点子\game-art-workflow\samples\frontier-relay-07\final-review\previews\v1`。[6 秒环绕录像](previews/v1/06-orbit.mp4) · [v10 主机位原图](previews/v1/previews/v10/matched.png)

## 版本关系和编辑路径

| 项目 | 文件及依赖 |
| --- | --- |
| 回退基线 | [v09 .blend](../source/frontier-relay-07-seams-v09.blend)、[v09 GLB](../seam-review/exports/frontier-relay-07-v09.glb)、[接缝记录](../seam-review/REVIEW.md)、[原 Godot 场景](../godot-review/project/review.tscn) |
| 最终可编辑源 | [frontier-relay-07-finish-v10.blend](../source/frontier-relay-07-finish-v10.blend)，在 v09 上细化，12 张使用中的图像已打包 |
| 最终导出 | [frontier-relay-07-v10.glb](../godot-review/project/assets/frontier-relay-07-v10.glb)，单一交付导出件，嵌入五张底色和七张粗糙度贴图 |
| 源贴图与生成 | [材质参数](finish.json)、[程序贴图生成](make_finish_maps.py)、[烘焙 PNG](textures/)、[Blender 编辑与导出脚本](build_finish.py)。楼梯标线取自 v08 完成版 [源 PNG](../material-review/textures/finish/stairs-basecolor.png) |
| 默认实景 | [project.godot](../godot-review/project/project.godot) 加载 [frontier_relay.tscn](../godot-review/project/frontier_relay.tscn)，直接实例化最终 GLB。Godot 提取的 PNG 与导入配置在 [assets](../godot-review/project/assets/) |
| 引擎环境依赖 | [照明 C](../godot-review/project/studio_c.gd)、[天空辐照着色器](../godot-review/project/lighting_review_sky.gdshader)、[机位](../godot-review/project/camera-reference.json) 和 [静态碰撞代理](../godot-review/project/review_physics.gd)。由 Godot 场景提供 |
| 运行与验收 | [run_final.ps1](run_final.ps1)、[实机截图脚本](../godot-review/project/final_capture.gd)、[导出和实机核验](verify_final.py)、[引擎报告](reports/engine-checks.json)、[导出报告](reports/export-checks.json)、[重建报告](reports/rebuild-checks.json) |

## 照明与观察范围

v09、v10 均使用 [照明实验 C](../lighting-review/REVIEW.md)。方向光能量 1.07，来源向量 (5.4, 8.4, 4.3) 指向原点，白色均匀补光 0.51，静态中性 Sky 提供环境反射，SSAO 关闭，Linear 色调映射与曝光 1.0。Godot 4.7.2.stable.steam.ed1daf0bf，Forward+ / Vulkan，RTX 3060 Ti，1280 × 853、4× MSAA、TAA 关闭。对照与 C 记录的运行参数一致。当前镜头为本样板的观察选择。

| 机位 | 距目标 | 垂直 FOV |
| --- | --- | --- |
| 原对照 | 原机位 (14.71342, 5.75619, 20.55872)，相机矩阵见 JSON | 12.5601° |
| 台阶、货箱近景 | 3.41 m、3.07 m | 44°、42° |
| 正、侧、背面 | 10.03 m、10.89 m、10.87 m | 38° |
| 右后中距、远景 | 12.77 m、22.80 m | 33.5°、40° |
| 环绕 | 9.2–21.2 m，360°，俯角约 11–23° | 40° |

## 材质取舍与看图结果

- **地台与台阶。** 以实物尺度生成偏中低频的色差和轻微粗糙度起伏。底色暗亮围绕原灰色，第一版看图后减弱大斑块。近景能区分混凝土与涂装，远景仍读成整洁的大面。新 UV 仅用于原先未展开的受影响部件，台阶原横向纹理坐标保留，纵向改为随踏面和立面展开。标线边缘连续，观察图中未见明显拉伸或密度跳变。
- **外壳和货箱。** 灰白、黄绿和标识沿用原底色，增加低频粗糙度约 0.34–0.49。区别主要体现在箱盖弧面、外壳掠射反光和与深色护角的对比，远看变化轻微。护角原粗糙度 0.60。混凝土粗糙度约 0.84–0.95。程序数据先生成 PNG，颜色为 sRGB、粗糙度为线性 G 通道，最终为标准 glTF 材质。本轮未使用凹凸图；导出 B 通道为常量，金属因子为零。
- **暗窗和接缝。** 原不透明烟熏窗仍随视角反射 C，能在斜视和正侧读到不同亮度。本轮以门和窗的正视、斜视、设备槽及背墙对照复查，连续内返和盲槽均保留。
- **移动和远景。** 远图上 `07`、橙红条及台阶标线仍可辨。查看整组环绕取样及窗侧的连续帧，没发现新增的明显颗粒闪烁。该结果限于本样板的已录制轨迹和设备。

## 边界与复现

- **技术通过。** Blender 5.2.4 LTS 独立进程复开 v10，12 张图像均打包。GLB 中 95 个网格的变换、位置、三角朝向与角法线核对通过，Godot 导入计数为 10,577 三角形、16 个材质，法线自查没有无效项。五张底色、七张粗糙度图具有 mipmap，线性 G 通道与各向异性过滤已核对。v09、v10 各通过 10 条静态碰撞射线，样板共 29 个碰撞体。
- **复现通过。** 以全新检出内容执行入口，重新生成 Godot 缓存、重做对比与碰撞并重建 GLB。重建的场景结构与嵌入图像一致；浮点顶点属性以绝对误差 `1e-6` 核验，二进制哈希可能因导出浮点差异而不同。运行方式见 [仓库 README](../../../README.md)。
- **视觉待用户确认。** 当前样板保留干净的科幻硬表面表现，背面为简化封闭外壳。用户可由同机位和近景决定最终视觉。样板的纹理、镜头和照明数值仅属于本资产。
- **未验证。** 角色通行、正式游戏集成、大场景性能、其他题材与美术风格、其他引擎或 Godot 渲染器、平台与角色动画。Windows 之外的启动脚本未验证。旧的最小技术方块用于单独验证工具连接。
