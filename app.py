"""
Streamlit 前端应用。
"""

import frontend.components as components
from frontend.services import chat


# --- 主入口 ---
def run():
    components.mainpage.page_init()
    components.mainpage.session_init()
    model = components.mainpage.render_sidebar()
    
    chat.load_agent(model)
    components.mainpage.render_welcome()
    chat.render_chat()
    chat.process_input()

if __name__ == "__main__":
    run() # 每次用户交互都会重新执行这行
