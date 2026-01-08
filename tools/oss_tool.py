"""
OSS 数据查询工具。
"""
import os
import pandas as pd
from langchain_core.tools import tool
from config import (
    OSS_ACCESS_KEY_ID, OSS_ACCESS_KEY_SECRET, OSS_ENDPOINT, OSS_BUCKET_NAME,
    OUTPUT_ROOT, PARQUET_ROOT as DATA_ROOT
)

try:
    import oss2
except ImportError:
    oss2 = None


def _download_from_oss(oss_path, local_path):
    """从阿里云 OSS 下载文件。"""
    if not oss2:
        return False, "oss2 模块未安装"
    
    try:
        auth = oss2.Auth(OSS_ACCESS_KEY_ID, OSS_ACCESS_KEY_SECRET)
        bucket = oss2.Bucket(auth, OSS_ENDPOINT, OSS_BUCKET_NAME)
        
        if not bucket.object_exists(oss_path):
            return False, f"OSS 文件未找到: {oss_path}"
            
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        bucket.get_object_to_file(oss_path, local_path)
        return True, "下载成功"
    except Exception as e:
        return False, str(e)


@tool
def query_oss_csv_data(satellite: str, bag_id: str, year: str, week: str, column: str, value: str) -> str:
    """
    下载并过滤 OSS 上的 CSV 数据。
    
    Args:
        satellite (str): 卫星代号 (e.g., "E")
        bag_id (str): 数据包 ID (e.g., "0x0821")
        year (str): 年份 (e.g., "2023")
        week (str): 周数 (e.g., "7" or "07")
        column (str): 过滤列名 (e.g., "ZTMS015-帆板1状态")
        value (str): 目标值 (e.g., "未展开")
        
    Returns:
        str: 状态信息及结果 JSON 文件路径。
    """
    try:
        # 1. 格式化参数
        week_str = f"{int(week):02d}"
        file_name = f"{year}_{week_str}.csv"
        
        # OSS 路径: E/0x0821/2023_07.csv
        oss_key = f"{satellite}/{bag_id}/{file_name}"
        
        # 本地路径: data/E/0x0821/2023_07.csv
        local_dir = os.path.join(DATA_ROOT, satellite, bag_id)
        local_path = os.path.join(local_dir, file_name)
        
        # 2. 检查本地缓存或下载
        if not os.path.exists(local_path):
            print(f"正在下载 {oss_key} 到 {local_path}...")
            success, msg = _download_from_oss(oss_key, local_path)
            if not success:
                return f"获取数据文件失败: {msg}"
        
        # 3. 读取 CSV (尝试多种编码)
        df = None
        for enc in ['utf-8', 'gb18030', 'ISO-8859-1']:
            try:
                df = pd.read_csv(local_path, encoding=enc)
                break
            except Exception:
                continue
        
        if df is None:
            return "无法以支持的编码读取 CSV 文件。"
        
        # 4. 过滤数据
        if column not in df.columns:
            return f"列 '{column}' 未找到。可用列: {list(df.columns)[:5]}..."
            
        mask = df[column].astype(str) == str(value)
        result_df = df[mask].copy()
        
        if result_df.empty:
            return f"未找到匹配 {column} == {value} 的数据。"
            
        # 5. 格式化时间列
        if 'time' in result_df.columns:
            try:
                if pd.api.types.is_numeric_dtype(result_df['time']):
                    result_df['time'] = pd.to_datetime(result_df['time'], unit='ns')
                else:
                    result_df['time'] = pd.to_datetime(result_df['time'])
                
                result_df['time'] = result_df['time'].dt.strftime('%Y-%m-%d %H:%M:%S.%f').str[:-3]
            except Exception as e:
                print(f"警告: 时间列转换失败: {e}")

        # 6. 保存结果
        output_filename = f"{satellite}_{bag_id}_{year}_{week_str}_filtered.json"
        output_path = os.path.join(OUTPUT_ROOT, output_filename)
        os.makedirs(OUTPUT_ROOT, exist_ok=True)
        
        result_df.to_json(output_path, orient='records', force_ascii=False, indent=4)
        
        return f"查询成功。找到 {len(result_df)} 条记录。已保存至: {output_path}"
        
    except Exception as e:
        return f"数据处理错误: {e}"
