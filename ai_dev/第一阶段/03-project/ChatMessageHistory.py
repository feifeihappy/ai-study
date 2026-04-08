from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from dotenv import load_dotenv
import os

load_dotenv()

load_dotenv()

# 1. 初始化模型
llm = ChatOpenAI(
    model="qwen-plus",
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    temperature=0.7,
)

# 2. 创建基础的 chain
prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个专业的历史学家，擅长分析古代政治事件。"),
    ("placeholder", "{chat_history}"),  # 这行代码是灵魂，它告诉LangChain：把历史记录放在这里
    ("user", "{input_text}")
])

chain = prompt | llm


# 1. 创建一个"笔记本"

message_history = ChatMessageHistory()

# 2. 把你之前的链条包装一下
# 注意：这里不需要改原来的 chain，直接包装就行

chain_with_history = RunnableWithMessageHistory(
    chain,
    lambda session_id: message_history,  # 返回历史记录对象
    input_messages_key="input_text",  # 输入的消息字段
    history_messages_key="chat_history"  # 历史记录字段
)

# 3. 开始对话
config = {"configurable":{"session_id":"chat1"}}

# 第一轮
result1 = chain_with_history.invoke(
    {"input_text":"王莽是谁？"},
    config=config
)

print(result1.content)

print("\n" + "=" * 30)
# 第二轮（模型记得上一轮）
result2 = chain_with_history.invoke(
    {"input_text": "他后来怎么样了？"},
    config=config
)
print(result2.content)