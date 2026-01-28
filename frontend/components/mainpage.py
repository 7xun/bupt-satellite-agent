
import streamlit as st
from langchain_core.messages import AIMessage,HumanMessage

def page_init():
    from .page_config import PAGE_ICON,PAGE_TITLE,LAYOUT,CUSTOM_CSS
    st.set_page_config(page_title=PAGE_TITLE, page_icon=PAGE_ICON, layout=LAYOUT)
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
    st.title("🛰️ 卫星运维智能体")


def session_init():
    """初始化会话状态。"""
    if "messages" not in st.session_state:
        st.session_state.messages = [
            AIMessage(content="👋 **您好！我是北邮卫星运维智能助手。**\n\n我可以帮您进行卫星体检、异常检测或查询故障知识库。")
        ]
    if "report_mode" not in st.session_state:
        st.session_state.report_mode = False




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
            import time
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



def render_welcome():
    """渲染欢迎界面及操作按钮。"""
    st.markdown("### 💡 快速开始")
    st.markdown("选择一个任务或下方输入:")
    
    def handle_action(prompt):
        """处理快捷操作。"""
        st.session_state.messages.append(HumanMessage(content=prompt))
        st.rerun()

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
        if st.button("🏥 健康体检\n\n查看报告", use_container_width=True):
            handle_action("我想看报告")
            
    
    st.divider()


