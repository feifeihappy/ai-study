"""
ui/pages/history_page.py
UI层：Streamlit 界面展示
"""
import streamlit as st
from logic.analyzer import HistoricalAnalyzer
from logic.models import HistoricalAnalysis


def render_page(analyzer:HistoricalAnalyzer):
    st.set_page_config(page_title="资质通鉴助手", page_icon="📜")
    st.title("📜 资治通鉴研读助手")

    # 初始化 Session State
    if "messages" not in st.session_state:
        st.session_state.messages = []

    def display_analysis(data: HistoricalAnalysis):
        """渲染分析结果卡片"""
        st.markdown(f"### 📜 {data.event_title}")
        st.markdown(f"**类型**：{data.event_type}")
        st.markdown("---")
        st.markdown(f"**📝 摘要**：{data.summary}")
        st.markdown(f"**💡 启示**：{data.moral_lesson}")


        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"👥 **人物**：{', '.join(data.key_figures)}")
        with col2:
            st.markdown(f"📍 **地点**：{', '.join(data.locations)}")
        if data.is_critical:
            st.markdown("**⚠️ 警告：这是历史的关键转折点！**")

        # --- 显示历史消息 ---

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            if message["role"] == "ai":
                display_analysis(message["content"])
            else:
                st.write(message["content"])

        # --- 处理用户输入 ---
    if prompt_text := st.chat_input("请输入历史人物或事件（例如：王莽受九锡）"):
        # 显示用户输入
        with st.chat_message("user"):
            st.write(prompt_text)
        st.session_state.messages.append({"role": "user", "content": prompt_text})

        # 调用逻辑层
        with st.chat_message("assistant"):
            with st.spinner("思考中..."):
                try:
                    result = analyzer.analyze(prompt_text)
                    display_analysis(result)
                    st.session_state.messages.append({"role": "ai", "content": result})
                except Exception as e:
                    st.error(f"发生错误：{e}")