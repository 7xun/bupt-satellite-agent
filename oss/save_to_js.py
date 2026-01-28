# part-1, part-2, ... 把 dataframe 转为 js 的代码

import pandas as pd
import json
from config import PART_1_INDICATORS, PART_2_INDICATORS,PROJECT_ROOT
import os
p = os.path.join(PROJECT_ROOT,'log.txt')
def counting_js(df:pd.DataFrame, output_path:str):
    d={}
    for indi in PART_1_INDICATORS:
        d[indi] = 0
        for x in df[indi][0:]: d[indi]+=x # 第一行用于计算change，这里用不到

    with open(output_path,'w',encoding='utf-8') as f:
        f.write(f'part_1_data = {json.dumps(d,ensure_ascii=False,indent=4)};')




def changes_js(df:pd.DataFrame, info_path:str, js_path:str, file_name:str):
    """将DataFrame转换为JS格式"""
    if len(df.columns) == 1:
        output_path = os.path.join(js_path,file_name)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(f"// {file_name} 为空，没有指标需要展示\n")
            f.write(f"const {file_name[:-3]} = {{}};")
        return

    type_mapping = {}
    with open(info_path,'r',encoding='utf-8') as f:
        info = json.load(f)
        for indicator in df.columns:
            if indicator == 'date': continue
            type_mapping[indicator] = info[indicator]['type']

    start_date = df.loc[1,'date']
    end_date = df['date'].iat[-1]

    
    # 生成日期信息
    dates = {f'day{i}': df.loc[i, 'date'] for i in range(1, len(df))}
    
    # 生成指标数据
    indicators = []
    
    for field in df.columns:
        if field == 'date':
            continue
        
        indicator_type = type_mapping[field]
        day_data = {}
        
        for i in range(1, len(df)):
            day_key = f'day{i}'
            value = df.loc[i, field] if not pd.isna(df.loc[i, field]) else 0
            
            prev = df.loc[i-1, field] if not pd.isna(df.loc[i-1, field]) else 0

            if prev != 0:
                change_pct = ((value - prev) / prev) * 100
                change = f"{change_pct:+.2f}%"
            else:
                change = "0%"
            
            # 确定状态（这里可以根据业务逻辑调整）
            status = "正常"
            
            day_data[day_key] = {
                'value': round(value, 4),
                'change': change,
                'status': status
            }
        
        indicators.append({
            'type': indicator_type,
            'name': field,
            **day_data
        })
    
    # 生成JS数据
    js_data = {
        'date_range': {
            'start_date': start_date,
            'end_date': end_date
        },
        'days': dates,
        'indicators': indicators
    }
    
    # 写入JS文件
    output_path = os.path.join(js_path,file_name)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(f"// {file_name} - 卫星遥测数据 ({start_date} 至 {end_date})\n")
        f.write(f"const {file_name[:-3]} = {json.dumps(js_data, ensure_ascii=False, indent=4)};")
    


