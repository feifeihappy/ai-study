from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
from typing import List, Literal
import os
from dotenv import load_dotenv

load_dotenv()

# 1. 定义结构 (我们要的 JSON 格式)
class TicketAnalysis(BaseModel):
    priority: Literal["High", "Medium", "Low"] = Field(description="根据用户情绪和问题严重性判断优先级")
    user_mood: str = Field(description="用户的情绪形容词，如愤怒、困惑、失望")
    issues: List[str] = Field(description="提取出的具体问题点列表")
    suggested_reply: str = Field(description="客服建议回复，需语气委婉且专业")

# 2. 初始化模型
llm = ChatOpenAI(
    model="qwen-plus",
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
)

# 3. 绑定结构化输出
structured_llm = llm.with_structured_output(TicketAnalysis)

# 4. 模拟一个复杂的用户抱怨
user_input = """
你们这软件怎么回事？我刚充值的会员居然没法用！
而且每次打开都闪退，简直是垃圾！
我已经试过重启了，根本没用。
再不解决我就去投诉平台曝光你们，还要退款！
"""

print(f"🚨 收到工单：\n{user_input}\n")
print("🤖 正在分析并生成 JSON...\n")

# 5. 关键：提示词里强制要求“先思考”
# 虽然 with_structured_output 会强制 JSON，但我们在 Prompt 里加入 CoT 指令
# 可以让模型在生成 JSON 字段之前，先在内部“过一遍逻辑”
prompt = f"""
请分析以下用户反馈。
为了确保准确性，请先在内心一步步思考：
1. 用户遇到了哪些具体的技术问题？
2. 用户的情绪状态如何？是否有流失风险？
3. 基于严重程度，应该定什么优先级？
4. 构思一个安抚性的回复。

思考完毕后，请严格按照 JSON 格式输出结果。

用户反馈内容：{user_input}
"""

# 6. 调用
result = structured_llm.invoke(prompt)

# 7. 展示结果
print("✅ 分析完成！提取结果：")
print(f"优先级: {result.priority}")
print(f"情绪: {result.user_mood}")
print(f"问题: {result.issues}")
print("-" * 30)
print(f"建议回复: {result.suggested_reply}")