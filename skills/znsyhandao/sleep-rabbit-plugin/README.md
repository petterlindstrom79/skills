# 🐰 眠小兔睡眠健康 - OpenClaw 技能

[![ClawHub](https://img.shields.io/badge/ClawHub-sleep--rabbit--plugin-blue)](https://clawhub.ai/skills/sleep-rabbit-plugin)
[![Version](https://img.shields.io/badge/version-1.0.0-green)]()

专业的睡眠健康分析系统，提供睡眠质量分析、压力评估和个性化冥想指导。

## ✨ 功能特点

- **睡眠分析**：分析EDF格式睡眠文件，生成睡眠评分和结构报告
- **压力评估**：基于HRV指标评估压力水平
- **冥想指导**：提供个性化冥想方案
- **智能内存管理**：自动根据文件大小选择分析策略
- **数据质量评估**：自动检测数据问题并给出建议

## 📦 安装方法

### 一键安装（推荐）
```bash
# 安装 ClawHub CLI（如果还没装）
npm install -g clawhub

# 安装眠小兔技能
clawhub install sleep-rabbit-plugin
使用 npx（无需全局安装）
bash
npx clawhub install sleep-rabbit-plugin
手动安装（开发者）
bash
git clone https://github.com/your-repo/sleep-rabbit-plugin.git
cd sleep-rabbit-plugin
clawhub link .
🚀 快速使用
分析睡眠文件
text
/sleep-analyze D:\data\SC4001E0-PSG.edf
输出示例：

text
睡眠评分: 92/100 ⭐ 优秀
睡眠质量: 优秀
监测时长: 22.08小时
建议:
  * 保持规律作息
  * 睡前1小时避免使用电子设备
评估压力水平
text
/stress-check 72,75,78,74,76,73,71,70,72,74
输出示例：

text
压力评分: 0.32/1.0
压力等级: 低压力
建议:
  * 保持良好状态
  * 适当放松
获取冥想指导
text
/meditation-guide --type sleep_prep --duration 15
📊 数据分析能力
功能描述输入格式
睡眠分析睡眠评分、结构、质量评估EDF文件
压力评估HRV分析、压力等级心率数据列表
冥想指导个性化冥想方案类型+时长
🛠️ 技术规格
兼容性：OpenClaw 2026.3.12+

依赖：Python 3.8+, mne, numpy, scipy, psutil

文件格式：EDF (European Data Format)

采样率：支持 100Hz-500Hz

📝 更新日志
v1.0.0 (2026-03-18)
🎉 首次发布

✅ 支持EDF睡眠分析

✅ 压力评估功能

✅ 冥想指导功能

✅ 智能内存管理

✅ 数据质量评估

🤝 贡献指南
欢迎提交 Issue 和 Pull Request！

📄 许可证
MIT © 眠小兔睡眠实验室

📞 联系我们
问题反馈：GitHub Issues

邮箱：support@sleep-rabbit.com

官网：https://sleep-rabbit.com
