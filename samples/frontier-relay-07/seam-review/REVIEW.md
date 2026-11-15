# Frontier Relay 07 · v09 接缝验收

上轮 Godot 导入通过，v08 视觉验收暂未通过。v09 已在原测试项目复测，等待接缝视觉验收。[同机位前后对比](previews/00-matched-before-after.jpg) · [正视、斜视及背面近景对比](previews/01-detail-before-after.jpg) · [7 秒环绕](previews/02-orbit-v09.mp4) · [环绕抽帧](previews/03-orbit-contact.png)

开工时核对了 [v08 源文件](../source/frontier-relay-07-materials-v08.blend)、[v08 GLB](../material-review/export-check/frontier-relay-07-v08.glb)、[原 Godot 项目](../godot-review/project/project.godot) 与 [上一轮验收记录](../godot-review/REVIEW.md)。v08 源与导出保留，前后 SHA-256 相同。[v09 Blender 源文件](../source/frontier-relay-07-seams-v09.blend) 和 [v09 GLB](exports/frontier-relay-07-v09.glb) 另存，默认场景现实例化 v09，运行 `seams-before` 可继续看原 v08。

## 根因与修复

| 位置 | v08 检查结果 | v09 源资产修复 |
|---|---|---|
| 门框 | 正视透过侧隙看到后墙、内侧窗和黄绿裙板。门洞返边止于 Blender Y = −2.225 m，门叶首面约 −2.202 m。两侧还各有约 5–6 cm 横向空隙。 | 从原返边延伸到门叶厚度内，做一圈共连顶点的内壁和搭入门叶约 28 mm 的止口。门叶和外框位置不变。正视和斜视只见连续深色门套。 |
| 窗框 | 内边与玻璃首面沿深度相隔约 2 mm，玻璃倒角使斜视下更容易看到后墙或其它颜色。不是单纯的玻璃高光。 | 延伸窗槽内返面至玻璃厚度内，沿轮廓搭接约 14 mm。细亮边退为深色接触线，保留原玻璃位置和材质。 |
| 设备槽 | 斜视可见浅色背景带。槽口内返以 X = 1.580 m 结束，背板前面在 X = 1.410 m，中间约 170 mm 没有侧壁。 | 将四周连续侧壁延至原背板厚度内，沿轮廓搭接约 16 mm。原背板、弯管及设备盒保留。正视和斜视均读成封闭暗槽。 |
| 背墙中央 | v08 射线先打到凸起的黑色缝条。排除缝条后仍命中完整的封闭后墙，属于正常结构分缝的表达问题。 | 删除凸条，在同一后墙切出约 18 mm 宽、12 mm 深的盲槽，使用原有炭灰。布尔后后墙仍是封闭体。正视留有较细的缝线，斜视能读到槽深。 |

后衬沿洞口真实厚度构造，三个原返边表面继续使用原材质，新增内壁和止口使用 v08 已有的 `Recess shadow` 材质。基线返边法线朝洞口内侧，v08/v09 GLB 材质的双面/剔除设置相同。v08 的穿视可在 Blender 网格射线复现，故没有修改全局法线、背面剔除、AO 或阴影设置。

[网格射线脚本](probe_seams.py)对门、窗、设备槽各发射 480 条测试射线，覆盖正视及 ±32°、±58°。排除先挡在前面的柱脚、面板和货箱后，v08 意外命中其它表面或落空的次数分别为 236、112、176，v09 在这些样本中均为零。原法线朝向核查、样本命中对象及后墙深度见 [v08 结果](reports/mesh-rays-before.json) 与 [v09 结果](reports/mesh-rays-after.json)。

## 导出及引擎复测

通过 MCP for Blender 2.2.9 在独立 Blender 5.2.4 LTS 会话从 v08 生成 v09。后台重开并导出新 GLB。同一个 Godot 4.7.2 Forward+ 测试场景在 1280 × 853 分别输出 v08/v09，核对固定相机矩阵、FOV、近景位姿、主灯矩阵、环境能量、曝光、滤波、抗锯齿和阴影参数一致。

二进制核对确认只改了三个内返网格和后墙，移除了原凸缝条。其余 91 个网格的位置、索引和法线数据相同。四个未编辑网格的导出 UV 有浮点舍入，最大差 4.77×10⁻⁷。16 个材质及四张贴图内容相同。资产由 96 网格、10,573 三角形变为 95 网格、10,577 三角形。Godot 实测两版均通过原有 10 项静态碰撞射线检查。[资产记录与 SHA-256](reports/asset-v09.json) · [v08 Godot 记录](reports/seams-before.json) · [v09 Godot 记录](reports/seams-after.json)

已逐张查看 Godot 前后近景、背墙对比及环绕抽帧。视频为 168 帧、24 fps、7 秒，编码后完整解码通过。采样近景和环绕中，四处目标没有再出现原有背景色透出。在极斜角仍可见装配板缝，包括窗墙与服务面板分界以及建筑外角。预留的材质差异、暗窗本身的层次、其它板件接缝的极近观察和正式游戏中的通行仍待后续，当前成果只申请接缝验收。

## 关键文件

- [.blend v09](../source/frontier-relay-07-seams-v09.blend) · [GLB v09](exports/frontier-relay-07-v09.glb) · [测试场景](../godot-review/project/review.tscn)
- [Blender 修复脚本](repair_seams.py) · [导出脚本](export_v09.py) · [复核脚本](verify_revision.py)
- 图像原件位于 `previews/before/` 和 `previews/after/`。运行 `../godot-review/run_review.ps1 -Mode seams-before` 与 `-Mode seams-after` 可重新截图，后者同时写出环绕帧。用 FFmpeg 按 24 fps 编码这些帧，底部补一行像素以满足 YUV420。
- [本地检查点与文件保留规则](../../../VERSION_CONTROL.md)。预览、录像及运行日志保存在本机路径，源码、资产与可复查记录入库。
