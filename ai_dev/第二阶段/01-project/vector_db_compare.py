"""
vector_db_compare.py — FAISS vs ChromaDB 向量库对比实验
=====================================================
第5周周日任务：用相同的文档和 Embedding，对比两种向量库的差异。

FAISS（Facebook AI Similarity Search）：
  - 定位：高性能向量**索引库**，不是数据库
  - 纯内存运算，依赖 CPU/GPU 做近似最近邻搜索（ANN）
  - 没有服务端、没有持久化（需手动 save/load）、没有元数据过滤
  - 适合：研究实验、百万级向量高速检索、嵌入到已有系统

ChromaDB：
  - 定位：向量**数据库**，开箱即用的完整存储方案
  - 内置持久化、元数据过滤、Collection 管理、REST API
  - 适合：生产级 RAG 应用、团队共享知识库

使用方式：
    pip install faiss-cpu
    python vector_db_compare.py
"""

import os
import time
import numpy as np
from typing import List, Tuple

from dotenv import load_dotenv
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
import dashscope
from dashscope import TextEmbedding
import faiss
from chromadb import HttpClient


# ============================================================
# 0. 配置
# ============================================================

NOTES_DIR = "./notes"
COLLECTION_NAME = "compare_test"
CHROMA_HOST = "localhost"
CHROMA_PORT = 8000
CHUNK_SIZE = 500
CHUNK_OVERLAP = 80
TOP_K = 3


def init_config():
    load_dotenv()
    api_key = os.getenv("DASHSCOPE_API_KEY")
    if not api_key:
        raise ValueError("请设置 DASHSCOPE_API_KEY")
    dashscope.api_key = api_key
    return api_key


# ============================================================
# 1. 加载文档（和之前完全一样的逻辑）
# ============================================================

def load_and_split(notes_dir: str) -> Tuple[List[Document], np.ndarray, List[str]]:
    """加载笔记并分割，返回 documents + embeddings + texts"""
    if not os.path.isdir(notes_dir):
        raise FileNotFoundError(f"笔记目录不存在: {notes_dir}")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", "。", ".", " ", ""],
    )

    documents = []
    md_files = sorted([f for f in os.listdir(notes_dir) if f.endswith(".md")])

    for filename in md_files:
        filepath = os.path.join(notes_dir, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        chunks = splitter.split_text(content)
        for i, chunk in enumerate(chunks):
            documents.append(Document(
                page_content=chunk,
                metadata={"source": filename, "chunk_index": i}
            ))

    # 批量向量化
    embeddings_list = []
    texts = []
    for i, doc in enumerate(documents):
        resp = TextEmbedding.call(
            model=TextEmbedding.Models.text_embedding_v2,
            input=doc.page_content,
        )
        if resp.status_code != 200:
            raise Exception(f"向量化失败 chunk {i}: {resp.message}")
        embeddings_list.append(resp.output["embeddings"][0]["embedding"])
        texts.append(doc.page_content)

    embeddings_array = np.array(embeddings_list, dtype=np.float32)
    print(f"📄 加载 {len(md_files)} 个文件 → {len(documents)} 个 chunk, 向量维度 {embeddings_array.shape[1]}\n")
    return documents, embeddings_array, texts


# ============================================================
# 2. FAISS 索引构建与检索
# ============================================================

class FAISSIndex:
    """
    FAISS 封装：用 IndexFlatIP 做内积搜索（等价于余弦相似度，前提是向量已归一化）。

    为什么用 IndexFlatIP？
    - IndexFlatIP 是暴力内积搜索，100% 精确
    - 数据量大时可以用 IndexIVFFlat（倒排索引 + 量化）来提速
    - L2 距离也用 IndexFlatL2，但学术界更常用内积/余弦
    """

    def __init__(self, dimension: int):
        self.dimension = dimension
        self.index: faiss.IndexFlatIP | None = None
        self.texts: List[str] = []
        self.metadatas: List[dict] = []

    def build(self, embeddings: np.ndarray, documents: List[Document]):
        """
        构建 FAISS 索引。

        关键步骤：
        1. 对向量做 L2 归一化 → 内积搜索 = 余弦相似度
        2. 创建 IndexFlatIP 并添加向量
        """
        faiss.normalize_L2(embeddings)

        self.index = faiss.IndexFlatIP(self.dimension)
        self.index.add(embeddings)
        self.texts = [doc.page_content for doc in documents]
        self.metadatas = [doc.metadata for doc in documents]

        print(f"  ✅ FAISS 索引构建完成: {self.index.ntotal} 条向量")

    def search(self, query_embedding: np.ndarray, k: int = TOP_K):
        """检索：对查询向量同样做归一化，然后搜索"""
        if self.index is None:
            raise RuntimeError("请先 build 索引")

        query = query_embedding.reshape(1, -1).astype(np.float32)
        faiss.normalize_L2(query)

        scores, indices = self.index.search(query, k)
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx >= 0 and idx < len(self.texts):
                results.append((self.texts[idx], self.metadatas[idx], float(score)))
        return results


# ============================================================
# 3. ChromaDB 索引构建与检索
# ============================================================

class ChromaIndex:
    """ChromaDB 封装：和 notes_qa_bot.py 中一样的逻辑"""

    def __init__(self):
        self.client = HttpClient(host=CHROMA_HOST, port=CHROMA_PORT)

    def build(self, embeddings: np.ndarray, documents: List[Document]):
        try:
            self.client.delete_collection(name=COLLECTION_NAME)
        except Exception:
            pass

        self.collection = self.client.create_collection(
            name=COLLECTION_NAME,
            metadata={"description": "FAISS vs ChromaDB 对比测试"},
        )

        ids = [f"doc_{i}" for i in range(len(documents))]
        texts = [doc.page_content for doc in documents]
        metadatas = [doc.metadata for doc in documents]

        batch_size = 50
        for i in range(0, len(ids), batch_size):
            self.collection.add(
                ids=ids[i:i + batch_size],
                documents=texts[i:i + batch_size],
                embeddings=embeddings[i:i + batch_size].tolist(),
                metadatas=metadatas[i:i + batch_size],
            )

        print(f"  ✅ ChromaDB 索引构建完成: {self.collection.count()} 条向量")

    def search(self, query_embedding: np.ndarray, k: int = TOP_K):
        results = self.collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=k,
        )
        retrieved = []
        for text, meta, distance in zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0],
        ):
            retrieved.append((text, meta, distance))
        return retrieved


# ============================================================
# 4. 查询向量化（共享）
# ============================================================

def embed_query(query: str) -> np.ndarray:
    """把查询文本转为向量"""
    resp = TextEmbedding.call(
        model=TextEmbedding.Models.text_embedding_v2,
        input=query,
    )
    if resp.status_code != 200:
        raise Exception(f"查询向量化失败: {resp.message}")
    return np.array(resp.output["embeddings"][0]["embedding"], dtype=np.float32)


# ============================================================
# 5. 对比实验主流程
# ============================================================

def run_comparison():
    print("╔══════════════════════════════════════════════════════╗")
    print("║   FAISS vs ChromaDB 向量库对比实验                ║")
    print("╚══════════════════════════════════════════════════════╝\n")

    # ---- 准备数据 ----
    documents, embeddings, texts = load_and_split(NOTES_DIR)
    dimension = embeddings.shape[1]

    # ---- 构建 FAISS 索引 ----
    print("📦 构建 FAISS 索引...")
    t0 = time.perf_counter()
    faiss_idx = FAISSIndex(dimension)
    faiss_idx.build(embeddings, documents)
    faiss_build_time = time.perf_counter() - t0

    # ---- 构建 ChromaDB 索引 ----
    print("📦 构建 ChromaDB 索引...")
    t0 = time.perf_counter()
    chroma_idx = ChromaIndex()
    chroma_idx.build(embeddings, documents)
    chroma_build_time = time.perf_counter() - t0

    # ---- 用相同查询对比 ----
    test_queries = [
        "什么是 RAG",
        "Python 装饰器怎么用",
        "LangChain 的核心概念",
    ]

    print(f"\n{'=' * 70}")
    print(f"检索对比（Top {TOP_K}）")
    print(f"{'=' * 70}")

    for query in test_queries:
        print(f"\n{'─' * 70}")
        print(f"查询: 「{query}」")
        q_emb = embed_query(query)

        # FAISS 检索
        t0 = time.perf_counter()
        faiss_results = faiss_idx.search(q_emb, k=TOP_K)
        faiss_time = (time.perf_counter() - t0) * 1000

        # ChromaDB 检索
        t0 = time.perf_counter()
        chroma_results = chroma_idx.search(q_emb, k=TOP_K)
        chroma_time = (time.perf_counter() - t0) * 1000

        faiss_label = f"FAISS (耗时 {faiss_time:.1f}ms)"
        chroma_label = f"ChromaDB (耗时 {chroma_time:.1f}ms)"
        print(f"  {faiss_label:<45} | {chroma_label}")
        print(f"  {'-' * 43}+{'-' * 23}")

        for rank in range(TOP_K):
            f_text, f_meta, f_score = faiss_results[rank]
            c_text, c_meta, c_dist = chroma_results[rank]

            f_preview = f_text[:35].replace("\n", " ")
            c_preview = c_text[:35].replace("\n", " ")

            f_line = f"  {rank + 1}. [{f_meta.get('source', '?')}] {f_preview}..."
            c_line = f"  {rank + 1}. [{c_meta.get('source', '?')}] {c_preview}..."
            print(f_line + "  |" + c_line)

    # ---- 总结对比 ----
    print(f"\n{'=' * 70}")
    print(f"性能总结")
    print(f"{'=' * 70}")
    print(f"  FAISS  构建耗时: {faiss_build_time * 1000:.1f}ms")
    print(f"  ChromaDB 构建耗时: {chroma_build_time * 1000:.1f}ms")

    print(f"""
{'=' * 70}
关键差异总结
{'=' * 70}

┌──────────────────┬─────────────────────────┬─────────────────────────┐
│ 维度             │ FAISS                   │ ChromaDB                │
├──────────────────┼─────────────────────────┼─────────────────────────┤
│ 本质             │ 向量索引库 (library)    │ 向量数据库 (database)    │
│ 运行方式         │ 进程内，纯 Python/C++    │ 独立服务 (Docker)        │
│ 持久化           │ 手动 save/load 文件     │ 自动持久化              │
│ 元数据管理       │ 自己维护（手动映射）     │ 内置 metadata 过滤       │
│ 分布式/多用户    │ 不支持                  │ 支持 REST API            │
│ 检索速度         │ 极快（纯内存）          │ 较快（网络开销）         │
│ 近似检索(ANN)    │ 支持多种索引(IVF/HNSW)  │ 默认 ANN (HNSW)          │
│ 安装复杂度       │ pip install 即可        │ 需要 Docker              │
│ 适用场景         │ 研究/嵌入式/百万级检索   │ 生产 RAG/团队共享         │
└──────────────────┴─────────────────────────┴─────────────────────────┘

选型建议：
  - 个人项目、离线实验、嵌入式场景 → FAISS（零依赖，极快）
  - 生产 RAG 系统、需要持久化/团队协作 → ChromaDB
  - 百万级以上生产环境 → Milvus / Qdrant / Weaviate
""")


# ============================================================
# 入口
# ============================================================

if __name__ == "__main__":
    init_config()
    run_comparison()
