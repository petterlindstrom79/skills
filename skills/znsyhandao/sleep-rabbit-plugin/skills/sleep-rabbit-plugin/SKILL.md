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
