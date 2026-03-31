from langchain_openai import ChatOpenAI
import os
from dotenv import load_dotenv

load_dotenv()

llm = ChatOpenAI(
    model="qwen-plus",
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
)

# 这就是 Few-Shot 的核心：给例子
examples = """
示例1：
用户说：我饿了
你回复：腹中饥馁，愿乞一餐

示例2：
用户说：你太厉害了
你回复：阁下才情，实乃当世无双

示例3：
用户说：我要走了
你回复：青山不改，绿水长流，就此别过
"""

# 用户的新输入
user_input = "你大爷"

# 组装提示词
prompt = f"""
你是一个古文翻译官，把用户的现代大白话翻译成文言文。
请严格模仿下面的例子风格。

{examples}

现在请翻译：
用户说：{user_input}
你回复："""

print("🚀 发送请求...\n")
response = llm.invoke(prompt)
print(response.content)