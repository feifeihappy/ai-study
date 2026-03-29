import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

# 1. 加载环境变量
load_dotenv()

# 2. 从环境变量中获取 API Key
api_key = os.getenv("DEEPSEEK_API_KEY")

# 3. 初始化模型
# 注意：base_url 需要指向 DeepSeek 的接口地址
llm = ChatOpenAI(
    model="deepseek-chat",
    api_key=api_key,
    base_url="https://api.deepseek.com"
)

# 4. 调用模型
response = llm.invoke("请用一句话介绍你自己")

# 5. 打印结果
print(response.content)