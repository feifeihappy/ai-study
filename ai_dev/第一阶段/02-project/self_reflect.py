from langchain_openai import ChatOpenAI
import os
from dotenv import load_dotenv


load_dotenv()

llm= ChatOpenAI(
    model="qwen-plus",
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
)

# 任务：写一段产品介绍文案

product ="一款能自动记录会议内容并生成纪要的AI工具"


# 第一步：让模型先写初稿
draft_prompt = f"""
请为以下产品写一段产品介绍文案：
{product}

要求：简洁有力，突出核心价值观。
"""
print("正在生成初稿")
draft = llm.invoke(draft_prompt)
print("初稿")
print(draft.content)
print("\n"+"="*50+"\n")

# 第二步：让模型自己检查初稿
critique_prompt  =f"""
你是一位资深文案编辑。请检查以下文案：

原文案：
{draft.content}

请从以下纬度进行评价：
1. 是否突出了核心卖点？
2. 语言是否足够吸引人？
3. 有没有冗余或模糊的表达？

请指出2个可以改进的地方。
"""

print("正在自我反思\n")
critique = llm.invoke(critique_prompt)
print("反思意见")
print(critique.content)
print("\n"+"="*50+"\n")

# 第三步：根据反思意见修改
revise_prompt = f"""
你是一位资深文案编辑。请根据以下反思意见修改原文案：


原文案：
{draft.content}

反思意见：
{critique.content}

请输出修改后的最终文案。
"""

print("正在修改最终定稿")

final = llm.invoke(revise_prompt)
print("最终稿")
print(final.content)
