import os
from typing import List
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# LangChain 核心组件
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory

# 加载环境变量
load_dotenv()


# ==========================================
# 1. 定义数据结构 (Schema)
# ==========================================

class HistoricalAnalysis(BaseModel):
    """资治通鉴片段的结构化分析结果"""
    event_title: str = Field(description="事件标题，简练概括，如'王莽受九锡'")
    event_type: str = Field(description="事件类型，如'政变', '战争', '外交', '制度改革'")
    summary: str = Field(description="事件摘要，100字以内")
    key_figures: List[str] = Field(description="涉及的关键历史人物列表")
    locations: List[str] = Field(description="涉及的地理位置列表")
    moral_lesson: str = Field(description="核心启示或司马光的评价观点")
    is_critical: bool = Field(description="是否为关键转折点（True/False）")


# 初始化输出解析器

parser = PydanticOutputParser(pydantic_object=HistoricalAnalysis)

# ==========================================
# 2. 初始化模型与工具
# ==========================================

llm = ChatOpenAI(
    model="qwen-plus",
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    temperature=0.3  # 低温度，保证分析准确性
)


# ==========================================
# 3. 模拟检索器 (RAG 的简化版)
# ==========================================

def mock_retriever(query: str) -> str:
    """
    在实际项目中，这里会连接向量数据库 (如 ChromaDB)。
    这里我们模拟检索到了一段关于“王莽”的原文。
    """
    if "王莽" in query or "九锡" in query:
        return """
        【原文片段】：五月，策命安汉公莽以九锡，莽稽首辞让，出奏封事，愿独得母衣服，必得之乃止。
        【背景】：元始元年（公元1年），王莽掌握朝政，为了进一步攫取权力，授意党羽上书请求赐予九锡。
        【注释】：九锡，古代天子赐给诸侯、大臣的九种器物，是一种最高礼遇。
        """
    else:
        return "未找到相关原文片段，请尝试询问关于王莽或西汉末年的历史。"


# ==========================================
# 4. 构建处理链条 (Chain)
# ==========================================

# 定义 Prompt
# 注意：我们加入了 {context} 用于检索内容，{chat_history} 用于记忆

prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一位精通《资治通鉴》的历史研读助手。请基于提供的【原文片段】和【背景知识】回答用户问题。"),
    ("user", """
    请分析以下内容：

    【原文片段】：
    {context}

    【用户问题】：
    {input_text}

    {format_instructions}
    """)
])

# 构建核心链条
# 流程：输入 -> 检索原文 -> 填入Prompt -> 模型分析 -> 解析为对象
chain = (
        {
            "context": RunnableLambda(lambda x: mock_retriever(x["input_text"])),  # 模拟检索步骤
            "input_text": RunnablePassthrough(),
            "format_instructions": RunnableLambda(lambda x: parser.get_format_instructions())
        }
        | prompt
        | llm
        | parser
)

# ==========================================
# 5. 包装记忆模块
# ==========================================
message_history = ChatMessageHistory()

chain_with_memory = RunnableWithMessageHistory(
    chain,
    lambda session_id: message_history,
    input_messages_key="input_text",
    history_messages_key="chat_history",
    output_messages_key=None  # <--- 加上这一行，彻底禁用自动输出记录
)
# ==========================================
# 6. 运行演示
# ==========================================
if __name__ == "__main__":
    config = {"configurable": {"session_id": "zizhi_tongjian_bot"}}

    print("📚 资治通鉴研读助手已启动 (输入 'quit' 退出)")

    while True:
        user_input = input("\n👤 请输入你的问题：")
        if user_input.lower() in ['quit', 'exit', '退出']:
            break

        try:
            # 1. 【手动】将用户输入存入历史记录
            # 这样下一次对话时，模型能看到上下文
            message_history.add_user_message(user_input)

            # 2. 调用链条获取结果 (Pydantic 对象)
            # 注意：这里我们直接传入 user_input，因为历史已经手动存了
            result: HistoricalAnalysis = chain.invoke(
                {"input_text": user_input, "context": mock_retriever(user_input),
                 "format_instructions": parser.get_format_instructions()}
            )

            # 3. 【手动】将 AI 结果存入历史记录
            # 这里将对象转为字符串存储，避免对象序列化问题
            message_history.add_ai_message(str(result))

            # 4. 格式化打印 (使用 Pydantic 对象的属性)
            print("\n" + "=" * 30)
            print(f"📜 **事件**：{result.event_title} ({result.event_type})")
            print(f"📍 **地点**：{', '.join(result.locations)}")
            print(f"👥 **人物**：{', '.join(result.key_figures)}")
            print("-" * 30)
            print(f"📝 **摘要**：{result.summary}")
            print(f"💡 **启示**：{result.moral_lesson}")
            if result.is_critical:
                print("⚠️ **注意**：这是历史的关键转折点！")
            print("=" * 30)

        except Exception as e:
            print(f"❌ 分析出错：{e}")



























