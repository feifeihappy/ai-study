# 第二阶段/01-project/text_splitter_test.py
"""
文本分割器测试 - 学习如何将长文档切分成适合 LLM 处理的小片段
"""
from langchain_text_splitters import (
    CharacterTextSplitter,
    RecursiveCharacterTextSplitter,
)


def test_character_splitter():
    """按字符分割（基础方式）"""
    print("=" * 60)
    print("=== CharacterTextSplitter ===")
    print("=" * 60)

    # 准备测试文本
    text = "这是第一段内容。\n" * 20 + "这是第二段内容。\n" * 20

    splitter = CharacterTextSplitter(
        separator="\n",  # 分隔符
        chunk_size=100,  # 每个片段最大100字符
        chunk_overlap=20  # 片段间重叠20字符，保持上下文连贯
    )

    chunks = splitter.split_text(text)

    print(f"原文长度: {len(text)} 字符")
    print(f"分割成 {len(chunks)} 个片段\n")

    for i, chunk in enumerate(chunks[:5]):  # 只显示前5个
        print(f"--- 片段 {i + 1} ({len(chunk)} 字符) ---")
        print(chunk)
        print()


def test_recursive_splitter():
    """递归字符分割（推荐用于实际项目）"""
    print("=" * 60)
    print("=== RecursiveCharacterTextSplitter（推荐）===")
    print("=" * 60)

    # 读取真实文档
    with open("../../学习路径.md", "r", encoding="utf-8") as f:
        text = f.read()

    # 递归分割器会尝试多种分隔符，优先在自然边界处分割
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,  # 每个片段500字符
        chunk_overlap=50,  # 重叠50字符
        separators=["\n\n", "\n", "。", "！", "？", "；", "，", " ", ""]  # 优先级从高到低
    )

    chunks = splitter.split_text(text)

    print(f"原文长度: {len(text)} 字符")
    print(f"分割成 {len(chunks)} 个片段")
    print(f"平均片段长度: {sum(len(c) for c in chunks) / len(chunks):.0f} 字符\n")

    # 显示片段统计
    lengths = [len(c) for c in chunks]
    print(f"片段长度分布:")
    print(f"  最短: {min(lengths)} 字符")
    print(f"  最长: {max(lengths)} 字符")
    print(f"  平均: {sum(lengths) / len(lengths):.0f} 字符\n")

    # 显示前3个片段示例
    print("片段示例：")
    for i, chunk in enumerate(chunks[:3]):
        print(f"\n--- 片段 {i + 1} ({len(chunk)} 字符) ---")
        print(chunk[:150] + "..." if len(chunk) > 150 else chunk)


def test_split_documents():
    """分割 Document 对象（保留元数据）"""
    print("\n" + "=" * 60)
    print("=== split_documents（保留元数据）===")
    print("=" * 60)

    from langchain_community.document_loaders import TextLoader
    from langchain_core.documents import Document

    # 加载文档
    loader = TextLoader("../../学习路径.md", encoding="utf-8")
    documents = loader.load()

    print(f"加载了 {len(documents)} 个文档\n")

    # 创建分割器
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )

    # 分割文档（返回的仍然是 Document 对象，保留 metadata）
    chunks = splitter.split_documents(documents)

    print(f"分割成 {len(chunks)} 个片段\n")

    # 显示前3个片段的元数据
    for i, chunk in enumerate(chunks[:3]):
        print(f"--- 片段 {i + 1} ---")
        print(f"内容长度: {len(chunk.page_content)} 字符")
        print(f"元数据: {chunk.metadata}")
        print(f"内容预览: {chunk.page_content[:100]}...\n")


def compare_strategies():
    """对比不同分割策略的效果"""
    print("=" * 60)
    print("=== 对比不同 chunk_size 的效果 ===")
    print("=" * 60)

    with open("../../学习路径.md", "r", encoding="utf-8") as f:
        text = f.read()

    chunk_sizes = [200, 500, 1000, 2000]

    print(f"原文长度: {len(text)} 字符\n")

    for size in chunk_sizes:
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=size,
            chunk_overlap=size // 10  # 重叠为 chunk_size 的 10%
        )

        chunks = splitter.split_text(text)
        avg_length = sum(len(c) for c in chunks) / len(chunks)

        print(f"chunk_size={size:4d}: {len(chunks):3d} 个片段, 平均长度 {avg_length:.0f} 字符")


if __name__ == "__main__":
    test_character_splitter()
    test_recursive_splitter()
    test_split_documents()
    compare_strategies()

    print("\n" + "=" * 60)
    print("✅ 所有文本分割器测试完成！")
    print("=" * 60)
    print("\n💡 关键要点：")
    print("1. RecursiveCharacterTextSplitter 是最佳选择")
    print("2. chunk_size 建议 300-800（根据模型上下文窗口调整）")
    print("3. chunk_overlap 建议为 chunk_size 的 10-20%")
    print("4. 使用 split_documents 可以保留元数据")
