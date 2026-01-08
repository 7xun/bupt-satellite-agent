"""
LSTM 异常检测工具。
"""
import os
import pandas as pd
from langchain_core.tools import tool
from config import OUTPUT_ROOT
from .lstm_impl import run_lstm_detection_and_plot


@tool
def run_lstm_ad() -> str:
    """运行 LSTM 异常检测模型。"""
    try:
        return f"检测完成。图表已生成至: {run_lstm_detection_and_plot()}"
    except Exception as e:
        return f"检测失败: {e}"


@tool
def analyze_lstm_results() -> str:
    """分析 LSTM 检测结果。"""
    csv_path = os.path.join(OUTPUT_ROOT, "lstm_ad_results.csv")
    if not os.path.exists(csv_path):
        return "未找到结果文件。请先运行检测。"
    
    try:
        df = pd.read_csv(csv_path)
        if df.empty or 'score' not in df.columns:
            return "结果数据无效。"
        
        stats = df['score'].describe()
        threshold = stats['mean'] + 3 * stats['std']
        anomalies = df[df['score'] > threshold]
        
        # 获取前 5 个异常点
        top5_str = ""
        if 'timestamp' in df.columns:
             top5 = df.nlargest(5, 'score')[['timestamp', 'score']]
             top5_str = top5.to_string(index=False, header=False)
        else:
             top5_str = "无时间戳列。"

        return (f"**LSTM 分析报告**\n"
                f"- 时间范围: {df['timestamp'].min() if 'timestamp' in df.columns else 'N/A'} ~ {df['timestamp'].max() if 'timestamp' in df.columns else 'N/A'}\n"
                f"- 分数统计: 均值 {stats['mean']:.4f}, 最大值 {stats['max']:.4f}\n"
                f"- 发现异常: {len(anomalies)} (阈值 > {threshold:.4f})\n"
                f"- Top 5 异常点:\n{top5_str}")
    except Exception as e:
        return f"分析失败: {e}"
