"""
similarity_vs_mmr.py — Similarity Search vs MMR（最大边际相关性）
==============================================================
周二任务：理解两种检索策略的本质区别。

你已会用 similarity search——它把最相似的 top-K 文档直接返回。
但"最相似"不等于"最有用"：4 个结果可能来自同一篇文章的相邻段落，
几乎重复，浪费了 LLM 的上下文窗口。

MMR 在相关性之外加了一个约束：新选中的文档不能和已选中的太像。
这样你拿到的是一组"相关但互不重复"的文档，覆盖更多角度。

运行方式：
    cd 第二阶段/02-project
    pip install langchain langchain-chroma langchain-openai langchain-community
    python similarity_vs_mmr.py
"""

import os
from dotenv import load_dotenv

from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter

# ============================================================
# 0. 配置
# ============================================================

NOTES_DIR = "../01-project/notes"
CHROMA_PERSIST_DIR = "./chroma_data"
COLLECTION_NAME = "similarity_vs_mmr_demo"
TOP_K = 4
FETCH_K = 20          # MMR 先从候选池里拉 20 个，再做多样性筛选
LAMBDA_MULT = 0.5     # 0~1，越大越偏重相关性，越小越偏重多样性

EMBEDDING_MODEL = "text-embedding-v3"
LLM_BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"


def build_knowledge_base():
    """
    第 1 步：构建向量知识库
    —————————————————————
    和 retrieval_qa.py 一样：加载 MD 笔记 → 切块 → 向量化 → 存 Chroma。
    如果本地已有索引，直接加载，跳过重建。
    """
    # 尝试加载已有索引
    if os.path.isdir(CHROMA_PERSIST_DIR):
        try:
            embeddings = _create_embeddings()
            vectorstore = Chroma(
                collection_name=COLLECTION_NAME,
                persist_directory=CHROMA_PERSIST_DIR,
                embedding_function=embeddings,
            )
            # 检查集合是否非空
            if vectorstore._collection.count() > 0:
                print(f"[跳过] 已有索引，直接加载（共 {vectorstore._collection.count()} 条）")
                return vectorstore
        except Exception:
            print("[提示] 检测到旧索引但无法加载，将重建...")

    # ---- 从头构建 ----
    from langchain_community.document_loaders import DirectoryLoader, TextLoader

    loader = DirectoryLoader(
        NOTES_DIR,
        glob="**/*.md",
        loader_cls=TextLoader,
        loader_kwargs={"encoding": "utf-8"},
    )
    documents = loader.load()
    print(f"[1/4] 加载了 {len(documents)} 个文档")

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100,
        separators=["\n\n", "\n", "。", ".", " ", ""],
    )
    chunks = text_splitter.split_documents(documents)
    print(f"[2/4] 切分为 {len(chunks)} 个文本块")

    embeddings = _create_embeddings()

    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        collection_name=COLLECTION_NAME,
        persist_directory=CHROMA_PERSIST_DIR,
    )
    print(f"[3/4] 向量化完成，存入 {CHROMA_PERSIST_DIR}")
    return vectorstore


def _create_embeddings():
    return OpenAIEmbeddings(
        model=EMBEDDING_MODEL,
        openai_api_base=LLM_BASE_URL,
        openai_api_key=os.getenv("DASHSCOPE_API_KEY"),
        check_embedding_ctx_length=False,
    )


def create_dual_retrievers(vectorstore):
    """
    第 2 步：从同一个向量库创建两个检索器
    —————————————————————————————————
    这是本节课的核心对比对象：

    similarity retriever:
      - 纯余弦相似度，选 top-4 最相似的
      - 每个结果"独立最优"，但可能高度重复

    mmr retriever:
      - 先拉 fetch_k=20 个候选，再从里面贪心选出 4 个
      - 每次选都把"和已选结果的相似度"作为惩罚项减去
      - lambda_mult=0.5：相关性和多样性各占一半权重
    """
    sim_retriever = vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={"k": TOP_K},
    )

    mmr_retriever = vectorstore.as_retriever(
        search_type="mmr",
        search_kwargs={
            "k": TOP_K,
            "fetch_k": FETCH_K,
            "lambda_mult": LAMBDA_MULT,
        },
    )

    print(f"[4/4] 双重检索器就绪")
    print(f"       similarity:  k={TOP_K}")
    print(f"       mmr:         k={TOP_K}, fetch_k={FETCH_K}, lambda_mult={LAMBDA_MULT}")
    return sim_retriever, mmr_retriever


# ============================================================
# 3. 对比输出
# ============================================================

def print_side_by_side(query, sim_docs, mmr_docs):
    """用表格并排对比两次检索的结果"""
    max_rows = max(len(sim_docs), len(mmr_docs))
    sim_sources = _count_sources(sim_docs)
    mmr_sources = _count_sources(mmr_docs)

    print(f"\n{'─' * 72}")
    print(f"  查询：「{query}」")
    print(f"{'─' * 72}")
    print(f"  {'Rank':<6} {'similarity (纯相关)':<34} {'mmr λ=0.5 (相关+多样)':<34}")
    print(f"  {'─' * 6} {'─' * 34} {'─' * 34}")

    for i in range(max_rows):
        sim_line = _format_row(sim_docs, i)
        mmr_line = _format_row(mmr_docs, i)

        # 比较两个结果的来源是否相同
        same = _same_source(sim_docs, mmr_docs, i)
        mark = " ✓" if same else " ✗"

        print(f"  #{i + 1:<4}  {sim_line:<34} {mmr_line:<34}{mark}")

    print(f"  {'─' * 6} {'─' * 34} {'─' * 34}")
    print(f"  来源数: similarity={sim_sources}, mmr={mmr_sources}")
    if sim_sources == mmr_sources:
        print(f"  → 两者多样性相同")
    elif mmr_sources > sim_sources:
        pct = int((mmr_sources - sim_sources) / max(sim_sources, 1) * 100)
        print(f"  → MMR 多样性提升 +{pct}%")
    else:
        print(f"  → similarity 多样性更高（少见情况）")


def _format_row(docs, idx):
    """格式化一行：截取内容前 32 字符"""
    if idx >= len(docs):
        return ""
    content = docs[idx].page_content[:32].replace("\n", " ")
    return f"{content}…"


def _same_source(sim_docs, mmr_docs, idx):
    """判断两个结果在同一位置是否来自相同源文件"""
    if idx >= len(sim_docs) or idx >= len(mmr_docs):
        return False
    s1 = sim_docs[idx].metadata.get("source", "")
    s2 = mmr_docs[idx].metadata.get("source", "")
    return os.path.basename(s1) == os.path.basename(s2)


def _count_sources(docs):
    """统计检索结果覆盖了多少个不同的源文件"""
    sources = set()
    for d in docs:
        src = d.metadata.get("source", "unknown")
        sources.add(os.path.basename(src))
    return len(sources)


def print_explanation():
    """打印 MMR 的核心原理解释"""
    print("\n" + "=" * 72)
    print("  三个核心原理")
    print("=" * 72)

    print("""
原理 1：相似性搜索的「贪心陷阱」
─────────────────────────────────
想象你问图书管理员："推荐几本烹饪书"。
纯 similarity search 的做法：找到最像的那本《烹饪大全》，然后发现它的
第 2 章也很像、第 3 章也很像……于是给你同一本书的 4 个不同章节。
——精准度满分，覆盖面零分。你学到的只是"一本烹饪书"，不是"烹饪"。

原理 2：MMR = 相关性 - 冗余度
─────────────────────────────────
MMR 是一个贪心选择算法，每次选下一个文档时：

  score = λ × sim(query, doc) - (1-λ) × max_sim(doc, already_picked)

  第 1 项（相关性）：这个文档和你的问题有多相关？（和 similarity 一样）
  第 2 项（冗余度）：这个文档和我已经选中的文档有多像？越像扣分越多
  λ（lambda_mult）：调节旋钮，决定"相关性"和"多样性"谁更重要

同一本书换了策略：一本烹饪基础 + 一本烘焙指南 + 一本刀工手册 + 一本
厨房安全。你失去了一点点"最精准"，但获得了对"烹饪"的完整理解。

原理 3：lambda_mult 旋钮的三个挡位
─────────────────────────────────
  0.7 - 1.0  → 接近纯 similarity。适合 FAQ 机器人，要的是"标准答案"
  0.4 - 0.6  → 平衡模式（推荐默认值）。适合通用知识检索
  0.1 - 0.3  → 高度多样化。适合头脑风暴、探索性搜索、"给我不同视角"

理解这三个挡位比记住公式重要得多。实际调优时你只需要决定：
"用户要的是精准答案，还是多角度覆盖？"然后拨动这个旋钮。
""")


# ============================================================
# 4. 运行入口
# ============================================================

if __name__ == "__main__":
    load_dotenv()

    vectorstore = build_knowledge_base()
    sim_ret, mmr_ret = create_dual_retrievers(vectorstore)

    # ---------- 三组测试查询 ----------
    # 每组都设计为让 similarity 和 MMR 产生明显差异
    test_queries = [
        "什么是 RAG？",
        "Python 有哪些高效编程技巧？",
        "LangChain 的核心概念是什么？",
    ]

    print(f"\n{'=' * 72}")
    print(f"  Similarity Search vs MMR 对比实验")
    print(f"{'=' * 72}")

    for query in test_queries:
        sim_results = sim_ret.invoke(query)
        mmr_results = mmr_ret.invoke(query)
        print_side_by_side(query, sim_results, mmr_results)

    # ---------- 原理讲解 ----------
    print_explanation()

    # ---------- 微型挑战 ----------
    print("=" * 72)
    print("  微型挑战：调节 lambda_mult 旋钮")
    print("=" * 72)
    print("""
请完成以下三步，把你的答案写在文件末尾的注释里：

  1. 把文件顶部的 LAMBDA_MULT = 0.5 改成 0.3，重新运行。
     观察：MMR 列的结果变得更"杂"了吗？来源文件数有没有增加？

  2. 再改成 0.9，重新运行。
     观察：MMR 列的结果是否几乎和 similarity 列一样了？为什么？

  3. 思考：你要构建两个搜索系统：
     - 系统 A：公司 FAQ 机器人，"我的年假有几天？"——用户要一个确定的答案
     - 系统 B：产品设计师的研究助手，"AI 交互界面的新趋势有哪些？"
     分别该设 lambda_mult 为多少？为什么？

把你的答案写在下方（用代码注释即可）：
""")

    print("─" * 72)
    print("💡 提示：两个检索器来自同一个向量库，唯一的区别就是 search_type 参数。")
    print("   这意味着你不需要重建索引、不需要换数据库——改一行参数就能切换策略。")
