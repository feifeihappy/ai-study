"""
app.py
应用入口
"""
import os
from dotenv import load_dotenv
from ui.pages.history_page import render_page
from logic.analyzer import HistoricalAnalyzer


def main():
    # 加载环境变量
    load_dotenv()

    # 初始化核心组件
    api_key = os.getenv("DASHSCOPE_API_KEY")
    if not api_key:
        raise ValueError("请在 .env 文件中设置 DASHSCOPE_API_KEY")

    analyzer = HistoricalAnalyzer(api_key)

    # 渲染页面
    render_page(analyzer)


if __name__ == "__main__":
    main()