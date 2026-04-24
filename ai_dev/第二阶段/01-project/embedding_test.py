"""
embedding_test.py
Embedding 原理学习与 API 调用演示
学习目标：
1. 理解文字如何变成向量
2. 调用通义千问 Embedding API
3. 计算文本相似度
4. 可视化向量空间
"""
import os
import numpy as np
from typing import List
from dotenv import load_dotenv
import dashscope
from dashscope import TextEmbedding


# ==================== 配置层 ====================

def _init_api():
    """初始化环境变量和 DashScope 配置（全局唯一入口）"""
    load_dotenv()
    api_key = os.getenv("DASHSCOPE_API_KEY")
    if not api_key:
        raise ValueError("请在 .env 文件中设置 DASHSCOPE_API_KEY")
    dashscope.api_key = api_key


# ==================== 服务层 ====================

def get_embedding(text: str) -> List[float]:
    """获取单个文本的 Embedding 向量"""
    response = TextEmbedding.call(
        model=TextEmbedding.Models.text_embedding_v2,
        input=text
    )
    if response.status_code != 200:
        raise Exception(f"API 调用失败: {response.message}")
    return response.output["embeddings"][0]["embedding"]


def get_embeddings(texts: List[str], verbose: bool = True) -> List[List[float]]:
    """批量获取文本的 Embedding 向量"""
    vectors = []
    for text in texts:
        vector = get_embedding(text)
        vectors.append(vector)
        if verbose:
            print(f"  ✅ 已处理: {text[:20]}... (维度: {len(vector)})")
    return vectors


def cosine_similarity(vec1: np.ndarray, vec2: np.ndarray) -> float:
    """计算两个向量的余弦相似度"""
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))


def find_top_k(query_vector: np.ndarray, corpus_vectors: np.ndarray, k: int = 3) -> List[tuple]:
    """在语料库中查找与查询向量最相似的前 K 个结果，返回 [(index, score), ...]"""
    similarities = [
        (i, cosine_similarity(query_vector, corpus_vectors[i]))
        for i in range(len(corpus_vectors))
    ]
    similarities.sort(key=lambda x: x[1], reverse=True)
    return similarities[:k]


# ==================== 演示：基础 Embedding 调用 ====================

def demo_basic():
    """演示基础的 Embedding API 调用"""
    print("=" * 60)
    print("📌 第一部分：基础 Embedding 调用")
    print("=" * 60)

    test_texts = [
        "人工智能正在改变世界",
        "AI技术革命性发展",
        "今天天气真好",
        "机器学习是AI的核心",
    ]

    print("\n🔍 测试文本：")
    for i, text in enumerate(test_texts, 1):
        print(f"  {i}. {text}")

    print("\n⚙️  正在调用 Embedding API...")
    vectors = get_embeddings(test_texts)

    print(f"\n✅ 成功获取 {len(vectors)} 个向量，维度: {len(vectors[0])} 维")
    print(f"第一个向量的前 10 个数值: {vectors[0][:10]}")

    return vectors, test_texts


# ==================== 演示：相似度计算 ====================

def demo_similarity(vectors: List[List[float]], texts: List[str]):
    """演示文本相似度矩阵计算"""
    print("\n" + "=" * 60)
    print("📌 第二部分：计算文本相似度")
    print("=" * 60)

    vectors_array = np.array(vectors)
    n = len(texts)

    # 打印相似度矩阵
    print("\n📈 相似度矩阵（越接近 1 表示越相似）：\n")

    header_width = 20
    col_width = 15
    print(f"{'':<{header_width}}", end="")
    for text in texts:
        short = text[:8] + "..." if len(text) > 10 else text
        print(f"{short:<{col_width}}", end="")
    print()

    for i in range(n):
        short_i = texts[i][:8] + "..." if len(texts[i]) > 10 else texts[i]
        print(f"{short_i:<{header_width}}", end="")
        for j in range(n):
            sim = cosine_similarity(vectors_array[i], vectors_array[j])
            print(f"{sim:.3f}         ", end="")
        print()

    # 找出最相似的一对
    best_pair = (0, 0)
    max_sim = -1
    for i in range(n):
        for j in range(i + 1, n):
            sim = cosine_similarity(vectors_array[i], vectors_array[j])
            if sim > max_sim:
                max_sim = sim
                best_pair = (i, j)

    print(f"\n🎯 最相似的文本对（相似度: {max_sim:.4f}）：")
    print(f"   「{texts[best_pair[0]]}」")
    print(f"   「{texts[best_pair[1]]}」")


# ==================== 演示：语义搜索 ====================

KNOWLEDGE_BASE = [
    "Python是一种广泛使用的编程语言，适合初学者",
    "Java是一门面向对象的语言，广泛应用于企业级开发",
    "JavaScript主要用于Web前端开发，让网页具有交互性",
    "C++是一种高性能语言，常用于游戏开发和系统编程",
    "Go语言由Google开发，适合并发编程和微服务",
    "React是一个用于构建用户界面的JavaScript库",
    "Docker是一个容器化平台，简化应用部署",
    "Kubernetes用于自动化容器化应用的部署和管理",
    "MySQL是一个流行的关系型数据库管理系统",
    "MongoDB是一个NoSQL文档数据库，灵活性强",
]

SEARCH_QUERIES = [
    "我想学一门简单的编程语言",
    "如何做网站前端开发",
    "容器化部署工具",
]


def demo_semantic_search():
    """演示基于 Embedding 的语义搜索"""
    print("\n" + "=" * 60)
    print("📌 第三部分：语义搜索实战")
    print("=" * 60)

    print(f"\n📚 知识库（共 {len(KNOWLEDGE_BASE)} 条）：")
    for i, item in enumerate(KNOWLEDGE_BASE, 1):
        print(f"  {i}. {item}")

    print("\n⚙️  正在为知识库生成向量索引...")
    kb_vectors = get_embeddings(KNOWLEDGE_BASE)
    kb_vectors_array = np.array(kb_vectors)

    for query in SEARCH_QUERIES:
        print(f"\n{'=' * 50}")
        print(f"🔍 查询：「{query}」")
        print(f"{'=' * 50}")

        query_vector = np.array(get_embedding(query))
        top_3 = find_top_k(query_vector, kb_vectors_array, k=3)

        print("\n📋 Top 3 相关结果：")
        for rank, (idx, score) in enumerate(top_3, 1):
            print(f"  {rank}. [相似度: {score:.4f}] {KNOWLEDGE_BASE[idx]}")


# ==================== 演示：向量空间可视化 ====================

TECH_TEXTS = ["人工智能", "机器学习", "深度学习", "神经网络"]
FOOD_TEXTS = ["火锅", "烧烤", "麻辣烫", "串串香"]
SPORT_TEXTS = ["篮球", "足球", "乒乓球", "羽毛球"]


def demo_visualization():
    """演示向量空间降维可视化"""
    print("\n" + "=" * 60)
    print("📌 第四部分：向量空间可视化（简化版）")
    print("=" * 60)

    all_texts = TECH_TEXTS + FOOD_TEXTS + SPORT_TEXTS
    labels = (["科技"] * 4) + (["美食"] * 4) + (["运动"] * 4)

    print(f"\n📝 测试文本分类：")
    print(f"  科技类: {TECH_TEXTS}")
    print(f"  美食类: {FOOD_TEXTS}")
    print(f"  运动类: {SPORT_TEXTS}")

    print("\n⚙️  正在生成向量...")
    vectors = get_embeddings(all_texts)
    vectors_array = np.array(vectors)

    # 尝试 PCA 降维
    try:
        from sklearn.decomposition import PCA
        pca = PCA(n_components=2)
        reduced = pca.fit_transform(vectors_array)

        print(f"\n📊 降维结果（{len(vectors[0])} 维 → 2 维）：")
        for i, (x, y) in enumerate(reduced):
            print(f"  [{labels[i]}] {all_texts[i]}: ({x:.2f}, {y:.2f})")

        print("\n💡 观察：同类别的文本在向量空间中应该距离较近！")

    except ImportError:
        print("\n⚠️  未安装 scikit-learn，跳过 PCA 可视化")
        print("💡 提示：pip install scikit-learn 可启用此功能")

        # 手动计算距离作为替代
        print("\n📏 手动计算向量距离示例：")
        print(f"  「人工智能」vs「机器学习」（同类）: {np.linalg.norm(vectors_array[0] - vectors_array[1]):.2f}")
        print(f"  「火锅」vs「烧烤」（同类）: {np.linalg.norm(vectors_array[4] - vectors_array[5]):.2f}")
        print(f"  「人工智能」vs「火锅」（跨类）: {np.linalg.norm(vectors_array[0] - vectors_array[4]):.2f}")
        print("\n💡 结论：同类文本的向量距离更小！")


# ==================== 主程序 ====================

if __name__ == "__main__":
    print("🚀 开始 Embedding 学习之旅...\n")

    try:
        _init_api()

        vectors, test_texts = demo_basic()
        demo_similarity(vectors, test_texts)
        demo_semantic_search()
        demo_visualization()

        print("\n" + "=" * 60)
        print("✅ Embedding 学习完成！")
        print("=" * 60)
        print("\n📖 核心知识点总结：")
        print("  1. Embedding 将文本转换为高维向量")
        print("  2. 语义相似的文本，向量距离更近")
        print("  3. 可以用余弦相似度衡量文本相关性")
        print("  4. 这是 RAG 系统中检索环节的核心技术")
        print("\n🎯 下一步：学习向量数据库（ChromaDB）存储这些向量")

    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        print("💡 请检查：")
        print("  1. .env 文件中是否配置了 DASHSCOPE_API_KEY")
        print("  2. 网络连接是否正常")
        print("  3. 是否安装了依赖: pip install dashscope numpy")
        print("  4. 可视化功能需要: pip install scikit-learn")
