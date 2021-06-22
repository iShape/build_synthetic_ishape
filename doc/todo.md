# TODOs in Chinese
### Todo:
- 不变的, 需要设置项的放在 defaults(分辨率)
- 可能做 DR 变化的设置项由用户自己管理

### Done:
- docker 一键生成数据集
- 更好的文档
- ~~更新 download, 自动 sleep~~(可以直接下载了)
- 更新 iShape 网页
- 添加 lisense for both 2 repos
- 考虑集成生成 coco json RLE 版本
- 将 gen_utils 集成到 bpycv
- 基于 zcs 统一的参数管理和继承
- 能一键生成数据集
- 输入命令包含数量和路径
- [x] asset 和 代码分开, 并结构化
- 兼容 brainpp_yl
- 验证 random.seed 有效性
    - 在版本(2.83 vs 2.90)和硬件(sb2 vs bpp)都不一样的情况下, 生成了一致的图像
    - 但 md5sum 不一致


### Decision:
Q: `zcs` or `hpman`?  
A: 选 `zcs`, 因为:
- `zcs` 和 detectron2 的 `yacs` 有连贯性
- 此项目是工具性质的, 而非迭代性质, 应该选择集中管理 config

Q: `.blend` 怎么集成和管理?  
A: `bpy.ops.wm.open_mainfile(filepath="../a.blend")`

Q: 如何管理和分发 10GB 的 hdri?  
A: 两种方案
- 写死 hdri names, 并自动从 hdri haven 自动下载
- 打包进 docker/magnet/云服务
- 最后选择了打包进 docker

