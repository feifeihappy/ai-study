# AGENTS.md

This file provides guidance to Qoder (qoder.com) when working with code in this repository.

## 项目定位

本仓库是一个 **12 周 AI 工程学习课程** 的代码库，按周组织为 `基础知识/`、`第一阶段/`、`第二阶段/` 等目录。`学习路径.md` 是完整课程规划，包含每周学习目标和每日任务。

代码分为两类：
- **学习脚本**：每周独立的练习脚本，用于演示单一概念（如 Prompt 工程、Embedding、Chain）。
- **主应用**：`第一阶段/03-project/my_history_app/` 是一个完整的《资治通鉴》研读助手，三层架构，使用 Streamlit + LangChain + DashScope。

## 常用命令

```bash
# 安装主应用依赖（在 03-project 目录下执行）
pip install -r 第一阶段/03-project/requirements.txt
pip install langchain-openai

# 启动主应用（Streamlit 资治通鉴助手）
streamlit run 第一阶段/03-project/my_history_app/app.py

# 运行独立学习脚本
python 第一阶段/hello_ai.py          # DeepSeek API 初体验
python 第一阶段/async.py             # 异步调用演示
python 基础知识/check_env.py         # 检查 Python 环境
python 第二阶段/01-project/embedding_test.py  # Embedding + 语义搜索

# Docker 构建（注意：当前 Dockerfile 指向旧版单文件 web_app.py）
docker build -t history-app 第一阶段/03-project/
docker run -e DASHSCOPE_API_KEY=your_key -p 8501:8501 history-app
```

## 主应用架构（03-project/my_history_app）

三层架构，数据流为 **Streamlit UI → LangChain LCEL Chain → 结构化输出 → 卡片渲染**。

```
app.py                          # 入口：加载 .env，初始化 HistoricalAnalyzer，调用 render_page()
├── ui/pages/history_page.py    # UI 层：Streamlit 聊天界面，渲染结构化分析卡片
├── logic/analyzer.py           # 逻辑层：LangChain LCEL 链
├── logic/models.py             # 逻辑层：Pydantic Schema（HistoricalAnalysis）
└── data/retriever.py           # 数据层：mock_retriever，签名为 (query: str) -> str
```

**Chain 构建细节**（需阅读多文件才能理解）：

1. `analyzer.py` 使用 `RunnablePassthrough` 并行分发：
   - `context` 分支调用 `self._get_context()` → 最终落到 `data/retriever.py` 的 `mock_retriever()`
   - `input_text` 分支透传用户原始输入
2. 两个分支的输出通过 `|` 送入 `ChatPromptTemplate`，再送入 `llm.with_structured_output(HistoricalAnalysis)`
3. `history_page.py` 接收的是 Pydantic 对象，直接通过属性访问渲染卡片（`data.event_title`、`data.key_figures` 等）

**扩展 RAG 的约定**：`data/retriever.py` 中的 `mock_retriever` 必须保持 `(query: str) -> str` 签名。替换为真实向量数据库查询（FAISS、Chroma 等）时，`analyzer.py` 通过 `self._get_context()` 调用它，无需改动链的构建逻辑。

## LLM 集成方式

主应用使用 `langchain_openai.ChatOpenAI` 接入阿里云 DashScope 的 OpenAI 兼容接口：

- 模型：`qwen-plus`
- Base URL：`https://dashscope.aliyuncs.com/compatible-mode/v1`
- Temperature：`0.3`
- 环境变量：`DASHSCOPE_API_KEY`

部分早期学习脚本（如 `hello_ai.py`）使用 DeepSeek 接口，依赖 `DEEPSEEK_API_KEY` 和 `OPENAI_BASE_URL`。

## 提示词模板库

`prompts/templates.yaml` 是可复用的提示词模板库，包含：
- `study_supervisor` — 学习督导
- `mock_interview` — 模拟面试
- `reading_supervisor` — 读书督导

## 已知问题

- **Dockerfile 入口陈旧**：`第一阶段/03-project/Dockerfile` 的 `CMD` 指向 `web_app.py`（旧版单文件实现），而非 `my_history_app/app.py`。如需容器化新版，需修改入口文件路径。
- **无测试套件**：本项目为学习性质，没有 pytest 或其他测试框架配置。修改后通过手动运行脚本验证。
- **无 lint/typecheck 配置**：未配置 ruff、mypy 等工具。
