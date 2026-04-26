import os
from langchain_community.document_loaders import (
    TextLoader,
    DirectoryLoader,
)

def test_text_loader():
    """测试文本文件加载"""
    print("=== 测试 TextLoader ===")
    loader = TextLoader("../../基础知识/main.py", encoding="utf-8")
    documents = loader.load()
    print(f"加载了 {len(documents)} 个文档")
    print(f"文档内容长度: {len(documents[0].page_content)} 字符")
    print(f"元数据: {documents[0].metadata}")
    print()

def test_markdown_loader_simple():
    """使用 TextLoader 加载 Markdown 文件（无需 unstructured）"""
    print("=== 测试 MarkdownLoader (简化版) ===")
    # Markdown 本质也是文本，可以用 TextLoader 加载
    loader = TextLoader("../../学习路径.md", encoding="utf-8")
    documents = loader.load()
    print(f"加载了 {len(documents)} 个文档")
    print(f"文档内容前200字符: {documents[0].page_content[:200]}...")
    print(f"元数据: {documents[0].metadata}")
    print()

def test_directory_loader():
    """测试批量加载目录下的所有 Markdown 文件"""
    print("=== 测试 DirectoryLoader ===")
    # 使用 TextLoader 替代 UnstructuredMarkdownLoader
    loader = DirectoryLoader(
        "../../../ai_dev",
        glob="*.md",
        loader_cls=TextLoader,
        loader_kwargs={'encoding': 'utf-8'}
    )
    documents = loader.load()
    print(f"从目录加载了 {len(documents)} 个文档")
    for doc in documents:
        print(f"  - {doc.metadata['source']}")
    print()

if __name__ == "__main__":
    test_text_loader()
    test_markdown_loader_simple()
    test_directory_loader()
    print("✅ 所有加载器测试完成！")
