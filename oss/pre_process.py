import pandas as pd
import json
import os
import oss2
from config import PROJECT_ROOT


def extract_info_from_excel(excel_file, output_file):
    """
    提取参数名到标识、类型的映射并保存为JSON
    """
    if not os.path.exists(excel_file):
        print(f"错误: 文件 '{excel_file}' 不存在！")
        return
    
    # 读取Excel文件
    excel_data = pd.ExcelFile(excel_file)
    
    # 创建映射字典：参数名 -> [hex_num标识, 类型]
    d = {}
    
    for sheet in excel_data.sheet_names:
        try:
            # 读取工作表
            df = pd.read_excel(excel_file, sheet_name=sheet, header=None)
            
            # B列和I列
            for _, row in df.iterrows():
                if len(row) > 8:  # 确保有I列
                    indicator = row[1]  # B列
                    hex_num = row[8]  # I列
                    
                    # 检查是否为有效数据
                    if (pd.notna(indicator) and pd.notna(hex_num) and 
                        indicator != '参数名称' and hex_num != '包标识'):
                        
                        indicator = str(indicator).strip()
                        hex_num = str(hex_num).strip()
                        
                        # 添加到映射
                        if indicator not in d: d[indicator] = {'hex_num':hex_num, 'type':sheet}
                            
        except Exception as e:
            print(f"error: {e}, when processing {sheet}")
    
    # 保存为JSON
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(d, f, ensure_ascii=False, indent=4)


