"""
notes_qa_bot.py — 个人笔记问答机器人
=====================================
RAG 完整闭环：索引笔记 → 语义检索 → 大模型生成答案

使用方式：
    python notes_qa_bot.py index          # 索引笔记目录
    python notes_qa_bot.py ask            # 进入问答模式
    python notes_qa_bot.py ask "什么是RAG" # 单次提问

架构：
    用户提问 → 向量化 → ChromaDB 检索 → 组装上下文 → LLM 生成 → 返回答案
"""
import os
import sys
from typing import List

from dotenv import load_dotenv
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
import dashscope
from dashscope import TextEmbedding
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from chromadb import HttpClient


# ============================================================
# 0. 配置
# ============================================================

NOTES_DIR = "./notes"                # 笔记目录
COLLECTION_NAME = "my_notes"         # ChromaDB Collection 名
CHROMA_HOST = "localhost"
CHROMA_PORT = 8000
CHUNK_SIZE = 500
CHUNK_OVERLAP = 80
TOP_K = 5                            # 检索返回的 chunk 数

# LLM 配置（DashScope 兼容 OpenAI 接口）
LLM_BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
LLM_MODEL = "qwen-plus"


def init_config():
    """加载 .env 并初始化 DashScope"""
    load_dotenv()
    api_key = os.getenv("DASHSCOPE_API_KEY")
    if not api_key:
        raise ValueError("请在 .env 文件中设置 DASHSCOPE_API_KEY")
    dashscope.api_key = api_key
    return api_key


# ============================================================
# 1. 索引阶段：把笔记存入向量数据库
# ============================================================

def load_notes(notes_dir: str) -> List[Document]:
    """
    遍历笔记目录，读取所有 .md 文件，分割成 chunk。

    每个 chunk 带 metadata（文件名），检索时能追溯到原始笔记。
    """
    if not os.path.isdir(notes_dir):
        raise FileNotFoundError(f"笔记目录不存在: {notes_dir}")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", "。", ".", " ", ""],
    )

    all_docs = []
    md_files = sorted([
        f for f in os.listdir(notes_dir) if f.endswith(".md")
    ])

    if not md_files:
        raise ValueError(f"目录 {notes_dir} 中没有 .md 文件")

    for filename in md_files:
        filepath = os.path.join(notes_dir, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        chunks = splitter.split_text(content)
        for i, chunk in enumerate(chunks):
            all_docs.append(Document(
                page_content=chunk,
                metadata={
                    "source": filename,
                    "chunk_index": i,
                    "chunk_size": len(chunk),
                }
            ))
        print(f"  📄 {filename}: {len(content)} 字符 → {len(chunks)} 个 chunk")

    print(f"\n  📊 总计: {len(md_files)} 个文件, {len(all_docs)} 个 chunk")
    return all_docs


def embed_documents(documents: List[Document]) -> List[List[float]]:
    """批量将 Document 转换为向量"""
    embeddings = []
    for i, doc in enumerate(documents):
        response = TextEmbedding.call(
            model=TextEmbedding.Models.text_embedding_v2,
            input=doc.page_content,
        )
        if response.status_code != 200:
            raise Exception(f"向量化失败 (chunk {i}): {response.message}")
        embeddings.append(response.output["embeddings"][0]["embedding"])
    return embeddings


def store_documents(documents: List[Document], embeddings: List[List[float]]):
    """存入 ChromaDB（Docker HttpClient）"""
    client = HttpClient(host=CHROMA_HOST, port=CHROMA_PORT)

    # 幂等：先删再建
    try:
        client.delete_collection(name=COLLECTION_NAME)
    except Exception:
        pass

    collection = client.create_collection(
        name=COLLECTION_NAME,
        metadata={"description": "个人笔记知识库"},
    )

    ids = [f"note_{i}" for i in range(len(documents))]
    texts = [doc.page_content for doc in documents]
    metadatas = [doc.metadata for doc in documents]

    # 分批写入
    batch_size = 50
    for i in range(0, len(ids), batch_size):
        collection.add(
            ids=ids[i:i + batch_size],
            documents=texts[i:i + batch_size],
            embeddings=embeddings[i:i + batch_size],
            metadatas=metadatas[i:i + batch_size],
        )

    print(f"  ✅ 已存入 ChromaDB → Collection: {COLLECTION_NAME}, {collection.count()} 条\n")
    return collection


def index_notes(notes_dir: str = NOTES_DIR):
    """完整索引流程：加载 → 分割 → 向量化 → 存储"""
    print("╔══════════════════════════════════════╗")
    print("║   📦 索引笔记到向量数据库           ║")
    print("╚══════════════════════════════════════╝\n")
    print(f"📂 笔记目录: {os.path.abspath(notes_dir)}\n")

    documents = load_notes(notes_dir)
    print(f"\n🧮 正在向量化 ({len(documents)} 个 chunk)...")
    embeddings = embed_documents(documents)
    print(f"   维度: {len(embeddings[0])}\n")

    store_documents(documents, embeddings)


# ============================================================
# 2. 问答阶段：检索 + 生成
# ============================================================

def retrieve(query: str, k: int = TOP_K):
    """
    语义检索：把用户问题向量化，在知识库中找最相关的 chunk。

    返回 [(content, metadata), ...]
    """
    # 向量化查询
    response = TextEmbedding.call(
        model=TextEmbedding.Models.text_embedding_v2,
        input=query,
    )
    if response.status_code != 200:
        raise Exception(f"查询向量化失败: {response.message}")
    query_embedding = response.output["embeddings"][0]["embedding"]

    # 在 ChromaDB 中检索
    client = HttpClient(host=CHROMA_HOST, port=CHROMA_PORT)
    collection = client.get_collection(name=COLLECTION_NAME)

    results = collection.query(query_embeddings=[query_embedding], n_results=k)

    retrieved = []
    for text, metadata, distance in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
    ):
        retrieved.append((text, metadata, distance))

    return retrieved


def generate_answer(query: str, retrieved_chunks: List[tuple], api_key: str) -> str:
    """
    组装 Prompt，把检索到的内容作为上下文，交给 LLM 生成答案。

    Prompt 设计要点：
    - 明确角色和任务
    - 把检索到的内容放到上下文中
    - 要求只基于上下文回答，不知道就说不知道（防幻觉）
    """
    # 拼装上下文
    context_parts = []
    for i, (text, metadata, _) in enumerate(retrieved_chunks, 1):
        source = metadata.get("source", "unknown")
        context_parts.append(f"[来源{source}]\n{text}")
    context = "\n\n---\n\n".join(context_parts)

    # System Prompt：约束行为
    system_prompt = """你是一个个人笔记助手。请根据用户提供的笔记内容回答问题。

规则：
- 只根据下面提供的笔记内容来回答，不要使用你自己的知识
- 如果笔记中没有相关信息，直接说"笔记中暂无相关内容"
- 回答时引用具体的笔记来源（文件名）
- 用简洁的中文回答"""

    # 构建对话
    llm = ChatOpenAI(
        model=LLM_MODEL,
        base_url=LLM_BASE_URL,
        api_key=api_key,
        temperature=0.3,
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("user", "笔记内容：\n\n{context}\n\n问题：{question}"),
    ])

    chain = prompt | llm
    response = chain.invoke({"context": context, "question": query})

    return response.content


def ask_once(query: str):
    """单次问答"""
    api_key = os.getenv("DASHSCOPE_API_KEY")
    if not api_key:
        init_config()
        api_key = os.getenv("DASHSCOPE_API_KEY")

    print(f"\n🔍 检索相关笔记...")
    chunks = retrieve(query)

    if not chunks:
        print("  ❌ 未找到相关笔记")
        return

    print(f"  ✅ 找到 {len(chunks)} 条相关内容:")
    for i, (text, metadata, distance) in enumerate(chunks, 1):
        source = metadata.get("source", "unknown")
        preview = text[:60].replace("\n", " ")
        print(f"     {i}. [{source}] 距离={distance:.4f} | {preview}...")

    print(f"\n🤖 正在生成回答...")
    answer = generate_answer(query, chunks, api_key)

    print(f"\n{'=' * 60}")
    print(f"📝 回答:\n{answer}")
    print(f"{'=' * 60}\n")


def ask_loop():
    """交互式问答循环"""
    api_key = os.getenv("DASHSCOPE_API_KEY")
    if not api_key:
        init_config()
        api_key = os.getenv("DASHSCOPE_API_KEY")

    print("╔══════════════════════════════════════╗")
    print("║   🤖 个人笔记问答机器人            ║")
    print("║   输入 quit 退出, index 重建索引    ║")
    print("╚══════════════════════════════════════╝")

    while True:
        try:
            query = input("\n💬 你的问题: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n👋 再见！")
            break

        if not query:
            continue
        if query.lower() == "quit":
            print("👋 再见！")
            break
        if query.lower() == "index":
            index_notes()
            continue

        ask_once(query)


# ============================================================
# 入口
# ============================================================

if __name__ == "__main__":
    init_config()

    if len(sys.argv) < 2:
        print("用法:")
        print("  python notes_qa_bot.py index          # 索引笔记")
        print("  python notes_qa_bot.py ask            # 交互式问答")
        print('  python notes_qa_bot.py ask "什么是RAG" # 单次提问')
        sys.exit(0)

    command = sys.argv[1]

    if command == "index":
        index_notes()

    elif command == "ask":
        if len(sys.argv) >= 3:
            # 单次提问
            ask_once(sys.argv[2])
        else:
            ask_loop()

    else:
        print(f"未知命令: {command}")
        sys.exit(1)
