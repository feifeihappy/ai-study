# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

请始终使用简体中文与我对话。

## 运行应用

```bash
# 配置环境变量（需要阿里云 DashScope 的 API Key）
echo "DASHSCOPE_API_KEY=your_key" > .env

# 安装依赖（在父目录 03-project/ 下）
pip install -r ../requirements.txt
pip install langchain-openai  # requirements.txt 中未列出，但运行必需

# 启动 Streamlit 应用
streamlit run app.py
```

## Docker（父目录）

Dockerfile 位于父目录 `../`（03-project/），目前指向重构前的单文件版本 `web_app.py`，而非本分层应用：

```bash
docker build -t history-app ../
docker run -e DASHSCOPE_API_KEY=your_key -p 8501:8501 history-app
```

## 架构概览

本项目是一个基于 Streamlit 的《资治通鉴》研读助手，采用三层架构：

```
app.py                          # 入口：加载 .env，初始化 HistoricalAnalyzer，调用 render_page()
├── ui/pages/history_page.py    # UI 层：Streamlit 聊天界面，渲染结构化分析卡片
├── logic/analyzer.py           # 逻辑层：LangChain 链（检索 → 提示词 → 结构化输出）
├── logic/models.py             # 逻辑层：LLM 结构化输出的 Pydantic Schema
└── data/retriever.py           # 数据层：模拟检索器（向量数据库的占位实现）
```

### 核心数据流

1. 用户在聊天界面提交问题
2. `render_page()` 调用 `analyzer.analyze(question)`
3. `HistoricalAnalyzer.chain` 执行：
   - `RunnablePassthrough` 将查询同时分发给 `context`（经由 `mock_retriever`）和 `input_text`
   - 提示词模板填充 `{context}` 和 `{input_text}`
   - `llm.with_structured_output(HistoricalAnalysis)` 返回经过验证的 Pydantic 对象
4. UI 将 `HistoricalAnalysis` 各字段渲染为结构化卡片

### LLM 集成

- 模型：`qwen-plus`，通过 `langchain_openai.ChatOpenAI` 接入 DashScope 的 OpenAI 兼容接口（`https://dashscope.aliyuncs.com/compatible-mode/v1`）
- 结构化输出：使用 `with_structured_output(HistoricalAnalysis)` 强制约束，Schema 定义在 `logic/models.py`

### 数据层扩展

`data/retriever.py` 目前的 `mock_retriever` 仅处理王莽相关查询。若要接入真实检索，用向量数据库查询（如 FAISS、Chroma）替换 `mock_retriever`，保持 `(query: str) -> str` 签名不变即可——`analyzer.py` 通过 `self._get_context()` 调用它。
