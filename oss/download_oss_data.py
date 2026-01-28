# -*- coding: utf-8 -*-
"""
从 OSS 下载 CSV 数据文件 (使用阿里云 OSS SDK)
"""
import os
import oss2
import pandas as pd
import io

# =============================================================================
# 配置信息
# =============================================================================
ACCESS_KEY_ID = os.environ.get('OSS_ACCESS_KEY_ID')
ACCESS_KEY_SECRET = os.environ.get('OSS_ACCESS_KEY_SECRET')
ENDPOINT = 'oss-cn-beijing.aliyuncs.com'  # 建议使用内网端点
BUCKET_NAME = 'hede-satellite'
# OSS_OBJECT_KEY = 'E/0x0826/2023_07.csv'

hex = "0x0826"
csv = "2023_06.csv"
OSS_OBJECT_KEY = 'E/'+hex+'/'+csv
# 输出文件路径
OUTPUT_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "E", f"{hex}", f"{csv}")


def download_oss_csv():
    print(f"正在从 OSS 下载文件: {OSS_OBJECT_KEY}")
    
    try:
        # 1. 创建认证对象
        auth = oss2.Auth(ACCESS_KEY_ID, ACCESS_KEY_SECRET)
        
        # 2. 创建 Bucket 对象
        bucket = oss2.Bucket(auth, ENDPOINT, BUCKET_NAME)
        

        # 3. 下载文件
        bucket.get_object_to_file(OSS_OBJECT_KEY, OUTPUT_FILE)
        print(f"✅ 文件已下载至: {os.path.abspath(OUTPUT_FILE)}")
        
        #======================================
        # file = bucket.get_object(OSS_OBJECT_KEY)
        # df = pd.read_csv(
        #     io.BytesIO(file.read()),
        #             usecols = ["time",'ZTMD214-母线电压','ZTMD215-母线电流'],
        #             encoding = 'utf-8' )
        # df.to_csv(OUTPUT_FILE,index=False,encoding='utf-8')
        


        # 4. 读取文件信息
        file_size = os.path.getsize(OUTPUT_FILE)
        print(f"文件大小: {file_size:,} 字节")
        
    except Exception as e:
        print(f"❌ 下载失败: {e}")


def get_list():
    auth = oss2.Auth(ACCESS_KEY_ID, ACCESS_KEY_SECRET)
    bucket = oss2.Bucket(auth, ENDPOINT, BUCKET_NAME)
    prefix = f'E/{hex}/'
    csv_list = []
    for obj in oss2.ObjectIterator(bucket, prefix=prefix):
        if(obj.key.endswith('.csv')):
            print(obj.key)


if __name__ == '__main__':
    #get_list()
    download_oss_csv()