"""
智能体核心智能模块。
"""
from typing import Dict
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_classic.agents import create_tool_calling_agent, AgentExecutor
from config import QWEN_MODEL, SYSTEM_PROMPT
from tools.utils import build_llm
from tools import (
    get_satellite_status_report,
    kb_search,
    run_lstm_ad,
    analyze_lstm_results,
    query_oss_csv_data
)

_STORE: Dict[str, ChatMessageHistory] = {}

def build_agent(verbose=False, model_name=QWEN_MODEL):
    """
    构建智能体执行器，包含工具和系统提示词。
    """
    llm = build_llm(model_name)
    tools = [
        get_satellite_status_report, 
        kb_search, 
        run_lstm_ad, 
        analyze_lstm_results, 
        query_oss_csv_data
    ]
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
        MessagesPlaceholder("agent_scratchpad"),
    ])
    
    return AgentExecutor(
        agent=create_tool_calling_agent(llm, tools, prompt), 
        tools=tools, 
        verbose=verbose
    )


def build_runnable_with_history(verbose=False, model_name=QWEN_MODEL):
    """
    包装智能体以管理消息历史。
    """
    return RunnableWithMessageHistory(
        build_agent(verbose, model_name),
        lambda sid: _STORE.setdefault(sid, ChatMessageHistory()),
        input_messages_key="input",
        history_messages_key="chat_history",
    )


if __name__ == "__main__":
    agent = build_agent(verbose=True)
    print("Agent started (types 'exit' to quit)")
    while True:
        try:
            q = input("\nYou: ").strip()
            if q.lower() in {"exit", "quit"}:
                break
            if q:
                print("\nAssistant:", agent.invoke({"input": q, "chat_history": []})["output"])
        except KeyboardInterrupt:
            break
        except Exception as e:
            print("Error:", e)
