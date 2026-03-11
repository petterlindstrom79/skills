# OpenClaw 技能安全扫描插件

一个用于扫描OpenClaw技能目录的安全插件，提供敏感操作检测和木马/后门检测功能。

## 功能特性

### 🔍 敏感操作检测
- 扫描SKILL.md文件中的敏感关键词
- 检查package.json中的危险脚本
- 分析JavaScript/TypeScript代码文件
- 自动评估风险等级（高/中/低）

### 🦠 木马/后门检测
- 网络通信后门检测（net, http, ws, socket.io等）
- 文件系统恶意操作检测（fs模块危险函数）
- 进程控制系统检测（child_process, exec, spawn等）
- 数据外传加密检测（crypto, Buffer, base64编码）
- 代码混淆隐藏检测（eval, Function构造器等）
- 高风险组合模式识别

### 📊 报告生成
- 文本格式报告
- Markdown格式报告
- JSON格式报告
- 风险统计摘要
- 木马检测摘要
- 安全建议

## 安装

### 作为OpenClaw插件安装

```bash
# 从npm安装
openclaw-cn plugins add @openclaw-cn/skill-security-scanner

# 或从本地路径安装
openclaw-cn plugins add ./extensions/skill-security-scanner
```

### 作为独立npm包安装

```bash
npm install @openclaw-cn/skill-security-scanner
```

## 使用方法

### 通过命令行工具使用（推荐）

插件现在提供了独立的命令行工具 `skill-security-scan`：

```bash
# 安装后全局可用
skill-security-scan

# 指定输出格式
skill-security-scan --format markdown
skill-security-scan --format json
skill-security-scan --format text

# 指定扫描路径
skill-security-scan --scan-path /path/to/skills
skill-security-scan "C:\\path\\to\\skills"

# 查看帮助
skill-security-scan --help

# 查看版本
skill-security-scan --version
```

### 通过OpenClaw工具使用

```bash
# 运行安全扫描（如果CLI命令已注册）
openclaw-cn skill-security-scan --format markdown

# 指定扫描路径
openclaw-cn skill-security-scan --scan-path /path/to/skills --format json

# 查看帮助
openclaw-cn skill-security-scan --help
```

### 通过API使用

```javascript
const { SkillScanner, SecurityReporter } = require('@openclaw-cn/skill-security-scanner');

// 创建扫描器
const scanner = new SkillScanner('/path/to/skills');

// 运行扫描
const report = await scanner.scan();

// 生成报告
const reporter = new SecurityReporter(report);
const markdownReport = reporter.generateMarkdownReport();
console.log(markdownReport);
```

## 配置

在OpenClaw配置文件中添加：

```yaml
plugins:
  entries:
    skill-security-scanner:
      config:
        scanPath: "/path/to/skills"
        sensitiveKeywords:
          - "exec"
          - "shell"
          - "rm"
          - "delete"
          - "format"
```

## 报告示例

### 风险统计
```
📊 风险统计:
  🔴 高风险: 2
  🟡 中风险: 48
  🟢 低风险: 2
```

### 木马检测摘要
```
🦠 木马检测摘要:
  检测技能: 52/52
  高风险: 0
  中风险: 0
  可疑文件: 0个
```

### 安全建议
```
💡 安全建议:
1. 立即审查高风险技能
2. 定期审查中风险技能
3. 提高文档覆盖率
4. 限制敏感操作的使用
5. 定期更新依赖
6. 实施代码审查流程
7. 使用沙盒环境
8. 建立技能白名单
9. 监控技能行为
10. 定期进行安全扫描
```

## 开发

### 构建

```bash
# 安装依赖
npm install

# 构建插件
npm run build

# 清理构建产物
npm run clean
```

### 测试

```bash
# 运行测试
npm test

# 运行扫描测试
node test-scan.js
```

## 许可证

MIT

## 贡献

欢迎提交Issue和Pull Request！

## 支持

- GitHub Issues: https://github.com/openclaw/openclaw-cn/issues
- 文档: https://docs.openclaw.ai