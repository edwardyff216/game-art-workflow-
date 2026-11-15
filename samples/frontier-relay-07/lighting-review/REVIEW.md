# Frontier Relay 07 · v09 Godot 光照与环境验收

v09 接缝视觉已通过。本轮以原 Godot 场景做 A/B/C 光照对照，停在光照验收。建议以 **C（关闭 SSAO）** 作为待选照明基线。B 的主光使体块和投影更清楚，C 在相同主光下增加窗面反射并抬起少量深色构件的亮部。

- [同机位 A/B/C](previews/01-abc-matched.png) · [后侧斜视 A/B/C](previews/01-abc-oblique.png)
- [窗面原图近景](previews/02-window-reflection.png) · [C / C-AO 落地细节](previews/03-contact-ao.png)
- [门框、窗框、设备槽正视与斜视及背面 A/C](previews/04-seams-a-c.png)
- 原始 1280 × 853 PNG [A 主图](previews/A/matched.png) · [B 主图](previews/B/matched.png) · [C 主图](previews/C/matched.png) · [A 斜视](previews/A/oblique.png) · [B 斜视](previews/B/oblique.png) · [C 斜视](previews/C/oblique.png)

## 基线和实际生效的设置

开工时工作区干净，`main` 指向 `330fc62`。[v09 源文件](../source/frontier-relay-07-seams-v09.blend)、[导出 GLB](../seam-review/exports/frontier-relay-07-v09.glb)、[测试场景](../godot-review/project/review.tscn)、[接缝记录](../seam-review/REVIEW.md) 均存在。场景实例化的 [项目内 GLB](../godot-review/project/assets/frontier-relay-07-v09.glb) 与导出件 SHA-256 相同。本轮独立 `SceneTree` 脚本加载该场景并临时设置灯光，原场景、原脚本、项目设置和资产文件均保持原内容。A 主图与上轮 v09 主图逐像素相等。运行中各版仍为 95 个网格实例、10,577 个 LOD0 三角形、16 个材质、4 张 1024 × 1024 标识贴图。

A 的唯一主光为白色方向光，能量 0.86，光从 `(2.4, 6, 4)` 的方向射向原点。补光为均匀白色 `AMBIENT_SOURCE_COLOR`，能量 0.59，无入射方向。反射源属性为 `BG`，实际背景为纯色且没有 Sky、ReflectionProbe 或 SSR，因此没有可采样的方向性环境反射。SSAO、SSIL、SDFGI、雾、泛光和色彩调整关。色调映射 Linear，曝光 1.0，相机和世界均无覆盖用的 CameraAttributes。环境补光与 Sky 反射是分别指定的输入。[A 运行记录](reports/A.json) · [Godot Environment](https://docs.godotengine.org/en/stable/classes/class_environment.html)

各版使用 Godot 4.7.2.stable.steam.ed1daf0bf，Forward+ / Vulkan 1.4.357，NVIDIA GeForce RTX 3060 Ti（621.01）。SubViewport 1280 × 853，4× MSAA，TAA 关。方向光阴影 4096，项目过滤质量枚举 4，软化 2.5，角直径 0°，偏移 0.10，法线偏移 1.0，最大距离 48 m，开启分级混合。原背景 `#848487`、地面 `#747373` 及其粗糙度 0.94 沿用。主图使用原镜头 `(14.71342, 5.75619, 20.55872)`、垂直视场 12.560115°。斜视镜头为右后方 `(10.2, 3.1, -7.6)`，目标 `(0.15, 1.43, 0.10)`，垂直视场 33.5°。两镜头分别在全部版本中锁定。

## 版本参数

| 版本 | 主光方向向量，指向原点 | 主光 / 白色补光能量 | 环境反射 | 遮蔽 |
| --- | --- | --- | --- | --- |
| [A](reports/A.json) | (2.4, 6, 4) | 0.86 / 0.59 | BG，纯色背景且无 Sky | 关 |
| [B](reports/B.json) | (5.4, 8.4, 4.3) | 1.07 / 0.51 | 同 A | 关 |
| [C](reports/C.json) | 同 B | 1.07 / 0.51 | 静态中性 Sky，仅供镜面环境反射 | 关 |
| [C-AO](reports/C-AO.json) | 同 B | 1.07 / 0.51 | 同 C | SSAO 半径 0.55 m、强度 0.8、功率 1.2、细节 0.5、地平线阈值 0.06、锐度 0.98、直射光影响 0 |

C 使用 128 × 128 的辐照立方体面，Quality 滤波。天空着色器由灰阶上下半球渐变（线性 0.065–0.22）和两个世界空间宽光区（附加强度 0.64、0.45）组成，无外部贴图、时间输入或日盘。背景和均匀白色补光继续沿用 B。参数与方向见 [天空着色器](../godot-review/project/lighting_review_sky.gdshader) 和 [Godot Sky shader](https://docs.godotengine.org/en/stable/tutorials/shaders/shader_reference/sky_shader.html)。

## 看图结果

### 光照已经改善

- **体积和着地。** B 把主光偏向窗墙。左柱斜肩更明显，正面与窄侧面的明暗关系反转，檐下仍能读到横向支撑。主图台阶踏面与立面的 8 位 G 通道样本差值由约 19 增至 28。后侧斜视下，货箱脚和地台的投影更容易定位，主图正面脚边的接触变化较小。
- **材料响应和颜色。** C 使暗窗、设备槽弯管、屋檐深色构件和货箱护角更易分辨。B → C 窗面取样均值在主图从 RGB (28,45,55) 到 (49,59,67)，右后斜视从 (26,42,51) 到 (32,45,54)。窗面在主图更亮、更偏灰蓝，斜视仍是深蓝且保留一段柔和渐变。灰白大面保留层次，抽样的受光白墙与白屋顶均无纯白剪切。黄绿的受光面、侧面和檐影仍有区分，受光倒角和台阶标线最亮。
- **接触遮蔽与接缝。** C-AO 只略收紧台阶根部、货箱脚边和邻接缝。在主图和斜视中分别约 0.15% 和 0.84% 像素出现至少 4/255 的绝对亮度差，最大 6/255 和 8/255，近景未见宽黑边。这个提升对当前镜头很小，建议 C 默认关闭 SSAO。A/C 的门、窗、设备槽正视和斜视截图仍见连续的暗色内壁，背墙中央保持窄盲槽，没有发现背景色或黄绿穿帮重现。[像素检查](reports/image-checks.json)

### 需要回到材质或纹理的差异

- **暗窗深度。** 当前 GLB 的窗面是粗糙度 0.19 的不透明着色表面，无透射扩展。C 证明其镜面反射能随观察方向变化，主图仍近似一整片玻璃。若需玻璃内侧的层次，需要在下一轮显式制作玻璃或内部层；本轮只观察了固定角度的实际画面。
- **混凝土与涂层近看。** 台阶和地台由遮光和几何边线勾出体积，表面粗糙度约 0.89，近看仍为均匀色块。混凝土表面细节、同一白色或黄绿色涂层内的粗糙度变化，需要材质或纹理提供空间变化。现有净色大面已足够用于这轮照明选择。

## 复跑与文件

仓库路径为 `D:\Game 仓库，一些点子\game-art-workflow`，实验输出在 `samples/frontier-relay-07/lighting-review`。从仓库根目录运行以下命令。捕获复用现有 `tools.session.json` 下的 Godot 路径，可通过 `-Preset A|B|C|C-AO` 单独复跑任一照明版本。拼图及像素检查使用 Python 3.12 和 Pillow 12.3.0。

```powershell
./samples/frontier-relay-07/lighting-review/run_lighting_review.ps1
python ./samples/frontier-relay-07/lighting-review/make_comparisons.py
```

- [运行入口](run_lighting_review.ps1) · [Godot 场景加载与捕获](../godot-review/project/lighting_review.gd) · [对照图和像素核验](make_comparisons.py)
- 维持本轮范围到照明验收。材质修订、正式场景集成、性能测试和移动镜头的时间稳定性未执行。
