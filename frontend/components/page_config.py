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
