"""
retrieval_qa.py — RetrievalQA：LangChain 最简 RAG 链
=============================================
本周一任务：用一行 RetrievalQA 链，替代手动"检索→拼Prompt→LLM"三步。

对比你之前写的 notes_qa_bot.py，那个流程是：
  用户提问 → dashscope.TextEmbedding 向量化 → ChromaDB 检索
  → 手动拼 context 到 Prompt → ChatOpenAI 生成 → 返回答案
  这本质就是 RAG，但每一步都是手写的。

RetrievalQA 做的事完全一样，只是 LangChain 帮你把这些步骤封装成了一条链。

使用方式：
    pip install langchain chromadb langchain-chroma langchain-openai
    python retrieval_qa.py
"""

import os
from dotenv import load_dotenv

# ---------- LangChain 导入 ----------
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_classic.chains import RetrievalQA
from langchain_text_splitters import RecursiveCharacterTextSplitter

# ============================================================
# 0. 配置
# ============================================================

NOTES_DIR = "../01-project/notes"       # 复用之前的笔记目录
CHROMA_PERSIST_DIR = "./chroma_data"    # Chroma 持久化路径（本地模式，无需服务端）
COLLECTION_NAME = "retrieval_qa_demo"
TOP_K = 4

# DashScope 兼容 OpenAI 接口
LLM_BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
LLM_MODEL = "qwen-plus"
EMBEDDING_MODEL = "text-embedding-v3"   # DashScope 的 embedding 模型


def build_knowledge_base():
    """
    第 1 步：构建向量知识库（一次性操作）
    ————————————————————————————————
    把 Markdown 笔记读进来 → 切块 → 向量化 → 存入 ChromaDB。

    这一步和 RetrievalQA 本身无关——任何一个 RAG 系统都需要先建813016库。
    """

    # 1a. 加载文档
    # ----------------------------------------------------------
    # langchain_community.document_loaders 提供了几十种 loader，
    # DirectoryLoader + TextLoader 是处理本地 MD 文件的最简组合。
    from langchain_community.document_loaders import DirectoryLoader, TextLoader

    loader = DirectoryLoader(
        NOTES_DIR,
        glob="**/*.md",       # 只加载 .md 文件
        loader_cls=TextLoader,
        loader_kwargs={"encoding": "utf-8"},
    )
    documents = loader.load()
    print(f"[1/4] 加载了 {len(documents)} 个文档")

    # 1b. 切分文档
    # ----------------------------------------------------------
    # 为什么要切？因为 LLM 上下文窗口有限，且检索精度随 chunk 变小而提高。
    # chunk_size=500：每个片段约 500 字符，适合单次检索返回 3-5 条。
    # chunk_overlap=100：相邻片段重叠 100 字符，防止关键信息被切在边界上。
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100,
        separators=["\n\n", "\n", "。", ".", " ", ""],  # 优先按段落切，保证语义完整
    )
    chunks = text_splitter.split_documents(documents)
    print(f"[2/4] 切分为 {len(chunks)} 个文本块")

    # 1c. 创建 Embeddings 实例
    # ----------------------------------------------------------
    # OpenAIEmbeddings 本质就是调 /v1/embeddings 接口。
    # 我们通过 openai_api_base 指向 DashScope 兼容接口，实现供应商透明切换。
    embeddings = OpenAIEmbeddings(
        model=EMBEDDING_MODEL,
        openai_api_base=LLM_BASE_URL,
        openai_api_key=os.getenv("DASHSCOPE_API_KEY"),
        check_embedding_ctx_length=False,  # DashScope 兼容接口不接受 token ID 列表
    )

    # 1d. 向量化 + 存入 ChromaDB
    # ----------------------------------------------------------
    # Chroma.from_documents 做了三件事：
    #   ① 调用 embeddings 把每个 chunk 转成向量
    #   ② 存入 ChromaDB（persist_directory 指定本地路径）
    #   ③ 返回一个可以直接当 retriever 用的 Chroma 对象
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        collection_name=COLLECTION_NAME,
        persist_directory=CHROMA_PERSIST_DIR,
    )
    print(f"[3/4] 向量化完成，存入 {CHROMA_PERSIST_DIR}")

    return vectorstore


def create_qa_chain(vectorstore):
    """
    第 2 步：创建 RetrievalQA 链（核心）
    ——————————————————————————————————
    这条链就是本节课的主角。

    RetrievalQA 内部自动完成了你之前手写的三步：
      ① retriever.get_relevant_documents(query)   → 从向量库检索相关文档
      ② 把检索结果拼进 Prompt 模板（放在 {context} 占位符）
      ③ LLM 基于 context 生成答案

    你不再需要：
      - 手动调用 dashscope.TextEmbedding
      - 手动拼 context 进 Prompt
      - 手动处理 document 列表

    核心参数：
      - llm：大模型实例
      - retriever：检索器（从 vectorstore 生成）
      - chain_type：链类型，决定了如何把文档"喂"给 LLM
      - return_source_documents：是否返回引用的原文
    """

    llm = ChatOpenAI(
        model=LLM_MODEL,
        openai_api_base=LLM_BASE_URL,
        openai_api_key=os.getenv("DASHSCOPE_API_KEY"),
        temperature=0.3,
    )

    # vectorstore.as_retriever() 包装了向量检索逻辑：
    #   - search_type="similarity"：默认，余弦相似度检索
    #   - search_kwargs={"k": TOP_K}：返回最相似的 4 个文档块
    retriever = vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={"k": TOP_K},
    )

    # RetrievalQA.from_chain_type 是工厂方法，帮你组装整条链。
    # chain_type="stuff" 是最简单的策略：把所有检索到的文档
    # 直接"塞"进 Prompt 的 {context} 位置。
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        chain_type="stuff",           # "stuff" = 全塞进去（最简策略）
        return_source_documents=True,  # 返回原文，方便验证答案来源
    )

    print("[4/4] RetrievalQA 链创建完成")
    return qa_chain


# ============================================================
# 运行入口
# ============================================================

if __name__ == "__main__":
    load_dotenv()

    # -- 如果之前已建库，可以直接加载，跳过 build 步骤 --
    # 首次运行需要 build，之后可以注释掉，直接 load 本地 Chroma 数据
    vectorstore = build_knowledge_base()
    qa = create_qa_chain(vectorstore)

    # ---------- 交互式问答 ----------
    print("\n" + "=" * 60)
    print("📚 RetrievalQA 问答模式（输入 quit 退出）")
    print("=" * 60)

    questions = [
        "什么是 RAG？",
        "LangChain 的核心概念有哪些？",
    ]

    for q in questions:
        print(f"\n🙋 问：{q}")
        # invoke 返回的是 dict，包含 query、result、source_documents
        result = qa.invoke({"query": q})
        print(f"🤖 答：{result['result']}")

        # 展示引用来源
        sources = result.get("source_documents", [])
        if sources:
            print(f"\n📖 引用了 {len(sources)} 个来源：")
            for i, doc in enumerate(sources, 1):
                # 截取前 80 字符显示
                preview = doc.page_content[:80].replace("\n", " ")
                print(f"  [{i}] {preview}...")
