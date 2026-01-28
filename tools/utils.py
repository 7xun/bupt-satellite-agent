"""
智能体工具函数与类。
"""
import os
from typing import List
import re
import duckdb
import pandas as pd
from openai import OpenAI
from langchain_openai import ChatOpenAI
from langchain_core.embeddings import Embeddings
from langchain_community.vectorstores import FAISS
from datetime import datetime, timedelta
from config import PROJECT_ROOT

from config import (
    DASHSCOPE_API_KEY, DASHSCOPE_BASE_URL, EMBEDDING_MODEL,
    EMBEDDING_DIMENSIONS, VECTOR_STORE_DIR, BAG_NAME, BAG_LABEL, QWEN_MODEL
)

_RETRIEVER = None


def _require_key():
    """确保 API KEY 已配置。"""
    if not DASHSCOPE_API_KEY or "REPLACE_ME" in DASHSCOPE_API_KEY:
        raise RuntimeError("请配置 DASHSCOPE_API_KEY")


def _normalize_bag_id(bag: str) -> str:
    """标准化包名 ID。"""
    if bag in BAG_NAME:
        return BAG_LABEL[BAG_NAME.index(bag)]
    return bag


def _query_parquet(start_ns: int, end_ns: int, path: str, cols: List[str], index_col="time") -> pd.DataFrame:
    """使用 DuckDB 查询 Parquet 文件。"""
    con = duckdb.connect()
    try:
        try:
            schema = con.sql(f"DESCRIBE SELECT * FROM '{path}'").df()
        except Exception:
            return pd.DataFrame()

        all_cols = schema["column_name"].tolist()
        final_cols = {index_col} if index_col in all_cols else set()

        for target in cols:
            if target in all_cols:
                final_cols.add(target)
            else:
                # 前缀匹配
                for ac in all_cols:
                    if ac.startswith(target):
                        final_cols.add(ac)
                        break

        if not final_cols:
            return pd.DataFrame()

        select_str = ", ".join([f'"{c}"' for c in final_cols])
        query = f'SELECT {select_str} FROM \'{path}\' WHERE "{index_col}" >= {start_ns} AND "{index_col}" <= {end_ns}'
        df = con.sql(query).df()
        
        if "time" in df.columns:
            df["time"] = pd.to_datetime(df["time"], unit="ns")
        return df
    finally:
        con.close()


class DashScopeCompatibleEmbeddings(Embeddings):
    """DashScope 兼容的 Embeddings 类。"""
    
    def __init__(self, api_key, base_url, model, chunk_size=10, dimensions=None):
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.model = model
        self.chunk_size = chunk_size
        self.dimensions = dimensions

    def _embed_batch(self, batch):
        kwargs = {"model": self.model, "input": batch, "encoding_format": "float"}
        if self.dimensions:
            kwargs["dimensions"] = self.dimensions
        return [i.embedding for i in self.client.embeddings.create(**kwargs).data]

    def embed_documents(self, texts):
        clean = [str(t).strip() for t in texts if t and str(t).strip()]
        vectors = []
        for i in range(0, len(clean), self.chunk_size):
            vectors.extend(self._embed_batch(clean[i:i + self.chunk_size]))
        return vectors

    def embed_query(self, text):
        return self._embed_batch([str(text).strip()])[0] if str(text).strip() else []


def build_embeddings():
    """构建 Embeddings 模型。"""
    _require_key()
    return DashScopeCompatibleEmbeddings(
        DASHSCOPE_API_KEY, DASHSCOPE_BASE_URL, EMBEDDING_MODEL, dimensions=EMBEDDING_DIMENSIONS
    )


def build_llm(model_name=QWEN_MODEL):
    """构建 LLM 实例。"""
    _require_key()
    return ChatOpenAI(
        model=model_name, temperature=0, api_key=DASHSCOPE_API_KEY, base_url=DASHSCOPE_BASE_URL
    )


def _get_retriever():
    """获取或初始化 FAISS 检索器。"""
    global _RETRIEVER
    if _RETRIEVER is None:
        if not os.path.isdir(VECTOR_STORE_DIR):
            raise FileNotFoundError(f"向量库未找到: {VECTOR_STORE_DIR}\n请运行 build_index.py")
        
        vs = FAISS.load_local(
            VECTOR_STORE_DIR, build_embeddings(), allow_dangerous_deserialization=True
        )
        _RETRIEVER = vs.as_retriever(search_kwargs={"k": 4})
    return _RETRIEVER


def log(info:str):
    """
    直接输入日志信息，不必输入结尾换行符
    """
    # 用于调试，请勿删除
    # 直接添加/删除下方 return 的注释即可
    return
    p = os.path.join(PROJECT_ROOT,'log.txt')
    with open(p,'a',encoding='utf-8')as f:
        f.write(f"{datetime.now().strftime('%m/%d %H:%M:%S')}\n{info}\n\n")

