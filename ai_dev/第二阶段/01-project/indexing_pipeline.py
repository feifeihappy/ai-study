"""
indexing_pipeline.py — 知识库索引流程实战
==========================================
RAG 系统的数据摄入管道：加载 → 分割 → 向量化 → 存储

整个流程对应 RAG 的离线阶段（Ingestion），在线阶段是检索+生成。

学完这个，你就能把任意文档变成可语义搜索的知识库。
"""
import os
from typing import List

from dotenv import load_dotenv
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
import dashscope
from dashscope import TextEmbedding
import chromadb
from chromadb import HttpClient


# ============================================================
# 0. 配置初始化
# ============================================================

def init_config():
    """加载环境变量，配置 DashScope API Key"""
    load_dotenv()
    api_key = os.getenv("DASHSCOPE_API_KEY")
    if not api_key:
        raise ValueError("请在 .env 文件中设置 DASHSCOPE_API_KEY")
    dashscope.api_key = api_key


# ============================================================
# 第一步：加载文档 (Load)
# ============================================================

def load_document(filepath: str) -> str:
    """
    从文件读取原始文本。

    为什么是纯文本读取而不是 PDF/DOCX 解析器？
    因为这是最小示例。真实项目中会用 LangChain 的 Document Loaders
    （PyPDFLoader、Docx2txtLoader 等），它们统一输出 Document 对象。
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"文件不存在: {filepath}")

    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    print(f"📄 加载文件: {filepath}")
    print(f"   文件大小: {len(content)} 字符")
    return content


# ============================================================
# 第二步：文本分割 (Split)
# ============================================================

def split_text(content: str, chunk_size: int = 500, chunk_overlap: int = 80) -> List[Document]:
    """
    将长文本切分成语义完整的小块，返回 LangChain Document 对象。

    为什么用 RecursiveCharacterTextSplitter？
    - 它尝试在语义边界（段落 → 句子 → 词组）处切分，而不是硬截断
    - separators 按优先级使用：先试 \n\n（段落），再试 \n（行），最后才按字符

    为什么要带 metadata？
    - 检索时不仅要拿到内容，还要知道它来自哪里
    - 在 UI 里可以展示"这段内容出自 XXX 文章"
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", "。", ".", " ", ""],
    )

    # 先生成纯文本块
    text_chunks = splitter.split_text(content)

    # 包装成 Document 对象，带上来源信息
    documents = []
    for i, chunk in enumerate(text_chunks):
        doc = Document(
            page_content=chunk,
            metadata={
                "source": os.path.basename(content) if not hasattr(content, '__len__') else "document",
                "chunk_index": i,
                "chunk_size": len(chunk),
            }
        )
        documents.append(doc)

    print(f"✂️  文本分割完成: {len(documents)} 个 chunk")
    print(f"   参数: chunk_size={chunk_size}, overlap={chunk_overlap}")
    # 显示每个 chunk 的大小分布
    sizes = [doc.metadata["chunk_size"] for doc in documents]
    print(f"   大小范围: {min(sizes)} ~ {max(sizes)} 字符, 平均 {sum(sizes)/len(sizes):.0f} 字符")
    return documents


# ============================================================
# 第三步：向量化 (Embed)
# ============================================================

def embed_chunks(documents: List[Document], batch_size: int = 10) -> List[List[float]]:
    """
    将每个 chunk 文本调用 Embedding API 转为向量。

    为什么要逐条调用而不是批量？
    - DashScope text_embedding_v2 的 input 可以接受列表，但计费按 token 总数
    - 逐条调用可以在失败时定位到具体哪条数据出错
    - 生产环境中应该用批量调用 + 重试机制

    向量维度：text_embedding_v2 返回 1536 维向量
    """
    all_embeddings = []
    total = len(documents)

    for i, doc in enumerate(documents):
        if i % batch_size == 0 and i > 0:
            print(f"   已处理 {i}/{total}...")

        response = TextEmbedding.call(
            model=TextEmbedding.Models.text_embedding_v2,
            input=doc.page_content,
        )

        if response.status_code != 200:
            raise Exception(f"Embedding API 失败 (chunk {i}): {response.message}")

        vector = response.output["embeddings"][0]["embedding"]
        all_embeddings.append(vector)

    print(f"🧮 向量化完成: {len(all_embeddings)} 个向量, 维度 {len(all_embeddings[0])}")
    return all_embeddings


# ============================================================
# 第四步：存储到向量数据库 (Store)
# ============================================================

def store_to_chroma(
    documents: List[Document],
    embeddings: List[List[float]],
    collection_name: str = "knowledge_base",
    host: str = "localhost",
    port: int = 8000,
):
    """
    将文档块和对应的向量存入 ChromaDB。

    为什么用 HttpClient？
    - HttpClient 连接 Docker 容器中的 ChromaDB 服务
    - 数据存在容器内，适合团队共享和生产环境
    - PersistentClient 适合单机本地开发，无需 Docker

    ChromaDB 数据模型：
    - Collection ≈ SQL 中的一张表
    - 每个条目 = id + embedding + document + metadata
    """
    # 连接到 Docker 容器中的 ChromaDB 服务
    client = HttpClient(host=host, port=port)

    # 获取或创建 Collection
    # 如果已存在同名 Collection，先删除再重建（保证幂等性）
    try:
        client.delete_collection(name=collection_name)
    except Exception:
        pass

    collection = client.create_collection(
        name=collection_name,
        metadata={"description": "知识库索引演示"},
    )

    # 准备数据
    ids = [f"chunk_{i}" for i in range(len(documents))]
    texts = [doc.page_content for doc in documents]
    metadatas = [doc.metadata for doc in documents]

    # 分批写入（避免单次写入数据量过大）
    batch_size = 50
    for i in range(0, len(ids), batch_size):
        collection.add(
            ids=ids[i:i + batch_size],
            documents=texts[i:i + batch_size],
            embeddings=embeddings[i:i + batch_size],
            metadatas=metadatas[i:i + batch_size],
        )

    print(f"💾 存储完成: {collection.count()} 条数据")
    print(f"   Collection: {collection_name}")
    print(f"   服务地址: http://{host}:{port}")
    return collection


# ============================================================
# 验证：语义搜索测试
# ============================================================

def verify_search(collection, query: str = "如何学习 RAG", n_results: int = 3):
    """
    用语义搜索验证索引是否正常工作。

    这是 RAG 检索环节的核心：用户问题 → 向量化 → 在知识库中找最相似的 chunk

    为什么用 query_embeddings 而不是 query_texts？
    - query_texts 会调用 ChromaDB 内置的默认 Embedding 模型（384 维）
    - 我们存数据时用的是 DashScope（1536 维），维度必须一致
    - 所以需要自己把查询文本向量化，再传给 ChromaDB
    """
    print(f"\n🔍 验证搜索: 「{query}」")

    # 用 DashScope 把查询文本变成向量（和存数据时同一个模型）
    response = TextEmbedding.call(
        model=TextEmbedding.Models.text_embedding_v2,
        input=query,
    )
    if response.status_code != 200:
        raise Exception(f"查询向量化失败: {response.message}")
    query_embedding = response.output["embeddings"][0]["embedding"]

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results,
    )

    print(f"   找到 {len(results['ids'][0])} 条相关结果:\n")
    for rank, (chunk_id, text, metadata, distance) in enumerate(
        zip(results["ids"][0], results["documents"][0], results["metadatas"][0], results["distances"][0]),
        1
    ):
        preview = text[:100].replace("\n", " ") + "..." if len(text) > 100 else text.replace("\n", " ")
        print(f"   {rank}. [{chunk_id}] 距离={distance:.4f}")
        print(f"      来源: {metadata.get('source', 'unknown')}")
        print(f"      {preview}")
        print()


# ============================================================
# 主流程：串联四步
# ============================================================

def run_pipeline(filepath: str):
    """执行完整的知识库索引流程"""
    print("╔══════════════════════════════════════════════════╗")
    print("║   📦 知识库索引流程：加载 → 分割 → 向量化 → 存储  ║")
    print("╚══════════════════════════════════════════════════╝")
    print()

    # Step 1: 加载
    content = load_document(filepath)

    # Step 2: 分割
    documents = split_text(content, chunk_size=500, chunk_overlap=0)

    # Step 3: 向量化
    embeddings = embed_chunks(documents)

    # Step 4: 存储
    collection = store_to_chroma(
        documents, embeddings,
        collection_name="learning_path",
        host="localhost",
        port=8000,
    )

    # 验证
    verify_search(collection, "如何学习 RAG 系统")
    verify_search(collection, "Python 基础学习")
    verify_search(collection, "Agent 开发")

    print("=" * 60)
    print("✅ 知识库索引流程完成！")
    print()
    print("💡 流水线总结：")
    print("   1. 加载 → LangChain 有上百种 DocumentLoader，覆盖 PDF/网页/数据库")
    print("   2. 分割 → RecursiveCharacterTextSplitter 首选，chunk_size 按场景调")
    print("   3. 向量化 → 用 Embedding 模型（DashScope/OpenAI）把文本变成向量")
    print("   4. 存储 → ChromaDB/FAISS/Milvus，选型取决于数据量和部署环境")
    print()
    print("🎯 下一步：构建 RAG 问答系统（检索 + 生成）")


# ============================================================
# 入口
# ============================================================

if __name__ == "__main__":
    init_config()

    # 使用项目中的真实文件作为知识库
    target_file = os.path.join(
        os.path.dirname(__file__),
        "../../学习路径.md"
    )

    try:
        run_pipeline(target_file)
    except FileNotFoundError as e:
        print(f"❌ {e}")
        print("💡 请确保文件路径正确，或修改 target_file 指向一个存在的 .md 文件")
    except Exception as e:
        print(f"❌ 运行失败: {e}")
