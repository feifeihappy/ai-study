import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

# 1. 初始化配置 (保持不变)
load_dotenv()
llm = ChatOpenAI(
    model="deepseek-chat",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)


# 2. 定义 Prompt 模板
# 使用 f-string 的变体，这里只是展示结构
def create_prompt(text):
    return f"""
    请阅读以下文本，完成两个任务：
    1. 用简练的语言总结核心内容（100字以内）。
    2. 提取文本中的名言名句（如有）。

    ---
    {text}
    ---
    """


# 3. 获取当前目录下所有 .md 文件
# 这一步替代了手动指定文件名
target_files = [f for f in os.listdir('.') if f.endswith('.md')]

print(f"🔍 发现 {len(target_files)} 个文档，开始批量处理...\n")

# 4. 循环处理
for filename in target_files:
    # 跳过刚才生成的摘要文件，防止死循环
    if filename.endswith("_摘要.md"):
        continue

    try:
        # --- 读取 ---
        with open(filename, "r", encoding="utf-8") as f:
            content = f.read()

        if not content.strip():
            continue

        # --- 调用 AI ---
        print(f"🤖 正在处理: {filename} ...")
        response = llm.invoke(create_prompt(content))
        summary = response.content

        # --- 保存 (关键点) ---
        # 动态生成新文件名：原文件名 + "_摘要.md"
        # 例如：项羽本纪.md -> 项羽本纪_摘要.md
        output_filename = filename.replace(".md", "_摘要.md")

        with open(output_filename, "w", encoding="utf-8") as f:
            f.write(summary)

        print(f"✅ {filename} 处理完成，已保存为 {output_filename}\n")

    except Exception as e:
        print(f"❌ 处理 {filename} 时出错: {e}")

print("🎉 所有文档处理完毕！")