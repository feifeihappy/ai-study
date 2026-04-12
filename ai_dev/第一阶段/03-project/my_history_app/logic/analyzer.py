"""
logic/analyzer.py
逻辑层：核心分析引擎
"""
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from logic.models import HistoricalAnalysis
from data.retriever import mock_retriever


class HistoricalAnalyzer:
    def __init__(self, api_key: str):
        # 1.初始化模型
        self.llm = ChatOpenAI(
            model="qwen-plus",
            api_key=api_key,
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
            temperature=0.3
        )
        # 2. 定义解析器
        self.parser = self.llm.with_structured_output(HistoricalAnalysis)
        # 3. 构建 Prompt
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", "你是一位精通《资治通鉴》的历史研读助手。请基于提供的【原文片段】回答用户问题。"),
            ("user", """
                    请分析以下内容：
    
                    【原文片段】：
                    {context}
    
                    【用户问题】：
                    {input_text}
                    """)
        ])
        # 4. 构建 Chain
        self.chain = (
                {
                    "context": RunnablePassthrough() | self._get_context,
                    "input_text": RunnablePassthrough()
                }
                | self.prompt
                | self.parser
        )

    def _get_context(self, query):
        """内部方法：获取上下文"""
        return mock_retriever(query)
    def analyze(self,question:str):
        """对外暴露的公共方法：执行分析"""
        return self.chain.invoke({"input_text":question})
