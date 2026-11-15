# 前哨小站 07 · 标识与基础材质验收

本轮已保存 [v08 可编辑源文件](../source/frontier-relay-07-materials-v08.blend)，状态为待用户验收。[v06 形体基线](../source/frontier-relay-07-shape-v06.blend)的 SHA-256 为 `5d448f3bba603a28e9c95989e1d685bc96b666367b6e274b23280d1015b85848`，执行前后相同。开工时已核实 [上轮记录](../shape-review/REVIEW.md)、[机位设置](../shape-review/shape-settings.json)、[原修形脚本](../shape-review/refine_shapes.py) 和参考图。工作流 Git 分支为 `main`，尚无提交。

[三版同机位对比](previews/00-comparison.jpg) · [v06](previews/01-v06.png) · [v07 仅标识](previews/02-markings.png) · [v08 标识与基础材质](previews/03-materials.png)

三张均由各自的 .blend 重新打开并渲染，分辨率 1280 × 853。相机世界矩阵、109 mm 焦距、两盏灯的矩阵和能量、环境光与 +0.2 EV 曝光核对相同，色彩管理均为 Khronos PBR Neutral。详见 [渲染核对](render-verification.json)。

## 檐下局部

三张 [v06 原近景](diagnostics/v06-eave.png)、[隐藏托肋](diagnostics/v06-eave-without-carriers.png)、[只看主体截面及灯具](diagnostics/v06-eave-core.png) 使用相同镜头与光照。主转角的明暗折痕在主体近景仍在，符合相邻切面的方向变化。两道额外小斜线随托肋隐藏消失。求值后的网格相交检查还显示，两根托肋分别与相邻底板边缘相交，每对有 17 个三角面相交对。

v08 只收窄两根托肋伸入接缝的边缘。四对托肋与相邻底板的三角面相交对由 17 降为 0，托肋与承托核心的安装接触保留。已有主切面、分缝及主体法线设置均沿用。见 [v08 近景](diagnostics/v08-eave.png) 与 [v06 网格诊断](diagnostics/eave-analysis.json)。

## 标识与材质

“07”按附图手绘成切角数字，三条橙红横线与数字同时放在长窗以下。其余标识是檐口三条斜纹、左柱两条深色斜纹及三级台阶两侧的连续标线。试拍后拉开数字和窗框的间距，拆开柱上相粘的两条斜纹，并将檐口斜纹向参考位置移近。

标识通过原网格的 UV0 和四张不透明 sRGB 底色 PNG 实现，直接输入 Principled BSDF 的 Base Color。它们随原表面走向穿过檐口折面和台阶立面，避免叠一层共面网格。PNG 在 .blend 中打包，也保留独立源文件。图形尺寸、位置和色板在 [贴图生成脚本](paint_maps.py) 中可编辑。

| 表面 | v08 材质 |
|---|---|
| 灰白与黄绿烤漆 | 外层为非金属涂膜，金属度 0，粗糙度 0.39 和 0.43 |
| 深色门框、基座与护角 | 炭灰粗糙度 0.60，门板与内凹面另有较暗的独立材质 |
| 地台与三级台阶 | 高粗糙度 0.89 的灰色混凝土，标线随踏面和立面变化 |
| 横窗 | 粗糙度 0.19 的深蓝灰不透明介电表面，用暗色与反射表达烟熏玻璃 |
| 灯具 | 门侧青灯、檐下白灯与红位置灯各自发光，使用基础发光色与强度 |

黄绿涂膜的 sRGB 基础色由约 `#cfe80b` 调到 `#aebc25`。分析结合了底色、固定曝光与色彩管理下的实际渲染。柱中段无标识的代表区域，参考 RGB 中位数约 (173,185,25)，v06 为 (212,239,34)，v08 为 (183,199,24)。这是不同图像上的近似取样，不是对参考材质反射率的测量。最终仍可在柱面读出阴影、侧边和斜肩高光。见 [取样记录](color-check.json)。

结构细节限于门把手、右墙与屋顶的主分缝、侧槽内两根弯管。主分缝采用已有几何缝及少量贴图线。侧槽弯管以网格替代原先的占位直块。

## 导出实测

用 Blender 5.2.4 LTS 从保存文件导出 [独立验收 GLB](export-check/frontier-relay-07-v08.glb)。二进制包内有四张底色图，标识材质走不透明核心 PBR，未使用材质扩展。Godot 4.7.2 的无头 `GLTFDocument` 实测成功实例化 96 个网格，检查到四个标识材质均有底色图及 UV0，三种灯材质均有发光属性。见 [Godot 日志](export-check/godot-import.log) 和 [验证脚本](verify_godot_import.gd)。

已实测范围为导出、读取、实例化和材质属性。Godot 内的实际画面、项目灯光下的发光强度、碰撞和正式集成待测。窗采用不透明表现，本轮没有真透射测试。见 [Godot 格式说明](https://docs.godotengine.org/en/stable/tutorials/assets_pipeline/importing_3d_scenes/available_formats.html) 与 [glTF 2.0 材质规范](https://registry.khronos.org/glTF/specs/2.0/glTF-2.0.html)。

## 仍影响参考还原的三个差异

1. **横窗仍是一条较平的蓝黑色面。** 原图窗内能看到深浅层次和类似遮挡物的形状。下一轮可先在现有暗窗内加两三个很弱的暗层次，再决定要不要真实透射。
2. **屋顶机盒和右地台仍有形体差。** 黄色机盒比参考更宽，右后地台与货箱在画面里也较高。这是沿用已批准 v06 形体的结果。
3. **大片涂装和干混凝土仍较均一。** 已有不同粗糙度及清楚标识，参考仍有更细的覆层、倒角高光和材质颗粒。后续先做受控微表面，再评估局部使用痕迹。

## 可编辑文件

- [v07 标识检查点](../source/frontier-relay-07-markings-v07.blend) · [v08 成果](../source/frontier-relay-07-materials-v08.blend)
- [Blender 制作脚本](apply_materials.py) · [贴图脚本](paint_maps.py) · [三版渲染与 GLB 导出脚本](render_and_export.py)
- v08 底色 PNG：[侧墙](textures/finish/side-basecolor.png) · [屋檐](textures/finish/roof-basecolor.png) · [设备柱](textures/finish/column-basecolor.png) · [台阶](textures/finish/stairs-basecolor.png)

通过现有 MCP for Blender 2.2.9，在独立 GUI 实例中打开 v06、编辑并另存。随后用后台 Blender 重新打开各版本渲染并导出。三版图、最终单图和檐下诊断图均已查看。本轮停在干净材质验收。
