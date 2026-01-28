"""
卫星报告工具。
"""
import os
from langchain_core.tools import tool
from config import REPORT_PATH, PROJECT_ROOT
from . import time_translate as tt
from oss import update_to_js
from .utils import log
from oss import pre_process as pre
import json
import datetime


@tool
def get_satellite_status_report(start_date: str|None, end_date: str|None = None, raw_indicators: list[str]|None = None, **kwargs) -> str:
    """
    更新报告
    参数：
    - start_date: 开始日期 (YYYY-MM-DD)
    - end_date: 结束日期 (YYYY-MM-DD)
    - raw_indicators: 参数列表
    返回报告的路径


    示例调用:
    1. get_satellite_status_report(start_date="2024-01-01", end_date="2024-01-31") 
    2. get_satellite_status_report(start_date="2024-01-01", end_date="2024-02-29", raw_indicators=['ZTMS021-整星状态','温度']) 
    """
    try:
        log(f"进入函数get_satellite_status_report\nstart_date: {start_date}\nend_date: {end_date}\nraw_indicators: {raw_indicators}")
        

        if(start_date is None or end_date is None):
            return "请提供明确的起止日期"

        if not(tt.is_valid_date(start_date) and tt.is_valid_date(end_date)):
            return "查询失败，输入的日期不存在，请使用 YYYY-MM-DD 格式"
        
        if(start_date>end_date): start_date,end_date = end_date,start_date
        if raw_indicators is None: raw_indicators=[]

        # 查找指标所在文件夹的十六进制编号
        # 如果需要更新，把这个 indicator_info.json 删了再运行一次
        indicator_info_path = os.path.join(PROJECT_ROOT,'oss','info','indicator_info.json')
        if not os.path.exists(indicator_info_path):
            execl_path = os.path.join(PROJECT_ROOT,'oss','info','子系统分类.xlsx')
            pre.extract_info_from_excel(excel_file=execl_path,output_file=indicator_info_path)
        indicators = []
        if(len(raw_indicators)>0):
            with open(indicator_info_path, 'r', encoding='utf-8') as f:
                mapping = json.load(f)
                for indicator, d in mapping.items():
                    t = d['type']
                    for x in raw_indicators:
                        if (x in indicator) or (t in x): 
                            indicators.append(indicator)
                            break
        
        log(f"查询：从{start_date}至{end_date}，\n原始指标: {raw_indicators},\n找到指标: {indicators}")
                

        update_to_js.update(indicators=indicators,start_date=start_date,end_date=end_date)
        log('update_to_js调用完毕')


        report_path = REPORT_PATH
        if(os.path.exists(report_path)):\
            return f"报告已准备就绪！\n\n报告所处路径： {report_path}（注意，你需要将这个地址输出，不需要生成链接）"
        else: 
            return "查询失败"
    except:
        import traceback
        log(f"error:\n{traceback.format_exc()}\n")
        return '报错了'
   
