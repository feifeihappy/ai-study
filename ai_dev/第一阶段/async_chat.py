import asyncio
import os
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate

# 1. 加载环境变量
load_dotenv()


# 2. 定义结构化输出模型 (类似 Java DTO)
class JokeResponse(BaseModel):
    setup: str = Field(description="笑话的铺垫部分")
    punchline: str = Field(description="笑话的笑点部分")
    rating: int = Field(description="笑话的有趣程度评分 (1-10)", ge=1, le=10)


# 3. 初始化 LLM (配置异步客户端)
# 注意：langchain_openai 自动处理了底层的 openai SDK 异步逻辑
llm = ChatOpenAI(
    model="deepseek-chat",       # <--- 修改这里：指定 DeepSeek 的模型名
    # 或者使用推理模型: model="deepseek-reasoner"
    temperature=0.7,
    streaming=True,
    # 不需要在这里写 base_url 和 api_key，它会自动从环境变量读取
)


async def main():
    print("🤖 AI 架构师助手启动... (按 Ctrl+C 停止)\n")

    # 4. 构建提示词模板 (修改这里！)
    # 我们显式地告诉模型需要返回的字段，甚至给出一个示例
    prompt = ChatPromptTemplate.from_messages([
        ("system", """你是一个幽默的助手。
        你的任务是根据用户提供的主题讲一个笑话。

        【重要约束】
        你必须严格按照以下 JSON 格式返回数据，不要包含任何多余的文字或 Markdown 标记：
        {{
            "setup": "笑话的铺垫部分",
            "punchline": "笑话的笑点部分",
            "rating": 1-10 的整数评分
        }}
        """),
        ("human", "请讲一个关于 {topic} 的笑话。")
    ])

    # 5. 绑定输出解析器 (强制 LLM 输出符合 Pydantic 模型的 JSON)
    parser = PydanticOutputParser(pydantic_object=JokeResponse)

    # 构建链：Prompt -> LLM -> Parser
    # 在 LangChain V1+ 中，使用 | 符号连接组件 (类似 Unix Pipe)
    chain = prompt | llm | parser

    topic = "程序员"

    try:
        print(f"📝 主题：{topic}\n")
        print("⏳ 正在生成笑话 (流式接收中)...\n")

        # 6. 异步流式调用 (ainvoke_stream 是伪代码，实际需用 astream 或特定方法)
        # LangChain 的 astream 返回的是异步生成器
        async for chunk in chain.astream({"topic": topic}):
            # chunk 这里已经是解析后的 Pydantic 对象片段或完整对象
            # 注意：PydanticOutputParser 通常在流式结束时才返回完整对象
            # 为了演示流式，我们通常直接流式输出文本，最后再解析。
            # 但为了简化演示，这里我们演示“流式文本” + “最终结构化验证”的组合。
            pass

        # 修正：为了真正展示流式效果，我们暂时去掉 Parser 进行流式打印，
        # 然后再演示一次带 Parser 的结构化调用。

        # --- 演示 A: 纯文本流式 (用户体验最好) ---
        print("--- [演示 A: 流式文本输出] ---")
        text_chain = prompt | llm
        full_response = ""
        async for chunk in text_chain.astream({"topic": topic}):
            content = chunk.content
            print(content, end="", flush=True)
            full_response += content
        print("\n")

        # --- 演示 B: 结构化输出 (后端集成必备) ---
        print("--- [演示 B: 结构化数据提取] ---")
        structured_chain = prompt | llm | parser
        # 结构化通常等待完整响应，但底层仍是异步
        result: JokeResponse = await structured_chain.ainvoke({"topic": topic})

        print(f"✅ 解析成功！")
        print(f"   铺垫: {result.setup}")
        print(f"   笑点: {result.punchline}")
        print(f"   评分: {'⭐' * result.rating} ({result.rating}/10)")

    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        print("💡 提示：请检查 .env 中的 API_KEY 是否正确，或网络连接是否正常。")


if __name__ == "__main__":
    # 运行异步主函数
    asyncio.run(main())