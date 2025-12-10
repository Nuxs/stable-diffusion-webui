# 用户使用指南

本指南帮助您快速上手 Stable Diffusion WebUI Desktop，并解决常见问题。

---

## 快速开始

### 1. 安装应用

1. 下载 `StableDiffusionDesktop.exe`
2. 双击运行
3. 跟随首次运行向导完成设置

### 2. 首次运行向导

**步骤 1: 系统检测**
- 应用会自动检测您的电脑配置
- 显示 GPU、显存、磁盘空间等信息

**步骤 2: 选择组件**
- **Python 环境**（必需）：
  - CPU 版本：2 GB（无 GPU 时）
  - CUDA 11.8：4 GB（推荐，适合大部分 NVIDIA GPU）
  - CUDA 12.1：4 GB（适合 RTX 40 系列）
- **AI 模型**（可选）：
  - Stable Diffusion 1.5：4.27 GB（推荐新手）
  - Stable Diffusion XL：6.94 GB（更高质量，需要 10GB 显存）

**步骤 3: 下载和安装**
- 后台自动下载组件
- 显示详细进度和速度
- 可以暂停或取消

**步骤 4: 完成**
- 自动启动主界面
- 开始使用！

---

## 主要功能

### 文生图（Text-to-Image）

1. 在顶部输入框输入**提示词**（Prompt）
   ```
   例如：a beautiful landscape, mountains, sunset, detailed, 4k
   ```

2. （可选）输入**负向提示词**（Negative Prompt）
   ```
   例如：blurry, low quality, distorted
   ```

3. 调整参数：
   - **采样步数**（Steps）：20-50（越高越精细但越慢）
   - **引导系数**（CFG Scale）：7-12（越高越符合提示词）
   - **分辨率**：512x512（默认）或其他尺寸

4. 点击**生成**按钮

5. 等待生成完成（首次加载模型需要时间）

### 图生图（Image-to-Image）

1. 切换到 **img2img** 标签
2. 上传参考图像
3. 输入提示词
4. 调整**重绘幅度**（Denoising Strength）：0-1
   - 0：完全保留原图
   - 1：完全重绘
5. 点击生成

### 模型管理

**查看已安装模型**：
- 主界面顶部下拉菜单

**下载新模型**：
1. 菜单 → 设置 → 模型管理
2. 浏览内置模型库
3. 选择模型 → 点击下载
4. 等待下载完成
5. 刷新模型列表

**手动添加模型**：
1. 从 [Civitai](https://civitai.com/) 或 [HuggingFace](https://huggingface.co/) 下载 `.safetensors` 文件
2. 将文件复制到 `data/models/Stable-diffusion/`
3. 重启应用或刷新模型列表

---

## 常见问题

### Q1: 首次运行卡在"下载中"

**可能原因**：
- 网络连接不稳定
- 服务器响应慢

**解决方案**：
1. 检查网络连接
2. 尝试使用 VPN（如果在国内）
3. 取消后重试（支持断点续传）

### Q2: 显示"显存不足"错误

**解决方案**：
1. 降低生成分辨率（512x512 或更小）
2. 减少批次数量（Batch size = 1）
3. 启用低显存模式：
   - 设置 → 优化 → 启用 `--lowvram` 或 `--medvram`
4. 关闭其他占用显存的程序

### Q3: 生成速度很慢

**原因分析**：
- **CPU 模式**：比 GPU 慢 10-50 倍
- **显卡性能不足**：老旧或低端 GPU

**优化建议**：
1. 降低采样步数（20 步）
2. 使用较小的分辨率
3. 选择速度较快的采样器（如 DPM++ 2M）
4. 升级到更强的 GPU

### Q4: 生成的图像质量不好

**优化技巧**：
1. **改进提示词**：
   - 添加质量关键词：`masterpiece, best quality, highly detailed`
   - 使用具体描述，避免模糊词汇
   - 参考优秀案例

2. **调整参数**：
   - 增加采样步数（30-50）
   - 调整 CFG Scale（7-12）
   - 尝试不同的采样器

3. **使用更好的模型**：
   - 下载专门的模型（如写实、动漫风格）
   - 尝试社区微调模型

### Q5: 应用无法启动

**检查清单**：
- [ ] 是否安装了 Visual C++ Redistributable？
   - 下载：https://aka.ms/vs/17/release/vc_redist.x64.exe
- [ ] 磁盘空间是否充足（至少 10 GB）？
- [ ] 防火墙是否阻止了应用？
- [ ] 查看日志文件：`logs/app.log`

### Q6: 如何更新应用？

1. 菜单 → 帮助 → 检查更新
2. 如有更新，点击下载
3. 关闭应用
4. 覆盖安装或运行更新程序

---

## 高级功能

### ControlNet（精确控制）

1. 启用 ControlNet 扩展（设置中）
2. 上传控制图像（边缘、深度图等）
3. 选择控制模型
4. 生成图像

### Lora（微调模型）

1. 下载 Lora 文件（`.safetensors`）
2. 放到 `data/models/Lora/`
3. 在提示词中使用：`<lora:filename:weight>`
   ```
   例如：a girl <lora:anime_style:0.8>
   ```

### Inpainting（局部重绘）

1. 切换到 **Inpaint** 标签
2. 上传图像
3. 使用画笔标记要重绘的区域
4. 输入提示词
5. 生成

---

## 提示词技巧

### 基础结构

```
[主体], [风格], [质量词], [细节描述], [艺术家/镜头]

例如：
a beautiful girl, anime style, masterpiece, best quality, 
detailed face, blue eyes, long hair, by makoto shinkai, 
cinematic lighting, 4k
```

### 常用质量词

**正向**：
- `masterpiece, best quality, highly detailed`
- `4k, 8k, ultra detailed`
- `professional, award winning`

**负向**：
- `low quality, blurry, distorted`
- `watermark, signature`
- `bad anatomy, deformed`

### 权重控制

```
(word)      # 提高权重 1.1x
((word))    # 提高权重 1.21x
[word]      # 降低权重 0.9x
(word:1.5)  # 精确控制权重
```

---

## 快捷键

| 功能 | 快捷键 |
|-----|--------|
| 重新加载页面 | `F5` |
| 在浏览器中打开 | `Ctrl+B` |
| 放大界面 | `Ctrl++` |
| 缩小界面 | `Ctrl+-` |
| 重置缩放 | `Ctrl+0` |
| 退出 | `Ctrl+Q` |

---

## 获取帮助

- **官方文档**：[README.md](README.md)
- **构建指南**：[BUILD_GUIDE.md](BUILD_GUIDE.md)
- **问题反馈**：[GitHub Issues](https://github.com/AUTOMATIC1111/stable-diffusion-webui/issues)
- **社区论坛**：[Reddit r/StableDiffusion](https://www.reddit.com/r/StableDiffusion/)

---

## 相关资源

- **模型下载**：
  - [Civitai](https://civitai.com/) - 社区模型库
  - [HuggingFace](https://huggingface.co/models) - 官方模型

- **学习资源**：
  - [PromptHero](https://prompthero.com/) - 提示词参考
  - [Lexica](https://lexica.art/) - AI 图像搜索

---

<div align="center">
享受创作！🎨
</div>

