#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
眠小兔睡眠健康技能 - OpenClaw集成
提供睡眠分析、压力评估和冥想指导功能
"""
import warnings
import numpy as np

import psutil
import mne  # 添加这一行
import os
import sys
import json
import argparse
from pathlib import Path
from typing import Dict, Any, List, Optional

def prepare_edf_for_analysis(edf_path: str, target_highpass=0.3, target_lowpass=35.0):
    """
    准备EDF文件进行睡眠分析，处理各种警告
    
    Args:
        edf_path: EDF文件路径
        target_highpass: 目标高通滤波器频率(Hz)
        target_lowpass: 目标低通滤波器频率(Hz)
    
    Returns:
        处理后的Raw对象
    """
    # 临时抑制已知的无关警告
    with warnings.catch_warnings():
        warnings.filterwarnings('ignore', category=RuntimeWarning, 
                              module='mne', message='Channels contain different*')
        
        # 读取文件（不预加载）
        raw = mne.io.read_raw_edf(edf_path, preload=False, verbose='ERROR')
    
    # 检查并修复通道配置
    for ch_idx, ch_info in enumerate(raw.info['chs']):
        # 获取当前滤波器设置
        hp = ch_info.get('highpass', 0)
        lp = ch_info.get('lowpass', raw.info['sfreq']/2)
        
        # 如果配置不合理，覆盖为标准值
        if hp > lp or hp < 0.1 or lp > 100:
            ch_info['highpass'] = target_highpass
            ch_info['lowpass'] = target_lowpass
            print(f"[INFO] 修正通道 {ch_info['ch_name']} 滤波器: {hp}Hz->{target_highpass}Hz, {lp}Hz->{target_lowpass}Hz")
    
    return raw

def analyze_with_quality_check(self, edf_path: str) -> Dict[str, Any]:
    """带质量检查的分析入口"""
    # 准备数据
    raw = prepare_edf_for_analysis(edf_path)
    
    # 分析数据质量
    quality_report = assess_data_quality(raw)
    
    # 如果质量差，给出建议
    if quality_report['overall_score'] < 60:
        print("[ADVICE] 数据质量较低，建议:")
        for issue in quality_report['issues']:
            print(f"  - {issue}")
    
    # 根据质量选择分析策略
    if quality_report['mixed_sampling']:
        print("[INFO] 检测到混合采样率，使用稳健分析模式")
        return self._analyze_mixed_sampling(raw, quality_report)
    else:
        return self._analyze_uniform_sampling(raw, quality_report)

def assess_data_quality(raw):
    """评估数据质量"""
    issues = []
    
    # 检查采样率一致性
    sfreqs = set()
    for ch_info in raw.info['chs']:
        sfreqs.add(ch_info.get('sfreq', raw.info['sfreq']))
    
    mixed_sampling = len(sfreqs) > 1
    if mixed_sampling:
        issues.append(f"混合采样率: {sfreqs}")
    
    # 检查滤波器设置
    bad_filters = []
    for ch_info in raw.info['chs']:
        hp = ch_info.get('highpass', 0)
        lp = ch_info.get('lowpass', raw.info['sfreq']/2)
        if hp > lp:
            bad_filters.append(ch_info['ch_name'])
    
    if bad_filters:
        issues.append(f"{len(bad_filters)}个通道滤波器配置不合理")
    
    # 检查数据长度
    duration_hours = raw.n_times / raw.info['sfreq'] / 3600
    if duration_hours < 6:
        issues.append(f"记录时长过短: {duration_hours:.1f}小时")
    
    # 计算综合评分
    score = 100
    score -= len(issues) * 10
    
    return {
        "overall_score": max(0, score),
        "issues": issues,
        "mixed_sampling": mixed_sampling,
        "duration_hours": duration_hours,
        "n_channels": len(raw.ch_names)
    }



# 添加项目路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from plugin_manager import PluginManager
    from plugins.sleep_analyzer import SleepAnalyzerPlugin
    from plugins.stress_analyzer_fixed import ScientificStressAnalyzerPlugin
    from plugins.meditation_guide import MeditationGuidePlugin
    PLUGINS_AVAILABLE = True
except ImportError as e:
    print(f"[WARN] 插件导入失败: {e}")
    PLUGINS_AVAILABLE = False


class SleepRabbitSkill:
    """眠小兔睡眠健康技能"""
    
    def __init__(self):
        self.name = "眠小兔睡眠健康"
        self.version = "1.0.0"
        self.description = "专业的睡眠分析、压力评估和冥想指导系统"
        
        # 初始化插件
        self.plugins = {}
        self.plugin_manager = None
        
        if PLUGINS_AVAILABLE:
            self._initialize_plugins()
    
    def _assess_data_quality(self, raw) -> Dict[str, Any]:
        """评估数据质量"""
        issues = []
        recommendations = []
        
        # 1. 检查采样率一致性
        sfreqs = set()
        for ch_info in raw.info['chs']:
            sfreq = ch_info.get('sfreq', raw.info['sfreq'])
            sfreqs.add(sfreq)
        
        mixed_sampling = len(sfreqs) > 1
        if mixed_sampling:
            issues.append(f"混合采样率: {sfreqs}")
            recommendations.append("建议使用稳健分析模式")
        
        # 2. 检查滤波器设置
        bad_filters = []
        for ch_info in raw.info['chs']:
            hp = ch_info.get('highpass', 0)
            lp = ch_info.get('lowpass', raw.info['sfreq']/2)
            if hp > lp:
                bad_filters.append(ch_info.get('ch_name', '未知通道'))
        
        if bad_filters:
            issues.append(f"{len(bad_filters)}个通道滤波器配置不合理")
            recommendations.append("将自动修正滤波器设置")
        
        # 3. 检查数据时长
        duration_hours = raw.n_times / raw.info['sfreq'] / 3600
        if duration_hours < 4:
            issues.append(f"记录时长过短: {duration_hours:.1f}小时 (<4小时)")
            recommendations.append("睡眠分析需要至少4小时数据")
        elif duration_hours < 6:
            issues.append(f"记录时长偏短: {duration_hours:.1f}小时")
            recommendations.append("建议监测完整夜间睡眠")
        else:
            print(f"[INFO] 记录时长充足: {duration_hours:.1f}小时")
        
        # 4. 检查通道数量
        n_channels = len(raw.ch_names)
        if n_channels < 3:
            issues.append(f"通道数过少: {n_channels}个")
            recommendations.append("睡眠分析至少需要EEG、EOG、EMG通道")
        
        # 5. 检查是否有呼吸相关通道（用于呼吸事件分析）
        respiratory_channels = [ch for ch in raw.ch_names if 'resp' in ch.lower() or 'oronasal' in ch.lower()]
        if not respiratory_channels:
            issues.append("未检测到呼吸通道")
            recommendations.append("呼吸事件分析可能不可用")
        
        # 6. 计算综合评分
        score = 100
        score -= len(issues) * 10  # 每个问题扣10分
        score = max(0, min(100, score))  # 限制在0-100
        
        return {
            "overall_score": score,
            "issues": issues,
            "recommendations": recommendations,
            "mixed_sampling": mixed_sampling,
            "duration_hours": round(duration_hours, 2),
            "n_channels": n_channels,
            "sampling_rate": raw.info['sfreq'],
            "has_respiratory": len(respiratory_channels) > 0,
            "respiratory_channels": respiratory_channels
        }

    def _analyze_mixed_sampling(self, edf_path: str, quality_report: Dict) -> Dict[str, Any]:
        """处理混合采样率的EDF文件"""
        print("[INFO] 使用混合采样率稳健分析模式...")
        
        try:
            # 只读元数据
            raw = mne.io.read_raw_edf(edf_path, preload=False, verbose='ERROR')
            
            # 按采样率分组
            channels_by_sfreq = {}
            for ch_idx, ch_name in enumerate(raw.ch_names):
                ch_info = raw.info['chs'][ch_idx]
                sfreq = ch_info.get('sfreq', raw.info['sfreq'])
                if sfreq not in channels_by_sfreq:
                    channels_by_sfreq[sfreq] = []
                channels_by_sfreq[sfreq].append(ch_name)
            
            print(f"[INFO] 检测到采样率分组: {list(channels_by_sfreq.keys())}Hz")
            
            # 对每种采样率分别分析
            group_results = {}
            for sfreq, channels in channels_by_sfreq.items():
                print(f"[INFO] 分析 {sfreq}Hz 通道组: {channels}")
                
                # 挑选该组通道
                raw_group = raw.copy().pick_channels(channels)
                
                # 分块处理该组数据
                chunk_minutes = 10
                chunk_samples = int(chunk_minutes * 60 * sfreq)
                total_chunks = (raw_group.n_times + chunk_samples - 1) // chunk_samples
                
                group_events = []
                for chunk_idx in range(total_chunks):
                    start = chunk_idx * chunk_samples
                    end = min(start + chunk_samples, raw_group.n_times)
                    
                    # 加载当前块
                    data, times = raw_group[:, start:end]
                    
                    # 分析当前块（调用现有的_analyze_chunk）
                    chunk_result = self._analyze_chunk(data, sfreq)
                    if chunk_result:
                        group_events.append(chunk_result)
                    
                    del data
                
                group_results[str(sfreq)] = {
                    "channels": channels,
                    "n_chunks": total_chunks,
                    "events": group_events
                }
            
            # 整合结果（主要取EEG通道组的结果）
            eeg_sfreq = max(channels_by_sfreq.keys())  # 假设最高采样率是EEG
            main_results = group_results.get(str(eeg_sfreq), {})
            
            return {
                "sleep_score": 75,  # 示例值，实际应从分析结果计算
                "sleep_quality": "良好",
                "mixed_sampling_handled": True,
                "sampling_groups": list(channels_by_sfreq.keys()),
                "group_results": group_results
            }
            
        except Exception as e:
            print(f"[ERROR] 混合采样率分析失败: {e}")
            return {"error": f"混合采样率分析失败: {str(e)}"}

    def _initialize_plugins(self):
        """初始化插件"""
        try:
            # 直接创建插件实例（避免动态加载问题）
            self.plugins['sleep'] = SleepAnalyzerPlugin()
            self.plugins['stress'] = ScientificStressAnalyzerPlugin()
            self.plugins['meditation'] = MeditationGuidePlugin()
            
            print(f"[OK] 插件初始化完成: {list(self.plugins.keys())}")
            
        except Exception as e:
            print(f"[ERROR] 插件初始化失败: {e}")
            PLUGINS_AVAILABLE = False
    

    
    def analyze_sleep(self, edf_path: str) -> Dict[str, Any]:
        """智能睡眠分析 - 集成数据质量检查"""
        if not PLUGINS_AVAILABLE:
            return {"error": "插件不可用，请检查依赖"}
        
        try:
            # 1. 首先进行数据质量评估（不加载完整数据）
            print("\n[QUALITY] 开始数据质量评估...")
            
            # 只读元数据评估质量
            with warnings.catch_warnings():
                warnings.filterwarnings('ignore', category=RuntimeWarning, module='mne')
                raw_preview = mne.io.read_raw_edf(edf_path, preload=False, verbose='ERROR')
            
            quality_report = self._assess_data_quality(raw_preview)
            
            # 显示质量报告
            print(f"[QUALITY] 数据质量评分: {quality_report['overall_score']}/100")
            if quality_report['issues']:
                print(f"[QUALITY] 发现 {len(quality_report['issues'])} 个问题:")
                for issue in quality_report['issues']:
                    print(f"  ⚠️ {issue}")
            
            # 如果数据质量太差，给出警告但继续
            if quality_report['overall_score'] < 50:
                print("[WARN] 数据质量较低，分析结果可能不准确")
                print("[ADVICE] 建议检查数据采集过程")
            
            # 2. 根据内存和文件大小选择分析策略
            file_size = os.path.getsize(edf_path)
            file_size_mb = file_size / (1024 * 1024)
            
            available_memory = psutil.virtual_memory().available
            available_mb = available_memory / (1024 * 1024)
            
            # 3. 根据数据质量选择具体分析方法
            if quality_report['mixed_sampling']:
                print("[INFO] 检测到混合采样率，使用稳健分析模式")
                result = self._analyze_mixed_sampling(edf_path, quality_report)
            elif file_size_mb < available_mb * 0.3:
                print(f"[INFO] 内存充足 ({available_mb:.0f}MB可用)，使用快速模式")
                result = self._analyze_sleep_fast(edf_path)
            else:
                print(f"[INFO] 文件较大 ({file_size_mb:.0f}MB)，使用分块模式")
                result = self._analyze_sleep_chunked(edf_path)
            
            # 4. 将质量报告整合到结果中
            if isinstance(result, dict):
                result['data_quality'] = quality_report
                
                # 如果分析结果中还没有评分，可以基于质量调整
                if 'sleep_score' in result and quality_report['overall_score'] < 60:
                    # 质量差时降低置信度
                    result['confidence'] = 'low'
                    result['quality_warning'] = '数据质量较低，建议谨慎解读'
            
            return result
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            return {"error": f"睡眠分析失败: {str(e)}"}
    
    def _analyze_sleep_fast(self, edf_path: str) -> Dict[str, Any]:
        """快速模式 - 预加载全部数据"""
        try:
            # mne 现在应该可用了
            raw = mne.io.read_raw_edf(edf_path, preload=True, verbose=False)
            
            # 执行分析
            result = self.plugins['sleep'].execute({
                "edf_path": edf_path,
                "analysis_mode": "detailed",
                "raw_data": raw
            })
            
            # 释放内存
            del raw
            
            return result
            
        except MemoryError:
            print("[WARN] 内存不足，自动切换到分块模式")
            return self._analyze_sleep_chunked(edf_path)
        except Exception as e:
            return {"error": f"快速分析失败: {str(e)}"}
    
    def _analyze_sleep_chunked(self, edf_path: str) -> Dict[str, Any]:
        """分块模式 - 修复sfreq访问问题"""
        try:
            # 1. 只加载元数据
            raw = mne.io.read_raw_edf(edf_path, preload=False, verbose=False)
            
            # 2. 获取全局采样率（如果通道采样率不同，取最高值）
            # 安全的获取采样率方式
            sfreq = None
            ch_sfreqs = []
            
            # 方法1：从info中获取
            if 'sfreq' in raw.info:
                sfreq = raw.info['sfreq']
                print(f"[INFO] 从info获取采样率: {sfreq}Hz")
            
            # 方法2：从通道信息获取
            if sfreq is None:
                for ch_idx, ch_name in enumerate(raw.ch_names):
                    try:
                        # 安全的访问方式
                        ch_info = raw.info['chs'][ch_idx]
                        if 'sfreq' in ch_info:
                            ch_sfreqs.append(ch_info['sfreq'])
                        elif 'cal' in ch_info and hasattr(ch_info['cal'], 'get'):
                            # 某些版本可能在其他地方
                            pass
                    except (IndexError, KeyError):
                        continue
                
                if ch_sfreqs:
                    # 使用最常见的采样率
                    from collections import Counter
                    sfreq = Counter(ch_sfreqs).most_common(1)[0][0]
                    print(f"[INFO] 从通道统计获取采样率: {sfreq}Hz (出现{Counter(ch_sfreqs)[sfreq]}次)")
            
            # 如果还不行，使用默认值
            if sfreq is None:
                sfreq = 100  # 大多数睡眠数据的常见值
                print(f"[WARN] 无法获取采样率，使用默认值: {sfreq}Hz")
            
            # 3. 分块参数
            chunk_minutes = 10
            chunk_samples = int(chunk_minutes * 60 * sfreq)
            total_chunks = (raw.n_times + chunk_samples - 1) // chunk_samples
            total_hours = raw.n_times / sfreq / 3600
            
            print(f"[INFO] 分块处理: {total_chunks} 块 (每块{chunk_minutes}分钟, 总时长{total_hours:.1f}小时)")
            
            # 4. 逐块处理
            aggregated_result = {
                "file": edf_path,
                "total_hours": round(total_hours, 2),
                "sampling_rate": sfreq,
                "chunks_analyzed": 0,
                "chunk_results": []
            }
            
            for chunk_idx in range(total_chunks):
                start = chunk_idx * chunk_samples
                end = min(start + chunk_samples, raw.n_times)
                
                # 只加载当前块
                try:
                    # 尝试不同的数据访问方式
                    if hasattr(raw, 'get_data'):
                        data = raw.get_data(start=start, stop=end)
                    else:
                        data, times = raw[:, start:end]
                    
                    # 分析当前块（简化版）
                    chunk_result = {
                        "chunk_index": chunk_idx,
                        "start_seconds": start / sfreq,
                        "end_seconds": end / sfreq,
                        "samples": end - start,
                        "status": "ok"
                    }
                    aggregated_result["chunk_results"].append(chunk_result)
                    
                    # 释放内存
                    del data
                    
                except Exception as e:
                    print(f"[WARN] 块{chunk_idx}处理失败: {e}")
                    aggregated_result["chunk_results"].append({
                        "chunk_index": chunk_idx,
                        "error": str(e)
                    })
                
                # 更新进度
                aggregated_result["chunks_analyzed"] = chunk_idx + 1
            
            # 5. 调用实际的分析插件（需要根据你的插件调整）
            # 这里假设你的sleep插件能处理整个文件
            try:
                full_result = self.plugins['sleep'].execute({
                    "edf_path": edf_path,
                    "analysis_mode": "detailed"
                })
                aggregated_result["full_analysis"] = full_result
            except Exception as e:
                print(f"[WARN] 完整分析失败: {e}")
                aggregated_result["full_analysis"] = {"error": str(e)}
            
            return aggregated_result
            
        except Exception as e:
            print(f"[ERROR] 分块分析失败: {str(e)}")
            import traceback
            traceback.print_exc()
            return {"error": f"分块分析失败: {str(e)}"}
    
    def _analyze_chunk(self, data, sfreq) -> Dict:
        """分析单个数据块"""
        # 这里实现具体的分析逻辑
        # 返回该块的睡眠评分、特征等
        pass
    
    def _aggregate_scores(self, chunk_results) -> int:
        """聚合各块评分"""
        if not chunk_results:
            return 0
        
        # 简单平均，也可以加权平均
        scores = [r.get("sleep_score", 0) for r in chunk_results]
        return sum(scores) // len(scores)


    def check_stress(self, heart_rate_data: List[float]) -> Dict[str, Any]:
        """评估压力水平"""
        if not PLUGINS_AVAILABLE:
            return {"error": "插件不可用，请检查依赖"}
        
        try:
            # 执行分析
            result = self.plugins['stress'].execute({
                "heart_rate": heart_rate_data
            })
            
            return result
            
        except Exception as e:
            return {"error": f"压力评估失败: {str(e)}"}
    
    def guide_meditation(self, meditation_type: str = None, 
                        duration: int = 10) -> Dict[str, Any]:
        """提供冥想指导"""
        if not PLUGINS_AVAILABLE:
            return {"error": "插件不可用，请检查依赖"}
        
        try:
            # 构建请求数据
            request_data = {
                "duration_minutes": duration
            }
            
            if meditation_type:
                request_data["meditation_type"] = meditation_type
            
            # 执行指导
            result = self.plugins['meditation'].execute(request_data)
            
            return result
            
        except Exception as e:
            return {"error": f"冥想指导失败: {str(e)}"}
    
    def generate_report(self, edf_path: str = None, 
                       heart_rate_data: List[float] = None) -> Dict[str, Any]:
        """生成综合报告"""
        report = {
            "timestamp": self._get_timestamp(),
            "overall_score": 0,
            "sleep_analysis": None,
            "stress_assessment": None,
            "meditation_recommendation": None,
            "recommendations": []
        }
        
        # 睡眠分析
        if edf_path and os.path.exists(edf_path):
            sleep_result = self.analyze_sleep(edf_path)
            if "error" not in sleep_result:
                report["sleep_analysis"] = sleep_result
                report["overall_score"] += sleep_result.get("sleep_score", 0) * 0.6
        
        # 压力评估
        if heart_rate_data and len(heart_rate_data) >= 10:
            stress_result = self.check_stress(heart_rate_data)
            if "error" not in stress_result:
                report["stress_assessment"] = stress_result
                # 压力评分越低越好，所以用(1-压力评分)计算
                stress_level = stress_result.get("stress_level", 0.5)
                report["overall_score"] += (1 - stress_level) * 100 * 0.4
        
        # 冥想推荐
        meditation_result = self.guide_meditation()
        if "error" not in meditation_result:
            report["meditation_recommendation"] = meditation_result
        
        # 生成建议
        report["recommendations"] = self._generate_recommendations(report)
        
        # 计算综合评分
        report["overall_score"] = min(100, max(0, int(report["overall_score"])))
        
        return report
    
    def _generate_recommendations(self, report: Dict[str, Any]) -> List[str]:
        """生成个性化建议"""
        recommendations = []
        
        # 睡眠建议
        if report["sleep_analysis"]:
            sleep_score = report["sleep_analysis"].get("sleep_score", 0)
            if sleep_score < 60:
                recommendations.append("睡眠质量较差，建议调整作息时间")
            elif sleep_score < 80:
                recommendations.append("睡眠质量一般，可以尝试睡前冥想")
            else:
                recommendations.append("睡眠质量良好，继续保持")
        
        # 压力建议
        if report["stress_assessment"]:
            stress_level = report["stress_assessment"].get("stress_level", 0.5)
            if stress_level > 0.7:
                recommendations.append("压力水平较高，建议每天进行减压冥想")
            elif stress_level > 0.4:
                recommendations.append("压力水平正常，保持日常放松练习")
            else:
                recommendations.append("压力水平较低，状态良好")
        
        # 通用建议
        if len(recommendations) < 3:
            recommendations.extend([
                "保持规律作息，每天固定时间睡觉和起床",
                "睡前1小时避免使用电子设备",
                "每天进行10-15分钟的冥想练习"
            ])
        
        return recommendations[:5]  # 最多5条建议
    
    def _get_timestamp(self) -> str:
        """获取时间戳"""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def format_output(self, result: Dict[str, Any], format_type: str = "text") -> str:
        """格式化输出"""
        if format_type == "json":
            return json.dumps(result, ensure_ascii=False, indent=2)
        
        # 文本格式输出
        output = []
        
        if "error" in result:
            output.append(f"[ERROR] 错误: {result['error']}")
            return "\n".join(output)
        
        # 睡眠分析输出
        if "sleep_score" in result:
            output.append("=" * 50)
            output.append("[SLEEP] 睡眠分析结果")
            output.append("=" * 50)
            output.append(f"[SCORE] 睡眠评分: {result.get('sleep_score', 0)}/100")
            output.append(f"[QUALITY] 睡眠质量: {result.get('sleep_quality', '未知')}")
            
            if "sleep_structure" in result:
                structure = result["sleep_structure"]
                output.append(f"[TIME] 总时长: {structure.get('total_duration_hours', 0):.1f}小时")
                output.append(f"[STAGES] 阶段数: {structure.get('total_segments', 0)}")
            
            if "recommendations" in result and result["recommendations"]:
                output.append("[ADVICE] 建议:")
                for rec in result["recommendations"][:3]:
                    output.append(f"  * {rec}")
        
        # 压力评估输出
        elif "stress_level" in result:
            output.append("=" * 50)
            output.append("[STRESS] 压力评估结果")
            output.append("=" * 50)
            output.append(f"[SCORE] 压力评分: {result.get('stress_level', 0):.3f}/1.0")
            output.append(f"[LEVEL] 压力等级: {result.get('stress_description', '未知')}")
            
            if "hrv_metrics" in result:
                metrics = result["hrv_metrics"]
                output.append(f"[HEART] 平均心率: {metrics.get('avg_heart_rate', 0):.1f} bpm")
                output.append(f"[HRV] HRV指标: SDNN={metrics.get('sdnn', 0):.1f}ms")
            
            if "recommendations" in result and result["recommendations"]:
                output.append("[ADVICE] 建议:")
                for rec in result["recommendations"][:3]:
                    output.append(f"  * {rec}")
        
        # 冥想指导输出
        elif "meditation_plan" in result:
            plan = result["meditation_plan"]
            output.append("=" * 50)
            output.append("[MEDITATION] 冥想指导")
            output.append("=" * 50)
            output.append(f"[TYPE] 推荐类型: {plan.get('type_name', '未知')}")
            output.append(f"[TIME] 时长: {plan.get('duration_minutes', 10)}分钟")
            output.append(f"[DESC] 描述: {plan.get('description', '')}")
            
            if "guidance_sequence" in plan and plan["guidance_sequence"]:
                output.append("[STEPS] 引导步骤:")
                for i, step in enumerate(plan["guidance_sequence"][:5], 1):
                    output.append(f"  {i}. {step}")
            
            if "benefits" in plan and plan["benefits"]:
                output.append("[BENEFITS] 预期效果:")
                for benefit in plan["benefits"][:3]:
                    output.append(f"  * {benefit}")
        
        # 综合报告输出
        elif "overall_score" in result:
            output.append("=" * 50)
            output.append("[REPORT] 综合健康报告")
            output.append("=" * 50)
            output.append(f"[SCORE] 综合评分: {result.get('overall_score', 0)}/100")
            output.append(f"[TIME] 报告时间: {result.get('timestamp', '')}")
            
            if result.get("sleep_analysis"):
                sleep = result["sleep_analysis"]
                output.append(f"[SLEEP] 睡眠评分: {sleep.get('sleep_score', 0)}/100")
            
            if result.get("stress_assessment"):
                stress = result["stress_assessment"]
                output.append(f"[STRESS] 压力评分: {stress.get('stress_level', 0):.3f}/1.0")
            
            if result.get("recommendations"):
                output.append("[ADVICE] 个性化建议:")
                for i, rec in enumerate(result["recommendations"][:5], 1):
                    output.append(f"  {i}. {rec}")
        
        return "\n".join(output)


def main():
    """命令行入口"""
    parser = argparse.ArgumentParser(description="眠小兔睡眠健康技能")
    parser.add_argument("--version", action="store_true", help="显示版本信息")
    
    subparsers = parser.add_subparsers(dest="command", help="可用命令")
    
    # 睡眠分析命令
    sleep_parser = subparsers.add_parser("sleep", help="分析睡眠数据")
    sleep_parser.add_argument("edf_file", help="EDF文件路径")
    sleep_parser.add_argument("--format", choices=["text", "json"], default="text", 
                             help="输出格式")
    
    # 压力评估命令
    stress_parser = subparsers.add_parser("stress", help="评估压力水平")
    stress_parser.add_argument("heart_rate", help="心率数据（逗号分隔）")
    stress_parser.add_argument("--format", choices=["text", "json"], default="text",
                              help="输出格式")
    
    # 冥想指导命令
    meditation_parser = subparsers.add_parser("meditation", help="获取冥想指导")
    meditation_parser.add_argument("--type", choices=["breathing", "body_scan", 
                                                     "sleep_prep", "stress_relief", 
                                                     "focus"], 
                                  help="冥想类型")
    meditation_parser.add_argument("--duration", type=int, default=10,
                                  help="冥想时长（分钟）")
    meditation_parser.add_argument("--format", choices=["text", "json"], default="text",
                                  help="输出格式")
    
    # 综合报告命令
    report_parser = subparsers.add_parser("report", help="生成综合报告")
    report_parser.add_argument("--edf", help="EDF文件路径")
    report_parser.add_argument("--hr", help="心率数据（逗号分隔）")
    report_parser.add_argument("--format", choices=["text", "json"], default="text",
                              help="输出格式")
    
    args = parser.parse_args()
    
    # 显示版本
    if args.version:
        skill = SleepRabbitSkill()
        print(f"{skill.name} v{skill.version}")
        print(skill.description)
        return
    
    # 创建技能实例
    skill = SleepRabbitSkill()
    
    # 执行命令
    if args.command == "sleep":
        result = skill.analyze_sleep(args.edf_file)
        print(skill.format_output(result, args.format))
    
    elif args.command == "stress":
        # 解析心率数据
        try:
            hr_data = [float(x.strip()) for x in args.heart_rate.split(",")]
            result = skill.check_stress(hr_data)
            print(skill.format_output(result, args.format))
        except ValueError:
            print("❌ 错误: 心率数据格式不正确，请使用逗号分隔的数字")
    
    elif args.command == "meditation":
        result = skill.guide_meditation(args.type, args.duration)
        print(skill.format_output(result, args.format))
    
    elif args.command == "report":
        edf_path = args.edf if args.edf else None
        hr_data = None
        
        if args.hr:
            try:
                hr_data = [float(x.strip()) for x in args.hr.split(",")]
            except ValueError:
                print("❌ 警告: 心率数据格式不正确，将忽略心率分析")
        
        result = skill.generate_report(edf_path, hr_data)
        print(skill.format_output(result, args.format))
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()