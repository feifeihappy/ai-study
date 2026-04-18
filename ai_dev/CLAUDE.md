# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

请始终使用简体中文与我对话。

## 运行命令

```bash
# 安装依赖（在 03-project/ 目录下）
pip install -r 第一阶段/03-project/requirements.txt
pip install langchain-openai

# 启动主应用（资治通鉴助手）
streamlit run 第一阶段/03-project/my_history_app/app.py

# 运行单个学习脚本
python 第一阶段/hello_ai.py
python 第一阶段/async.py
python 基础知识/check_env.py

# Docker 部署
docker build -t history-app 第一阶段/03-project/
docker run -e DASHSCOPE_API_KEY=your_key -p 8501:8501 history-app
```

## 环境变量

```
DASHSCOPE_API_KEY=   # 阿里云 DashScope（主应用使用）
OPENAI_API_KEY=      # DeepSeek 或其他兼容接口
OPENAI_BASE_URL=     # 如 https://api.deepseek.com/v1
```

## 项目结构与学习路径

本仓库是一个 **12 周 AI 工程学习课程**，按阶段组织：

- `基础知识/` — Python 基础、OpenAI API 直调、爬虫示例
- `第一阶段/` — LangChain 基础、提示词工程、生产级应用（主要代码在此）
- `prompts/templates.yaml` — 可复用提示词模板库（学习督导、模拟面试、读书督导）
- `学习路径.md` — 完整 12 周课程规划

## 主应用架构（03-project/my_history_app）

《资治通鉴》研读助手，三层架构：

```
app.py                          # 入口：加载 .env，初始化 HistoricalAnalyzer，调用 render_page()
├── ui/pages/history_page.py    # UI 层：Streamlit 聊天界面，渲染结构化分析卡片
├── logic/analyzer.py           # 逻辑层：LangChain LCEL 链（检索 → 提示词 → 结构化输出）
├── logic/models.py             # 逻辑层：Pydantic Schema（HistoricalAnalysis）
└── data/retriever.py           # 数据层：mock_retriever，签名为 (query: str) -> str
```

**核心数据流**：用户问题 → `analyzer.analyze()` → LangChain 链（`RunnablePassthrough` 并行分发 context 和 input_text）→ `llm.with_structured_output(HistoricalAnalysis)` → UI 渲染结构化卡片。

**LLM 集成**：模型 `qwen-plus`，通过 `langchain_openai.ChatOpenAI` 接入 DashScope OpenAI 兼容接口（`https://dashscope.aliyuncs.com/compatible-mode/v1`），temperature=0.3。

**扩展 RAG**：替换 `data/retriever.py` 中的 `mock_retriever` 为真实向量数据库查询（FAISS、Chroma 等），保持 `(query: str) -> str` 签名不变即可，`analyzer.py` 通过 `self._get_context()` 调用它。

**Dockerfile** 目前指向旧版单文件 `web_app.py`，而非 `my_history_app/`，如需容器化新版需修改。
