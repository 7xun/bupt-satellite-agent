import streamlit as st
import functools
import http.server
import threading,os,json
import streamlit.components.v1 as components
from urllib.parse import quote as url_quote
class _QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        return
@st.cache_resource
def _get_report_server(root_dir):
    handler = functools.partial(_QuietHandler, directory=root_dir)
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server


def get_report_url(html_path):
    """为报告路径生成本地可访问的 URL。"""
    root_dir = os.path.dirname(html_path)
    filename = os.path.basename(html_path)
    server = _get_report_server(root_dir)
    port = server.server_address[1]
    return f"http://127.0.0.1:{port}/{url_quote(filename)}"


def open_html_in_new_tab(html_path, opened_key):
    """最佳努力方式在新标签页打开 HTML。"""
    if "opened_report_tabs" not in st.session_state:
        st.session_state.opened_report_tabs = set()
    if opened_key in st.session_state.opened_report_tabs:
        return
    st.session_state.opened_report_tabs.add(opened_key)

    url = get_report_url(html_path)
    url_js = json.dumps(url)
    components.html(
        f"""
        <script>
        (function() {{
            const url = {url_js};
            const newWin = window.open(url, "_blank");
            if (newWin) {{
                if (newWin.blur) newWin.blur();
                if (window.focus) window.focus();
            }}
        }})();
        </script>
        """,
        height=0,
        width=0,
    )

