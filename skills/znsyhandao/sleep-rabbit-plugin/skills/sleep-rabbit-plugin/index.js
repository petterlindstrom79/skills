const { exec } = require('child_process');
const fs = require('fs');
const path = require('path');
const util = require('util');
const execPromise = util.promisify(exec);

/**
 * 眠小兔睡眠健康插件
 * 提供睡眠分析、压力评估和冥想指导工具
 */
class SleepRabbitPlugin {
  constructor(api) {
    this.api = api;
    this.name = 'sleep-rabbit-plugin';
    this.version = '1.0.0';
    
    // Python脚本路径
    this.pythonScript = path.join(__dirname, 'bin', 'openclaw_skill.py');
    
    // 注册工具
    this.registerTools();
  }

  /**
   * 注册所有工具
   */
  registerTools() {
    // 注册睡眠分析工具
    this.api.registerTool({
      name: 'sleep-analyzer',
      description: '分析EDF睡眠文件，返回睡眠评分、睡眠结构和建议',
      parameters: {
        type: 'object',
        properties: {
          edf_file: {
            type: 'string',
            description: 'EDF文件的完整路径'
          },
          analysis_mode: {
            type: 'string',
            enum: ['basic', 'detailed'],
            default: 'detailed',
            description: '分析模式：basic（基础）或 detailed（详细）'
          }
        },
        required: ['edf_file']
      },
      handler: this.handleSleepAnalysis.bind(this)
    });

    // 注册压力评估工具
    this.api.registerTool({
      name: 'stress-checker',
      description: '评估压力水平，基于心率数据和HRV分析',
      parameters: {
        type: 'object',
        properties: {
          heart_rate: {
            type: 'array',
            items: { type: 'number' },
            description: '心率数据列表（每分钟心跳数）'
          },
          hrv_analysis: {
            type: 'boolean',
            default: true,
            description: '是否进行HRV分析'
          }
        }
      },
      handler: this.handleStressCheck.bind(this)
    });

    // 注册冥想指导工具
    this.api.registerTool({
      name: 'meditation-guide',
      description: '提供个性化冥想指导',
      parameters: {
        type: 'object',
        properties: {
          meditation_type: {
            type: 'string',
            enum: ['breathing', 'body_scan', 'sleep_prep', 'stress_relief', 'focus'],
            description: '冥想类型'
          },
          duration_minutes: {
            type: 'integer',
            minimum: 5,
            maximum: 30,
            default: 10,
            description: '冥想时长（分钟）'
          }
        }
      },
      handler: this.handleMeditationGuide.bind(this)
    });

    console.log(`[${this.name}] 工具注册完成`);
  }

  /**
   * 处理睡眠分析请求
   */
  async handleSleepAnalysis(params, context) {
    try {
      const { edf_file, analysis_mode = 'detailed' } = params;
      
      // 验证文件存在
      if (!fs.existsSync(edf_file)) {
        return {
          error: true,
          message: `EDF文件不存在: ${edf_file}`
        };
      }

      // 验证文件扩展名
      if (!edf_file.toLowerCase().endsWith('.edf')) {
        return {
          error: true,
          message: '文件不是EDF格式'
        };
      }

      console.log(`[sleep-analyzer] 分析文件: ${edf_file}`);

      // 调用Python脚本
      const result = await this.runPythonScript('sleep', [
        `"${edf_file}"`,
        '--format', 'json'
      ]);

      return JSON.parse(result);

    } catch (error) {
      console.error('睡眠分析失败:', error);
      return {
        error: true,
        message: `睡眠分析失败: ${error.message}`
      };
    }
  }

  /**
   * 处理压力评估请求
   */
  async handleStressCheck(params, context) {
    try {
      const { heart_rate = [], hrv_analysis = true } = params;
      
      // 如果没有提供心率数据，使用模拟数据
      let hrData = heart_rate;
      if (hrData.length === 0) {
        hrData = [72, 75, 78, 74, 76, 73, 71, 70, 72, 74];
        console.log('[stress-checker] 使用默认心率数据');
      }

      // 调用Python脚本
      const result = await this.runPythonScript('stress', [
        hrData.join(','),
        '--format', 'json'
      ]);

      return JSON.parse(result);

    } catch (error) {
      console.error('压力评估失败:', error);
      return {
        error: true,
        message: `压力评估失败: ${error.message}`
      };
    }
  }

  /**
   * 处理冥想指导请求
   */
  async handleMeditationGuide(params, context) {
    try {
      const { meditation_type, duration_minutes = 10 } = params;
      
      // 构建参数
      const args = ['meditation'];
      if (meditation_type) {
        args.push('--type', meditation_type);
      }
      args.push('--duration', duration_minutes.toString());
      args.push('--format', 'json');

      // 调用Python脚本
      const result = await this.runPythonScript('meditation', args.slice(1));

      return JSON.parse(result);

    } catch (error) {
      console.error('冥想指导失败:', error);
      return {
        error: true,
        message: `冥想指导失败: ${error.message}`
      };
    }
  }

  /**
   * 运行Python脚本
   */
  async runPythonScript(command, args) {
    try {
      // 检查Python脚本是否存在
      if (!fs.existsSync(this.pythonScript)) {
        throw new Error(`Python脚本不存在: ${this.pythonScript}`);
      }

      // 构建命令
      const cmd = `python "${this.pythonScript}" ${command} ${args.join(' ')}`;
      
      console.log(`[exec] ${cmd}`);

      // 执行命令
      const { stdout, stderr } = await execPromise(cmd);

      if (stderr) {
        console.warn('Python stderr:', stderr);
      }

      return stdout;

    } catch (error) {
      console.error('执行Python脚本失败:', error);
      throw error;
    }
  }

  /**
   * 插件生命周期：启动
   */
  async onStart() {
    console.log(`[${this.name}] 插件启动`);
    
    // 检查Python依赖
    try {
      await execPromise('python -c "import mne, numpy, scipy"');
      console.log('[✓] Python依赖检查通过');
    } catch (error) {
      console.warn('[!] Python依赖缺失，请运行: pip install mne numpy scipy');
    }
  }

  /**
   * 插件生命周期：停止
   */
  async onStop() {
    console.log(`[${this.name}] 插件停止`);
  }
}

// 插件入口
module.exports = (api) => {
  return new SleepRabbitPlugin(api);
};
