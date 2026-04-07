from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv
import os
import yaml

load_dotenv()

# 1. 初始化模型
llm = ChatOpenAI(
    model="qwen-plus",
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    temperature=0.7,
)

# 2. 定义三个步骤的 Prompt

# 步骤 A: 翻译
translate_prompt = ChatPromptTemplate.from_template("请将以下文言文翻译成白话文：\n{input_text}")

# 步骤 B: 润色
polish_prompt = ChatPromptTemplate.from_template("请润色以下白话文，使其更具学术风格，用词更精准：\n{input_text}")
# 摘要
abstract_prompt = ChatPromptTemplate.from_template("在结尾加一句摘要，总结这段历史：\n{input_text}")

# 步骤 C: 格式化
format_prompt = ChatPromptTemplate.from_template(
    "请将以下内容包装成 Markdown 代码块格式，并在开头加一句点评：\n{input_text}")

# 定义链条
# 流程：翻译Prompt -> 模型 -> 润色Prompt -> 模型 -> 格式化Prompt -> 模型 -> 输出字符串
chain = (translate_prompt | llm | StrOutputParser() | polish_prompt | llm | StrOutputParser()|abstract_prompt | llm | StrOutputParser() | format_prompt | llm | StrOutputParser())

original_text = "五月，策命￼安汉公莽以九锡，莽稽首再拜，受绿韨￼，衮冕￼、衣裳￼，玚琫￼、玚珌￼，句履￼，鸾路￼、乘马￼，龙旂九旒￼，皮弁￼、素积￼，戎路￼、乘马￼，彤￼弓矢、卢￼弓矢，左建朱钺￼，右建金戚￼，甲、胄￼一具，秬鬯￼二卣￼，圭瓒￼二，九命￼青玉珪二，朱户￼，纳陛￼，署￼宗官￼、祝官￼、卜官￼、史官￼，虎贲￼三百人。"
print("🚀 开始流水线处理...")
result =chain.invoke({"input_text":original_text})

print("\n✅ 最终结果：")
print(result)
