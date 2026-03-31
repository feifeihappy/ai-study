from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
import os
from dotenv import load_dotenv
import json

load_dotenv()

# 1. 定义我们要的结构 (用 Pydantic)
# 这相当于给模型定义了 JSON 的 Schema
class ReviewExtract(BaseModel):
    product: str = Field(description="用户评价的产品名称")
    rating: int = Field(description="用户给出的评分，1到5分")
    sentiment: Literal["positive", "negative", "neutral"] = Field(description="情感倾向")
    keywords: list[str] = Field(description="提取的关键形容词")

# 2. 初始化模型
llm = ChatOpenAI(
    model="qwen-plus",
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
)

# 3. 关键一步：绑定结构化输出
# 这一步会自动把 Pydantic 的格式说明塞进提示词里，强制模型遵守
structured_llm = llm.with_structured_output(ReviewExtract)

# 4. 用户的“乱七八糟”的评论
user_comment = "这双跑鞋穿着太舒服了，而且颜值很高，就是价格有点贵，不过还是值得入手！"

print(f"📝 正在分析评论：{user_comment}\n")

# 5. 调用
result = structured_llm.invoke(user_comment)

# 6. 处理结果
# 注意：result 现在直接就是一个 ReviewExtract 对象，不是字符串了！
print("✅ 提取成功！Python 对象内容：")
print(result)
print("\n" + "="*30 + "\n")

# 如果你想转成 JSON 字符串给前端用
json_str = result.model_dump_json(indent=2)
print("📦 对应的 JSON 格式：")
print(json_str)