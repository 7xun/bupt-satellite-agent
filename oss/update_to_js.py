import io
import os
import oss2
import pandas as pd
from tools import time_translate as tt
import json
import chardet
from config import (
    PROJECT_ROOT,
    NORMAL_VALUES,
    PART_1_INDICATORS,
    PART_2_INDICATORS,
    OSS_ACCESS_KEY_ID,
    OSS_ACCESS_KEY_SECRET,
    OSS_ENDPOINT,
    OSS_BUCKET_NAME
)
from . import save_to_js
from tools.utils import log

ACCESS_KEY_ID = OSS_ACCESS_KEY_ID
ACCESS_KEY_SECRET = OSS_ACCESS_KEY_SECRET
ENDPOINT = OSS_ENDPOINT
BUCKET_NAME = OSS_BUCKET_NAME


# 这里 indicators 与 fields 混用了。含义是相同的

def _get_target(indicator_list:list, info_path:str)->list:
    """
    结果结构如下：
    target = [
        # [十六进制编号, [需要的字段1, 需要的字段2, ...]]
        ['0x0826',['ZTMD214-母线电压','ZTMD215-母线电流']],
        ['0x3030',['蓄电池电流','蓄电池电压','上注指令接收计数','上注指令执行计数','上注指令错误计数']],
        ....
    ]
    """

    # 加载映射文件
    with open(info_path, 'r', encoding='utf-8') as f:
        info = json.load(f)
    
    # 创建一个字典来按包标识分组
    d = {}
    
    for indicator in indicator_list:
        hex = info[indicator]['hex_num']
        if hex not in d:
            d[hex] = []
        d[hex].append(indicator)
    # 转换为目标格式
    target = []
    for hex, indicators in d.items():
        target.append([hex, indicators])
    
    return target


def _get_file_paths_dict(bucket:oss2.Bucket, target, end_date:str)->dict:
    """
    获取每个hex_num对应的CSV文件路径
    示例：
    {
        "0x0826" : ["E/0x0826/2022_20.csv","E/0x0826/2022_19.csv"]
    }
    """
    file_paths = {}
    end_year, end_month, _ = map(int, end_date.split('-'))
    end_limit = f"{end_year}_{end_month*5:02d}.csv"
    
    for hex_num, _ in target:
        prefix = f'E/{hex_num}/'
        csv_list = []
        
        for obj in oss2.ObjectIterator(bucket, prefix=prefix):
            if obj.key.endswith('.csv'):
                csv_list.append(obj.key) # 形式："E/0x0826/2022_24.csv"
        
        csv_list.sort(reverse=True)
        
        # 过滤异常数据
        csv_list = [item for item in csv_list if item[-11:] < end_limit]
        
        file_paths[hex_num] = csv_list
    
    return file_paths


def _read_df(bucket:oss2.Bucket,file_path:str,fields:list,encoding_info:dict)->pd.DataFrame|None:
    log(f"reading {file_path}")
    file_obj = bucket.get_object(file_path)
    file_content = file_obj.read()
    dtype = {
        'time':'int',
        **{
            field:'str' if field in NORMAL_VALUES else 'float64' for field in fields
        }
    }
    def read(encoding:str)->pd.DataFrame|None:
        try:
            df_file = pd.read_csv(
                io.BytesIO(file_content),
                usecols=["time"] + fields,
                #dtype={'time': 'int', **{field: 'float64' for field in fields}},
                dtype=dtype,
                encoding=encoding,
                na_values=['False', 'false', 'FALSE', 'N/A', 'NA', 'null', 'NULL', 'NaN', 'nan', ''],
                keep_default_na=True
            )
            return df_file
        except: return None
    df_file = None

    if(file_path in encoding_info):
        encoding = encoding_info[file_path]
        df_file = read(encoding=encoding)
        if df_file is not None: return df_file
    
    df_file = read('utf-8')
    if df_file is not None:
        encoding_info[file_path] = 'utf-8'
        return df_file

    encoding_detected = chardet.detect(file_content)
    df_file = read(encoding_detected)
    if df_file is not None:
        encoding_info[file_path] = 'utf-8'
        return df_file

    encodings = ['gbk', 'gb2312', 'gb18030']
    for encoding in encodings:
        df_file = read(encoding)
        if df_file is not None:
            encoding_info[file_path] = 'utf-8'
            return df_file

    log(f"读取 {file_path}失败\n")
    return df_file

def _get_tot_df(bucket:oss2.Bucket, start_date:str, end_date:str, target:list,  file_paths_dict:dict, encoding_info_path:str,first_times_info_path:str)->pd.DataFrame:
    """获取日期范围内的数据并合并为DataFrame"""
    start_time = tt.date_to_time(start_date)
    end_time = tt.date_to_time(end_date) + 24*3600*1e9  # 包含结束日期当天
    
    # 生成所有日期
    date_range = pd.date_range(start=start_date, end=end_date, freq='D')
    dates = [date.strftime('%Y-%m-%d') for date in date_range]
    
    # 初始化DataFrame
    tot_df = pd.DataFrame(columns = ['date'] + [item for _, fields in target for item in fields])
    
    # 设置日期列
    for i, date in enumerate(dates): tot_df.loc[i, 'date'] = date

    # 如果暂无预处理文件
    if not os.path.exists(encoding_info_path):
        with open(encoding_info_path, 'w', encoding='utf-8') as f:
            f.write('{}')
    if not os.path.exists(first_times_info_path):
        with open(first_times_info_path, 'w', encoding='utf-8') as f:
            f.write('{}')
    
    with open(encoding_info_path,'r',encoding='utf-8')as f:
        encoding_info = json.load(f)
    with open(first_times_info_path,'r',encoding='utf-8') as f:
        first_times_info = json.load(f)
    
    # 处理每个hex_num的数据
    for hex_num, fields in target:
        # 按日期分组收集数据
        d = {date: [] for date in dates} # dict
        for file_path in file_paths_dict[hex_num]:
            # 跳过日期范围外的文件 (year)
            if file_path[-11:-7] > end_date[:4]: continue
            
            # 获取文件第一行时间，用于快速判断
            if file_path in first_times_info:
                first_time = first_times_info[file_path]
                if first_time >= end_time: continue
            
            # 读取完整文件
            df_file = _read_df(bucket=bucket,file_path=file_path,fields=fields,encoding_info=encoding_info)
            
            
            # 如果实在读取不出来，跳过该指标
            if df_file is None: 
                continue 
            first_times_info[file_path] = int(df_file.loc[0,'time'])
            # 按日期分组数据
            for i, date in enumerate(dates):
                start_t = tt.date_to_time(date)
                end_t = start_t + 24*3600*1e9
                date_df = df_file.query('@start_t <= time < @end_t')
                if not date_df.empty: d[date].append(date_df)
            if(int(df_file.loc[len(df_file)-1,'time']) < start_time): break
        # 此 hex 下所有文件已读完

        # 计算每个日期的计数或平均值
        for i, date in enumerate(dates):
            date_dfs = d[date]
            
            if len(date_dfs) > 0:
                # 合并该日期的所有数据
                combined_df = pd.concat(date_dfs, ignore_index=True)
                
                for field in fields:
                    if field in combined_df.columns:
                        if field not in NORMAL_VALUES:
                            mean_value = combined_df[field].mean()
                            tot_df.loc[i, field] = mean_value if not pd.isna(mean_value) else 0
                        else:
                            normal_values = NORMAL_VALUES[field]
                            cnt = 0
                            for x in combined_df[field]:
                                if x not in normal_values: cnt+=1
                            tot_df.loc[i,field] = cnt

                    else: tot_df.loc[i, field] = 0
            else:
                for field in fields: tot_df.loc[i, field] = 0
    
    with open(encoding_info_path,'w',encoding='utf-8') as f:
        json.dump(encoding_info,f,indent=4,ensure_ascii=False)
    with open(first_times_info_path,'w',encoding='utf-8') as f:
        json.dump(first_times_info,f,indent=4,ensure_ascii=False)

    return tot_df



def update(indicators:list,start_date:str,end_date:str):
    log(f"已进入update")
    try:
        start_date = tt.time_to_date(tt.date_to_time(start_date)-24*3600*1e9) # 前一天，因为要处理增量 

        # 初始化OSS连接
        auth = oss2.Auth(ACCESS_KEY_ID, ACCESS_KEY_SECRET)
        bucket = oss2.Bucket(auth, ENDPOINT, BUCKET_NAME)

        indicator_list = list(set(PART_1_INDICATORS+PART_2_INDICATORS+indicators))

        indicator_info_path = os.path.join(PROJECT_ROOT,'oss','info','indicator_info.json')
        encoding_info_path = os.path.join(PROJECT_ROOT,'oss','info','encoding_info.json')
        first_times_info_path = os.path.join(PROJECT_ROOT,'oss','info','first_times_info.json')

        # 查询目标
        target = _get_target(indicator_list=indicator_list,info_path=indicator_info_path)

        # 获取文件路径
        file_paths_dict = _get_file_paths_dict(bucket, target, end_date=end_date)


        log("正在得到df")
        df = _get_tot_df(bucket=bucket,start_date=start_date,end_date=end_date,target=target,file_paths_dict=file_paths_dict,encoding_info_path=encoding_info_path,first_times_info_path=first_times_info_path)
        log("已得到df")

        js_path = os.path.join(PROJECT_ROOT,'frontend','js')

        part_1_data_path = os.path.join(PROJECT_ROOT,'frontend','js','part_1_data.js')
        save_to_js.counting_js(df=df[PART_1_INDICATORS],output_path=part_1_data_path)
        log(f"完成part_1.js写入\n")

        
        save_to_js.changes_js(df=df[['date']+PART_2_INDICATORS],info_path=indicator_info_path, js_path=js_path, file_name='part_2_data.js')
        log(f"完成part_2.js写入\n")

        save_to_js.changes_js(df[['date']+indicators],info_path=indicator_info_path,js_path=js_path,file_name='part_3_data.js')
        log(f"完成part_3.js写入\n")
    except:
        import traceback
        log(f"error: {traceback.format_exc()}\n")
   


