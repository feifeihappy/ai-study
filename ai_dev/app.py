from openai import OpenAI

# 1. 初始化客户端
client = OpenAI(
    api_key="",  # <--- ⚠️ 确保这里填对了
    base_url="https://api.deepseek.com"
)

print("🤖 AI 助手已启动！(输入 'quit' 或 'exit' 退出)")

# 2. 创建一个列表来保存聊天记录，这样 AI 能记住上下文
# 先设定一个人设
messages = [
    {"role": "system", "content": "你是一个幽默、博学的助手，回答要简洁有趣。"}
]

while True:
    # 3. 获取用户输入
    user_input = input("\n👤 你: ")

    # 检查是否要退出
    if user_input.lower() in ['quit', 'exit', 'q']:
        print("👋 再见！祝你今天愉快！")
        break

    if not user_input.strip():
        continue

    # 4. 把用户的话加入历史记录
    messages.append({"role": "user", "content": user_input})

    try:
        # 5. 发送请求 (带上之前的聊天记录)
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            temperature=0.7
        )

        # 6. 获取 AI 回复
        ai_reply = response.choices[0].message.content

        # 7. 打印回复
        print(f"🤖 AI: {ai_reply}")

        # 8. 【关键】把 AI 的回复也加入历史记录，否则它下一句就忘了自己说过什么
        messages.append({"role": "assistant", "content": ai_reply})

    except Exception as e:
        print(f"\n❌ 出错了：{e}")
        break