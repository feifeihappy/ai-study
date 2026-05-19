"""
元数据过滤演示 — 按日期和标签筛选文档
学习目标：理解元数据如何帮助"查准"而非仅靠向量相似度
"""

from datetime import datetime
from typing import Literal

# 模拟文档：每条记录包含内容 + 元数据
documents = [
    {"content": "BERT 是 Google 2018 年提出的预训练模型", "metadata": {"date": "2018-10-11", "tags": ["NLP", "预训练"]}},
    {"content": "GPT-3 由 OpenAI 在 2020 年发布，参数量达 1750 亿", "metadata": {"date": "2020-05-28", "tags": ["NLP", "生成模型"]}},
    {"content": "ChatGPT 是 OpenAI 基于 GPT-3.5 的对话产品，2022年11月发布", "metadata": {"date": "2022-11-30", "tags": ["NLP", "对话AI"]}},
    {"content": "LangChain 是 2023 年初兴起的 AI 应用开发框架", "metadata": {"date": "2023-01-01", "tags": ["框架", "LangChain"]}},
    {"content": "Mistral 7B 是 2023 年 9 月发布的开源模型，表现优异", "metadata": {"date": "2023-09-27", "tags": ["NLP", "开源模型"]}},
]


def filter_by_date(docs: list, after: str | None = None, before: str | None = None) -> list:
    """
    按日期范围筛选文档
    after: '2020-01-01' 格式的字符串，不填则不限制下限
    """
    result = []
    for doc in docs:
        doc_date = datetime.strptime(doc["metadata"]["date"], "%Y-%m-%d")
        if after and doc_date < datetime.strptime(after, "%Y-%m-%d"):
            continue
        if before and doc_date > datetime.strptime(before, "%Y-%m-%d"):
            continue
        result.append(doc)
    return result


def filter_by_tags(docs: list, tags: list, match_all: bool = False) -> list:
    """
    按标签筛选文档
    tags: 目标标签列表
    match_all: True=必须包含所有标签，False=包含任一标签即可
    """
    result = []
    for doc in docs:
        doc_tags = set(doc["metadata"]["tags"])
        if match_all:
            if all(t in doc_tags for t in tags):
                result.append(doc)
        else:
            if any(t in doc_tags for t in tags):
                result.append(doc)
    return result


def metadata_filter(
    docs: list,
    after: str | None = None,
    before: str | None = None,
    tags: list | None = None,
    match_all_tags: bool = False,
) -> list:
    """
    组合过滤：先按日期筛选，再按标签筛选
    等价于 SQL 的 WHERE date > X AND tags IN (Y, Z)
    """
    filtered = filter_by_date(docs, after, before)
    if tags:
        filtered = filter_by_tags(filtered, tags, match_all_tags)
    return filtered


# ============ 验证演示 ============

if __name__ == "__main__":
    print("=== 原始文档 ===")
    for d in documents:
        print(f"[{d['metadata']['date']}] {d['metadata']['tags']} | {d['content'][:30]}...")

    print("\n=== 场景1：查 2020 年之后的 NLP 文档 ===")
    result = metadata_filter(documents, after="2020-01-01", tags=["NLP"])
    for d in result:
        print(f"[{d['metadata']['date']}] {d['content'][:40]}...")

    print("\n=== 场景2：只想要同时有'框架'和'LangChain'标签的 ===")
    result = metadata_filter(documents, tags=["框架", "LangChain"], match_all_tags=True)
    for d in result:
        print(f"[{d['metadata']['date']}] {d['metadata']['tags']} | {d['content']}")