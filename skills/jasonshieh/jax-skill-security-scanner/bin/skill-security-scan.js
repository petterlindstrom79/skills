#!/usr/bin/env node

/**
 * OpenClaw技能安全扫描命令行工具
 * 将JavaScript API封装为可执行命令
 */

const { SkillScanner, SecurityReporter } = require('../dist/index.js');
const path = require('path');
const fs = require('fs');

// 解析命令行参数
function parseArgs() {
  const args = process.argv.slice(2);
  const options = {
    scanPath: 'C:\\Users\\Administrator\\AppData\\Roaming\\npm\\node_modules\\openclaw-cn\\skills',
    outputFormat: 'text',
    help: false,
    version: false
  };

  for (let i = 0; i < args.length; i++) {
    const arg = args[i];
    
    if (arg === '--help' || arg === '-h') {
      options.help = true;
    } else if (arg === '--version' || arg === '-v') {
      options.version = true;
    } else if (arg === '--format' || arg === '-f') {
      if (i + 1 < args.length) {
        const format = args[++i];
        if (['text', 'json', 'markdown'].includes(format)) {
          options.outputFormat = format;
        } else {
          console.error(`错误：不支持的输出格式 "${format}"，支持：text, json, markdown`);
          process.exit(1);
        }
      }
    } else if (arg === '--scan-path' || arg === '-p') {
      if (i + 1 < args.length) {
        options.scanPath = args[++i];
      }
    } else if (arg.startsWith('--')) {
      console.error(`错误：未知选项 "${arg}"`);
      process.exit(1);
    } else {
      // 第一个非选项参数作为扫描路径
      if (!options.scanPathSet) {
        options.scanPath = arg;
        options.scanPathSet = true;
      }
    }
  }

  return options;
}

// 显示帮助信息
function showHelp() {
  console.log(`
OpenClaw技能安全扫描工具 v1.0.0

用法：
  skill-security-scan [选项] [扫描路径]

选项：
  -h, --help          显示帮助信息
  -v, --version       显示版本信息
  -f, --format <格式> 输出格式：text, json, markdown (默认: text)
  -p, --scan-path <路径> 要扫描的技能目录路径

示例：
  skill-security-scan
  skill-security-scan --format markdown
  skill-security-scan --format json
  skill-security-scan "C:\\path\\to\\skills"
  skill-security-scan --scan-path "C:\\path\\to\\skills" --format markdown

环境变量：
  OPENCLAW_SKILLS_PATH  默认技能目录路径
`);
}

// 显示版本信息
function showVersion() {
  const packageJson = JSON.parse(fs.readFileSync(path.join(__dirname, '..', 'package.json'), 'utf8'));
  console.log(`skill-security-scan v${packageJson.version}`);
}

// 主函数
async function main() {
  const options = parseArgs();

  if (options.help) {
    showHelp();
    return;
  }

  if (options.version) {
    showVersion();
    return;
  }

  try {
    console.log(`🚀 开始安全扫描...`);
    console.log(`📁 扫描目录: ${options.scanPath}`);
    console.log(`📝 输出格式: ${options.outputFormat}`);
    console.log('='.repeat(50));

    // 检查目录是否存在
    if (!fs.existsSync(options.scanPath)) {
      console.error(`❌ 错误：扫描目录不存在 "${options.scanPath}"`);
      process.exit(1);
    }

    // 创建扫描器
    const scanner = new SkillScanner(options.scanPath);
    
    // 运行扫描
    console.log('🔍 扫描技能目录...');
    const report = await scanner.scan();
    
    // 生成报告
    const reporter = new SecurityReporter(report);
    
    let output;
    switch (options.outputFormat) {
      case 'json':
        output = JSON.stringify(reporter.generateJsonReport(), null, 2);
        break;
      case 'markdown':
        output = reporter.generateMarkdownReport();
        break;
      case 'text':
      default:
        output = reporter.generateTextReport();
        break;
    }

    console.log(output);
    console.log('\n' + '='.repeat(50));
    console.log('✅ 扫描完成！');

  } catch (error) {
    console.error('❌ 扫描失败：', error.message);
    if (error.stack) {
      console.error('堆栈跟踪：', error.stack);
    }
    process.exit(1);
  }
}

// 执行主函数
if (require.main === module) {
  main().catch(error => {
    console.error('❌ 未处理的错误：', error);
    process.exit(1);
  });
}

module.exports = { parseArgs, showHelp, showVersion };