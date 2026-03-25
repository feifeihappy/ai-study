import streamlit as st
from openai import OpenAI

# 1. 设置页面标题和图标
st.set_page_config(page_title="我的 AI 助手", page_icon="🤖")

st.title("🤖 我的专属 AI 聊天机器人")
st.caption("由 Streamlit + DeepSeek 驱动")

# 2. 初始化客户端 (建议从环境变量读取，这里先硬编码方便测试)
# ⚠️ 实际部署时请不要把 Key 直接写在代码里上传到 GitHub
api_key = ""
base_url = "https://api.deepseek.com"

client = OpenAI(api_key=api_key, base_url=base_url)

# 3. 初始化会话状态 (这是网页版的“记忆”)
# 每次用户点击按钮，网页都会重新运行，所以需要用 st.session_state 来保存聊天记录
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "你是一个幽默、博学的助手，回答要简洁有趣。"}
    ]

# 4. 显示历史聊天记录
for message in st.session_state.messages:
    if message["role"] != "system":  # 不显示系统人设
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# 5. 处理用户输入
if prompt := st.chat_input("请输入你想问的问题..."):
    # 显示用户消息
    with st.chat_message("user"):
        st.markdown(prompt)

    # 保存用户消息到历史
    st.session_state.messages.append({"role": "user", "content": prompt})

    # 生成 AI 回复
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("正在思考... 🧠")

        try:
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=st.session_state.messages,
                temperature=0.7
            )
            ai_reply = response.choices[0].message.content
            message_placeholder.markdown(ai_reply)

            # 保存 AI 回复到历史
            st.session_state.messages.append({"role": "assistant", "content": ai_reply})
        except Exception as e:
            message_placeholder.error(f"出错了: {e}")