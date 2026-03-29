import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

# 1. 加载环境变量
load_dotenv()

# 2. 初始化模型 (修改这里！)
llm = ChatOpenAI(
    # 模型名称：通义千问 Plus (或者 Qwen-Turbo, Qwen-Max)
    model="qwen-plus",

    # 阿里云的兼容接口地址 (非常重要！)
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",

    # 填入你的千问 API Key
    api_key=os.getenv("DASHSCOPE_API_KEY")
)


# 3. 定义结构化提示词 (保持不变)
def build_prompt(topic, role, style):
    return f"""
    # 角色
    你是一位{role}。

    # 任务
    请简要介绍“{topic}”。

    # 约束
    1. 必须使用{style}的风格。
    2. 结尾必须用一句话总结核心精神。
    3. 输出格式为 Markdown 列表。
    """


# 4. 运行测试
topic = "项羽"
role = "严厉的中学教导主任"
style = "恨铁不成钢"

prompt = build_prompt(topic, role, style)

print(f"🤖 正在调用通义千问 (Qwen-Plus)...\n")
response = llm.invoke(prompt)

print(response.content)