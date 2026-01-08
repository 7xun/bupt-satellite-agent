"""
Streamlit 前端应用。
"""
import os
import re
import time
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
from langchain_core.messages import HumanMessage, AIMessage
from agent import build_agent


# --- 配置 ---

PAGE_TITLE = "北邮卫星智能体"
PAGE_ICON = "🤖"
LAYOUT = "wide"

CUSTOM_CSS = """
<style>
    .stChatFloatingInputContainer {bottom: 20px;}
    .block-container {padding-top: 2rem;}
    h1 {color: #0056b3; font-family: 'Segoe UI', sans-serif; font-weight: 600;}
    
    /* Sidebar Style */
    [data-testid="stSidebar"] {background-color: #f8f9fa; border-right: 1px solid #e9ecef;}
    
    /* Status Card */
    .status-card {
        background-color: #ffffff; 
        border-left: 4px solid #0056b3; 
        padding: 15px; 
        border-radius: 6px; 
        margin-bottom: 20px; 
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
    .status-item {display: flex; justify-content: space-between; margin-bottom: 8px; font-size: 0.9em; color: #495057;}
    .status-item:last-child {margin-bottom: 0;}
    .status-value {font-weight: 600; color: #0056b3;}
    
    /* Button Style */
    .stButton button {
        border-radius: 8px; 
        border: 1px solid #dee2e6; 
        transition: all 0.2s;
        font-weight: 500;
    }
    .stButton button:hover {
        border-color: #0056b3; 
        color: #0056b3; 
        background-color: #e7f1ff;
        transform: translateY(-1px);
    }
</style>
"""


# --- 辅助函数 ---

def init_session():
    """初始化会话状态。"""
    if "messages" not in st.session_state:
        st.session_state.messages = [
            AIMessage(content="👋 **您好！我是北邮卫星运维智能助手。**\n\n我可以帮您进行卫星体检、异常检测或查询故障知识库。")
        ]


def load_agent(model_name):
    """加载或更新智能体。"""
    if "agent" not in st.session_state or st.session_state.get("current_model") != model_name:
        with st.spinner(f"正在切换模型到 {model_name}..."):
            st.session_state.agent = build_agent(verbose=True, model_name=model_name)
            st.session_state.current_model = model_name


def render_sidebar():
    """渲染侧边栏。"""
    with st.sidebar:
        st.title("⚙️ 控制面板")
        
        st.markdown("### 🤖 模型配置")
        model = st.radio("基础模型:", ("qwen-plus", "qwen3-omni-flash"), index=0)
        
        st.markdown("### 🖥️ 系统状态")
        msg_count = len(st.session_state.messages) // 2
        
        st.markdown(f"""
        <div class="status-card">
            <div class="status-item"><span>状态</span><span class="status-value">🟢 在线</span></div>
            <div class="status-item"><span>模型</span><span class="status-value">{model}</span></div>
            <div class="status-item"><span>知识库</span><span class="status-value">📚 已加载</span></div>
            <div class="status-item"><span>轮次</span><span class="status-value">{msg_count}</span></div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("### 🛠️ 工具箱")
        if st.session_state.messages:
            chat_log = "\n\n".join([f"[{m.type.upper()}] {m.content}" for m in st.session_state.messages])
            st.download_button(
                "💾 导出日志", 
                chat_log, 
                file_name=f"chat_log_{int(time.time())}.txt", 
                use_container_width=True
            )
        
        if st.button("🗑️ 清除历史", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
            
        st.markdown("---")
        st.caption("© 2025 北邮卫星团队")
            
    return model


def handle_action(prompt):
    """处理快捷操作。"""
    st.session_state.messages.append(HumanMessage(content=prompt))
    st.rerun()


def extract_file_path(text, ext_pattern):
    """
    从文本中提取有效的文件路径。
    支持绝对路径、相对路径和文件名。
    """
    pattern = rf"((?:[a-zA-Z]:[\\/])?(?:[\w\-\.]+[\\/])*[\w\-\.]+\.{ext_pattern})"
    matches = re.findall(pattern, text, re.IGNORECASE)
    
    for match in matches:
        path = match.strip()
        if os.path.exists(path):
            return path
        abs_path = os.path.abspath(path)
        if os.path.exists(abs_path):
            return abs_path
            
    return None


def render_welcome():
    """渲染欢迎界面及操作按钮。"""
    st.markdown("### 💡 快速开始")
    st.markdown("选择一个任务或下方输入:")
    
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        if st.button("📘 故障诊断\n\nGNSS 故障排查", use_container_width=True):
            handle_action("GNSS故障的一般步骤是什么？")
    with c2:
        if st.button("🔍 数据查询\n\nOSS 遥测数据", use_container_width=True):
            handle_action("帮我查询E卫星0x0821包中，2023年第7周的数据中‘ZTMS015-帆板1状态’字段值为‘未展开’的所有数据。")
    with c3:
        if st.button("📉 异常检测\n\n深度学习 (LSTM)", use_container_width=True):
            handle_action("运行lstm模型进行时序异常检测")
    with c4:
        if st.button("🏥 健康体检\n\n年度报告", use_container_width=True):
            handle_action("请展示年度报告")
    
    st.divider()


def render_chat():
    """渲染对话历史。"""
    for i, msg in enumerate(st.session_state.messages):
        role = "user" if isinstance(msg, HumanMessage) else "assistant"
        avatar = "🧑‍💻" if role == "user" else "🛰️"
        
        with st.chat_message(role, avatar=avatar):
            content = msg.content
            
            if role == "assistant":
                st.markdown(content)

                html_path = extract_file_path(content, "html")
                img_path = extract_file_path(content, "(?:png|jpg|jpeg)")
                json_path = extract_file_path(content, "json")

                if html_path and os.path.exists(html_path):
                    st.success(f"✅ 报告: {os.path.basename(html_path)}")
                    with open(html_path, "r", encoding="utf-8") as f:
                        components.html(f.read(), height=600, scrolling=True)
                    with open(html_path, "rb") as f:
                        st.download_button("📥 下载 HTML", f, os.path.basename(html_path), key=f"dl_html_{i}")

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


# --- 主入口 ---

def main():
    st.set_page_config(page_title=PAGE_TITLE, page_icon=PAGE_ICON, layout=LAYOUT)
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

    init_session()
    model = render_sidebar()
    st.title("🛰️ 卫星运维智能体")
    
    load_agent(model)
    render_welcome()
    render_chat()
    process_input()


if __name__ == "__main__":
    main()
