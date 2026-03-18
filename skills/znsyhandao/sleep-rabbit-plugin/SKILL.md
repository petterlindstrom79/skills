---
name: "🐰 眠小兔睡眠健康"
description: "专业的睡眠健康分析系统，提供睡眠质量分析、压力评估和个性化冥想指导"
version: "1.0.0"
author: "眠小兔睡眠实验室"
tags: ["睡眠", "健康", "冥想", "压力", "HRV"]
---

# 🐰 眠小兔睡眠健康

这是一个专业的睡眠健康分析系统，可以帮助用户分析睡眠质量、评估压力水平并提供个性化的冥想指导。

## 功能

### 1. 睡眠分析 (sleep-analyzer)
分析EDF睡眠文件，返回睡眠评分、睡眠结构和建议。

**参数：**
- `edf_file`: EDF文件的完整路径（必填）
- `analysis_mode`: 分析模式，可选 `basic` 或 `detailed`（默认 `detailed`）

**输出示例：**
睡眠评分: 92/100
睡眠质量: 优秀
建议:

保持规律作息

睡前1小时避免使用电子设备

text

### 2. 压力评估 (stress-checker)
评估压力水平，基于心率数据和HRV分析。

**参数：**
- `heart_rate`: 心率数据列表（可选，默认使用模拟数据）
- `hrv_analysis`: 是否进行HRV分析（默认 `true`）

**输出示例：**
压力评分: 0.32/1.0
压力等级: 低压力
建议:

保持良好状态

适当放松

text

### 3. 冥想指导 (meditation-guide)
提供个性化冥想指导。

**参数：**
- `meditation_type`: 冥想类型（breathing/body_scan/sleep_prep/stress_relief/focus）
- `duration_minutes`: 冥想时长（默认10分钟）

**输出示例：**
冥想类型: 睡前准备
时长: 10分钟
引导步骤:

舒适躺下

深呼吸3次

扫描身体...

text

## 使用示例

```bash
# 分析睡眠
/sleep-analyze D:\data\sleep.edf

# 评估压力
/stress-check 72,75,78,74,76

# 冥想指导
/meditation-guide --type sleep_prep --duration 15
注意事项
EDF文件必须是完整路径

心率数据至少需要10个点

确保已安装Python依赖：mne, numpy, scipy, psutil

## 安装方法

### 方式一：通过 ClawHub 安装（推荐）
```bash
# 安装 ClawHub CLI（如果还没装）
npm install -g clawhub

# 安装眠小兔技能
clawhub install sleep-rabbit-plugin

## 权限说明

本技能为了提供完整的睡眠分析功能，需要以下权限：

- **filesystem:read**：读取您提供的EDF文件进行分析
- **filesystem:write**：将分析生成的详细报告（JSON/文本格式）保存到您指定的输出目录
- **process:spawn**：调用本地已安装的Python解释器执行科学计算（依赖mne/numpy/scipy等专业库）

**安全承诺：**
- ✅ 所有文件操作仅限于您指定的路径
- ✅ 不收集、不上传任何个人数据
- ✅ 不联网（已移除network权限）
- ✅ 所有分析均在本地完成

## 输出文件说明

运行睡眠分析后，会在EDF文件所在目录创建 `respiratory_analysis/` 文件夹，包含：
- `respiratory_analysis_report.json`：完整的结构化分析数据
- `respiratory_analysis_summary.txt`：易读的文本报告

您可以根据需要删除这些文件，技能不会在其它地方写入数据。
