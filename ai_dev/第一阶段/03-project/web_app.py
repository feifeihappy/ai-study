import streamlit as st
from typing import List
from pydantic import BaseModel, Field
from dotenv import load_dotenv
import os

# --- LangChain 导入 ---
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.runnables import RunnablePassthrough

# 1. 加载环境变量
load_dotenv()


# 2. 定义数据结构 (Schema)
class HistoricalAnalysis(BaseModel):
    """资治通鉴片段的结构化分析结果"""
    event_title: str = Field(description="事件标题，简练概括")
    event_type: str = Field(description="事件类型，如'政变', '战争'")
    summary: str = Field(description="事件摘要，100字以内")
    key_figures: List[str] = Field(description="涉及的关键历史人物列表")
    locations: List[str] = Field(description="涉及的地理位置列表")
    moral_lesson: str = Field(description="核心启示或司马光的评价观点")
    is_critical: bool = Field(description="是否为关键转折点")


# 3. 初始化模型与解析器
llm = ChatOpenAI(
    model="qwen-plus",
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    temperature=0.3
)
parser = PydanticOutputParser(pydantic_object=HistoricalAnalysis)


# 4. 模拟检索器 (Mock Retriever)
def mock_retriever(query: str) -> str:
    if "王莽" in query or "九锡" in query:
        return """
        【原文片段】：五月，策命安汉公莽以九锡，莽稽首辞让，出奏封事，愿独得母衣服，必得之乃止。
        【背景】：元始元年（公元1年），王莽掌握朝政，为了进一步攫取权力，授意党羽上书请求赐予九锡。
        【注释】：九锡，古代天子赐给诸侯、大臣的九种器物，是一种最高礼遇。
        """
    else:
        return "未找到相关原文片段，请尝试询问关于王莽或西汉末年的历史。"


# 5. 构建 Prompt
prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一位精通《资治通鉴》的历史研读助手。请基于提供的【原文片段】回答用户问题。"),
    ("user", """
    请分析以下内容：

    【原文片段】：
    {context}

    【用户问题】：
    {input_text}

    {format_instructions}
    """)
])

# 6. 构建核心链条 (Chain)
chain = (
        {
            "context": RunnablePassthrough() | (lambda x: mock_retriever(x["input_text"])),
            "input_text": RunnablePassthrough(),
            "format_instructions": RunnablePassthrough() | (lambda x: parser.get_format_instructions())
        }
        | prompt
        | llm
        | parser
)

# ==========================================
# 7. Streamlit 界面逻辑 (重写版 - 核心修复)
# ==========================================

st.set_page_config(page_title="资治通鉴助手", page_icon="📜")
st.title("📜 资治通鉴研读助手")

# 初始化 Session State
if "messages" not in st.session_state:
    st.session_state.messages = []


# --- 辅助函数：专门用来显示 AI 的分析卡片 ---
def display_analysis(data_dict):
    """
    专门接收字典数据并渲染成卡片。
    无论新旧数据，都统一用这个函数处理，确保格式一致。
    """
    # 1. 标题与类型
    st.markdown(f"### 📜 {data_dict.get('event_title', '未知标题')}")
    st.markdown(f"**类型**：{data_dict.get('event_type', '未知')}")
    st.markdown("---")

    # 2. 摘要与启示
    st.markdown(f"**📝 摘要**：{data_dict.get('summary', '无')}")
    st.markdown(f"**💡 启示**：{data_dict.get('moral_lesson', '无')}")

    # 3. 人物与地点 (并排)
    col1, col2 = st.columns(2)
    with col1:
        figures = data_dict.get('key_figures', [])
        # 确保 figures 是列表，防止模型返回字符串
        if isinstance(figures, str):
            figures = [figures]
        st.markdown(f"👥 **人物**：{', '.join(figures)}")

    with col2:
        locs = data_dict.get('locations', [])
        if isinstance(locs, str):
            locs = [locs]
        st.markdown(f"📍 **地点**：{', '.join(locs)}")

    # 4. 关键转折点警告
    if data_dict.get('is_critical', False):
        st.markdown("**⚠️ 警告：这是历史的关键转折点！**")


# --- 显示历史消息 ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if message["role"] == "ai":
            # 关键点：这里直接把 content (字典) 传给 display_analysis 函数
            # 不再做任何类型判断，因为我们只存字典
            display_analysis(message["content"])
        else:
            st.write(message["content"])

# --- 处理用户输入 ---
if prompt_text := st.chat_input("请输入历史人物或事件（例如：王莽受九锡）"):
    # 1. 显示并保存用户输入
    with st.chat_message("user"):
        st.write(prompt_text)
    st.session_state.messages.append({"role": "user", "content": prompt_text})

    # 2. 调用 AI 并显示结果
    with st.chat_message("assistant"):
        with st.spinner("正在研读史书..."):
            try:
                # 调用 Chain
                result = chain.invoke({"input_text": prompt_text})

                # --- 核心修复逻辑 ---
                # 1. 将 Pydantic 对象转换为普通字典
                # 这样它才能被 Streamlit 安全地保存和读取
                if hasattr(result, 'dict'):
                    result_dict = result.dict()
                elif hasattr(result, 'model_dump'):  # Pydantic V2 兼容
                    result_dict = result.model_dump()
                else:
                    result_dict = dict(result)  # 万不得已转成字典

                # 2. 使用统一的函数显示结果
                display_analysis(result_dict)

                # 3. 直接将字典保存到历史记录中 (不再保存对象)
                st.session_state.messages.append({"role": "ai", "content": result_dict})

            except Exception as e:
                st.error(f"分析出错：{e}")
                st.session_state.messages.append({"role": "ai", "content": {"error": str(e)}})