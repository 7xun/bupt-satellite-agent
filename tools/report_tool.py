"""
卫星报告工具。
"""
import os
from langchain_core.tools import tool
from config import ANNUAL_REPORT_PATH


@tool
def get_satellite_status_report(question: str) -> str:
    """获取卫星状态报告的路径。"""
    q = (question or "").strip()
    if "年度" in q and os.path.exists(ANNUAL_REPORT_PATH):
        return ANNUAL_REPORT_PATH
    return "未找到匹配的报告 (目前仅支持: '年度报告')。"
