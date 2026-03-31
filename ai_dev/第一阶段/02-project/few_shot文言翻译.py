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
# response = llm.invoke(prompt)
# print(response.content)

#
#
# # question = "一个球拍和一个球一共1.10美元，球拍比球贵1美元，问球多少钱？"
# question = "甲、乙、丙三个人排队。已知：甲不在第一个位置，乙不在最后一个位置，丙在甲的后面。问三个人的顺序是什么？"
#
# # 方法1：直接问，不给提示
# prompt1 = f"请回答：{question}"
# print("🚀 方法1：直接问\n")
# response1 = llm.invoke(prompt1)
# print(response1.content)
# print("\n" + "="*40 + "\n")
#
# # 方法2：用 CoT，让它一步步思考
# prompt2 = f"""
# 请回答：{question}
#
# 请一步步思考，写出你的推理过程，最后再给出答案。
# """
# print("🚀 方法2：用思维链\n")
# response2 = llm.invoke(prompt2)
# print(response2.content)


question = "甲、乙、丙三个人排队。已知：甲不在第一个位置，乙不在最后一个位置，丙在甲的后面。问三个人的顺序是什么？"

prompt = f"""
请回答：{question}

请一步步思考，写出你的推理过程，最后再给出答案。
"""

print("🚀 开始推理...\n")
response = llm.invoke(prompt)
print(response.content)