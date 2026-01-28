import streamlit as st
import time
from langchain_core.messages import HumanMessage,AIMessage
import streamlit.components.v1 as components
import os
import pandas as pd
from . import utils

def load_agent(model_name):
    """加载或更新智能体。"""
    from agent import build_agent
    if "agent" not in st.session_state or st.session_state.get("current_model") != model_name:
        with st.spinner(f"正在加载模型 {model_name}..."):
            st.session_state.agent = build_agent(verbose=True, model_name=model_name)
            st.session_state.current_model = model_name



def render_chat():
    """渲染对话历史。"""
    for i, msg in enumerate(st.session_state.messages):
        role = "user" if isinstance(msg, HumanMessage) else "assistant"
        avatar = "🧑‍💻" if role == "user" else "🛰️"
        
        with st.chat_message(role, avatar=avatar):
            content = msg.content
            
            if role == "assistant":
                st.markdown(content)

                html_path = utils.extract_file_path(content, "html")
                img_path = utils.extract_file_path(content, "(?:png|jpg|jpeg)")
                json_path = utils.extract_file_path(content, "json")

                #在这里加入在对话框中显示html的功能，既可以显示报告，也可以在新建标签页打开
                #具体的方法是使用st.components.iframe显示报告，使用st.markdown生成新标签页链接
                if html_path and os.path.exists(html_path):
                

                    from tools import html_to_hyperlink as hth
                    base_url = hth.get_report_url(html_path)
                    url = f"{base_url}?_ts={int(time.time() * 1000)}"
                    #components.iframe(url, height=720, width=900, scrolling=True)
                    st.markdown(
                        f'<a href="{url}" target="_blank">🔗 在新标签页打开报告</a>',
                        unsafe_allow_html=True
                    )

                elif img_path and os.path.exists(img_path):
                    st.success(f"✅ 图表: {os.path.basename(img_path)}")
                    st.image(img_path)
                    with open(img_path, "rb") as f:
                        st.download_button("📥 下载图片", f, os.path.basename(img_path), key=f"dl_img_{i}")

                elif json_path and os.path.exists(json_path):
                    st.success(f"✅ 数据: {os.path.basename(json_path)}")
                    try:
                        df = pd.read_json(json_path)
                        t1, t2 = st.tabs(["📈 图表", "📋 表格"])
                        with t1:
                            if "time" in df.columns:
                                plot_df = df.iloc[::len(df)//1000] if len(df) > 5000 else df
                                st.line_chart(plot_df.set_index("time").select_dtypes(include=['number']))
                            else:
                                st.info("未找到时间列。")
                        with t2:
                            st.dataframe(df)
                        with open(json_path, "rb") as f:
                            st.download_button("📥 下载 JSON", f, os.path.basename(json_path), key=f"dl_json_{i}")
                    except Exception as e:
                        st.error(f"读取数据失败: {e}")
            else:
                st.markdown(content)


def process_input():
    """处理用户输入。"""
    # 处理待办操作
    if st.session_state.messages and isinstance(st.session_state.messages[-1], HumanMessage):
        with st.chat_message("assistant", avatar="🛰️"):
            with st.spinner("正在分析..."):
                try:
                    resp = st.session_state.agent.invoke({
                        "input": st.session_state.messages[-1].content,
                        "chat_history": st.session_state.messages[:-1]
                    })
                    st.session_state.messages.append(AIMessage(content=resp["output"]))
                    st.rerun()
                except Exception as e: 
                    st.error(f"系统错误: {e}")
    
    # 仅在空闲时显示输入框
    if not (st.session_state.messages and isinstance(st.session_state.messages[-1], HumanMessage)):
        if prompt := st.chat_input("输入指令..."):
            st.session_state.messages.append(HumanMessage(content=prompt))
            st.rerun()
