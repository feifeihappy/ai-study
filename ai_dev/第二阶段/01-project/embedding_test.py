"""
embedding_demo.py
第5周周一任务：理解Embedding原理并调用Embedding API
学习目标：
1. 理解文字如何变成向量
2. 调用通义千问Embedding API
3. 计算文本相似度
4. 可视化向量空间
"""
import os
from dotenv import load_dotenv
import numpy as np
from typing import List

# ==================== 第一部分：基础调用 ====================

def basic_embedding_call():
    """演示如何调用Embedding API获取文本向量"""
    print("=" * 60)
    print("📌 第一部分:基础Embedding调用")
    print("=" * 60)

    # 加载环境变量
    load_dotenv()
    api_key = os.getenv("DASHSCOPE_API_KEY")

    if not api_key:
        raise ValueError("请在 .env 文件中设置 DASHSCOPE_API_KEY")

    # 使用阿里云原生DashScope SDK
    import dashscope
    from dashscope import TextEmbedding
    
    dashscope.api_key = api_key

    # 测试文本
    test_texts = [
        "人工智能正在改变世界",
        "AI技术革命性发展",
        "今天天气真好",
        "机器学习是AI的核心"
    ]

    print(f"\n🔍 测试文本:\n")
    for i, text in enumerate(test_texts, 1):
        print(f"{i}. {text}")

    # 调用API获取向量
    print(f"\n⚙️  正在调用Embedding API...")
    
    vectors = []
    for text in test_texts:
        try:
            response = TextEmbedding.call(
                model=TextEmbedding.Models.text_embedding_v2,
                input=text
            )
            
            if response.status_code == 200:
                vector = response.output['embeddings'][0]['embedding']
                vectors.append(vector)
                print(f"  ✅ 已处理: {text[:15]}... (维度: {len(vector)})")
            else:
                print(f"  ❌ 处理失败: {text[:15]}... 错误码: {response.code}")
                print(f"     错误信息: {response.message}")
                raise Exception(f"API调用失败: {response.message}")
        except Exception as e:
            print(f"  ❌ 异常: {e}")
            raise

    # 展示结果
    print(f"\n✅ 成功获取 {len(vectors)} 个向量")
    print(f"📊 向量维度:{len(vectors[0])} 维")
    print(f"\n第一个向量的前10个数值:")
    print(f"{vectors[0][:10]}")

    return vectors


# ==================== 第二部分：相似度计算 ====================

def calculate_similarity(vectors: List[List[float]], texts: List[str]):
    """计算文本之间的余弦相似度"""
    print("\n" + "=" * 60)
    print("📌 第二部分：计算文本相似度")
    print("=" * 60)

    # 将列表转为numpy数组便于计算
    vectors_array = np.array(vectors)

    def cosine_similarity(vec1, vec2):
        """计算两个向量的余弦相似度"""
        dot_product = np.dot(vec1, vec2)
        norm_vec1 = np.linalg.norm(vec1)
        norm_vec2 = np.linalg.norm(vec2)
        return dot_product / (norm_vec1 * norm_vec2)

    # 计算所有文本对的相似度
    print(f"\n📈 相似度矩阵（值越接近1表示越相似）：\n")

    # 打印表头
    print(f"{'':<20}", end="")
    for i, text in enumerate(texts):
        short_text = text[:8] + "..." if len(text) > 10 else text
        print(f"{short_text:<15}", end="")
    print()

    # 打印相似度矩阵
    for i in range(len(texts)):
        short_text_i = texts[i][:8] + "..." if len(texts[i]) > 10 else texts[i]
        print(f"{short_text_i:<20}", end="")
        for j in range(len(texts)):
            similarity = cosine_similarity(vectors_array[i], vectors_array[j])
            print(f"{similarity:.3f}         ", end="")
        print()

    # 找出最相似的文本对
    print(f"\n🎯 最相似的文本对：")
    max_sim = -1
    best_pair = (0, 0)
    for i in range(len(texts)):
        for j in range(i + 1, len(texts)):
            sim = cosine_similarity(vectors_array[i], vectors_array[j])
            if sim > max_sim:
                max_sim = sim
                best_pair = (i, j)

    print(f"   「{texts[best_pair[0]]}」")
    print(f"   「{texts[best_pair[1]]}」")
    print(f"   相似度：{max_sim:.4f}")


# ==================== 第三部分：语义搜索演示 ====================

def semantic_search_demo():
    """演示基于Embedding的语义搜索"""
    print("\n" + "=" * 60)
    print("📌 第三部分:语义搜索实战")
    print("=" * 60)

    load_dotenv()
    api_key = os.getenv("DASHSCOPE_API_KEY")

    import dashscope
    from dashscope import TextEmbedding
    
    dashscope.api_key = api_key

    # 构建一个小型知识库
    knowledge_base = [
        "Python是一种广泛使用的编程语言,适合初学者",
        "Java是一门面向对象的语言,广泛应用于企业级开发",
        "JavaScript主要用于Web前端开发,让网页具有交互性",
        "C++是一种高性能语言,常用于游戏开发和系统编程",
        "Go语言由Google开发,适合并发编程和微服务",
        "React是一个用于构建用户界面的JavaScript库",
        "Docker是一个容器化平台,简化应用部署",
        "Kubernetes用于自动化容器化应用的部署和管理",
        "MySQL是一个流行的关系型数据库管理系统",
        "MongoDB是一个NoSQL文档数据库,灵活性强"
    ]

    print(f"\n📚 知识库内容(共{len(knowledge_base)}条):")
    for i, item in enumerate(knowledge_base, 1):
        print(f"  {i}. {item}")

    # 获取知识库中所有文本的向量
    print(f"\n⚙️  正在为知识库生成向量索引...")
    
    kb_vectors = []
    for text in knowledge_base:
        response = TextEmbedding.call(
            model=TextEmbedding.Models.text_embedding_v2,
            input=text
        )
        if response.status_code == 200:
            vector = response.output['embeddings'][0]['embedding']
            kb_vectors.append(vector)
            print(f"  ✅ 已索引: {text[:20]}...")
        else:
            raise Exception(f"API调用失败: {response.message}")
    
    kb_vectors_array = np.array(kb_vectors)

    # 用户查询
    queries = [
        "我想学一门简单的编程语言",
        "如何做网站前端开发",
        "容器化部署工具"
    ]

    for query in queries:
        print(f"\n{'='*50}")
        print(f"🔍 查询：「{query}」")
        print(f"{'='*50}")

        # 获取查询向量
        response = TextEmbedding.call(
            model=TextEmbedding.Models.text_embedding_v2,
            input=query
        )
        if response.status_code == 200:
            query_vector = response.output['embeddings'][0]['embedding']
        else:
            raise Exception(f"API调用失败: {response.message}")
        
        query_vector_array = np.array(query_vector)

        # 计算与知识库中每个条目的相似度
        similarities = []
        for i, kb_vector in enumerate(kb_vectors_array):
            sim = np.dot(query_vector_array, kb_vector) / (
                np.linalg.norm(query_vector_array) * np.linalg.norm(kb_vector)
            )
            similarities.append((i, sim))

        # 按相似度排序，取前3个
        similarities.sort(key=lambda x: x[1], reverse=True)
        top_3 = similarities[:3]

        print(f"\n📋 Top 3 相关结果：")
        for rank, (idx, score) in enumerate(top_3, 1):
            print(f"  {rank}. [相似度: {score:.4f}] {knowledge_base[idx]}")


# ==================== 第四部分：向量可视化（简化版）====================

def visualize_embeddings_simple():
    """简单可视化:展示向量在降维后的分布"""
    print("\n" + "=" * 60)
    print("📌 第四部分:向量空间可视化(简化版)")
    print("=" * 60)

    load_dotenv()
    api_key = os.getenv("DASHSCOPE_API_KEY")

    import dashscope
    from dashscope import TextEmbedding
    
    dashscope.api_key = api_key

    # 准备三组不同主题的文本
    tech_texts = ["人工智能", "机器学习", "深度学习", "神经网络"]
    food_texts = ["火锅", "烧烤", "麻辣烫", "串串香"]
    sport_texts = ["篮球", "足球", "乒乓球", "羽毛球"]

    all_texts = tech_texts + food_texts + sport_texts
    labels = ["科技"] * 4 + ["美食"] * 4 + ["运动"] * 4

    print(f"\n📝 测试文本分类:")
    print(f"  科技类:{tech_texts}")
    print(f"  美食类:{food_texts}")
    print(f"  运动类:{sport_texts}")

    # 获取向量 - 使用DashScope原生SDK
    print(f"\n⚙️  正在生成向量...")
    vectors = []
    for text in all_texts:
        response = TextEmbedding.call(
            model=TextEmbedding.Models.text_embedding_v2,
            input=text
        )
        if response.status_code == 200:
            vector = response.output['embeddings'][0]['embedding']
            vectors.append(vector)
            print(f"  ✅ 已处理: {text}")
        else:
            raise Exception(f"API调用失败: {response.message}")
    
    vectors_array = np.array(vectors)

    # 使用PCA降维到2D（如果安装了sklearn）
    try:
        from sklearn.decomposition import PCA
        pca = PCA(n_components=2)
        reduced_vectors = pca.fit_transform(vectors_array)

        print(f"\n📊 降维结果（1536维 -> 2维）：")
        for i, (x, y) in enumerate(reduced_vectors):
            category = labels[i]
            text = all_texts[i]
            print(f"  [{category}] {text}: ({x:.2f}, {y:.2f})")

        print(f"\n💡 观察：同类别的文本在向量空间中应该距离较近！")

    except ImportError:
        print(f"\n⚠️  未安装sklearn，跳过可视化步骤")
        print(f"💡 提示：运行 pip install scikit-learn 可启用此功能")

        # 手动计算几个样本的距离
        print(f"\n📏 手动计算向量距离示例：")
        tech_dist = np.linalg.norm(vectors_array[0] - vectors_array[1])
        food_dist = np.linalg.norm(vectors_array[4] - vectors_array[5])
        cross_dist = np.linalg.norm(vectors_array[0] - vectors_array[4])

        print(f"  「人工智能」vs「机器学习」（同类）: {tech_dist:.2f}")
        print(f"  「火锅」vs「烧烤」（同类）: {food_dist:.2f}")
        print(f"  「人工智能」vs「火锅」（跨类）: {cross_dist:.2f}")
        print(f"\n💡 结论：同类文本的向量距离更小！")


# ==================== 主程序 ====================

if __name__ == "__main__":
    print("🚀 开始Embedding学习之旅...\n")

    try:
        # 第一部分：基础调用
        vectors = basic_embedding_call()
        test_texts = [
            "人工智能正在改变世界",
            "AI技术革命性发展",
            "今天天气真好",
            "机器学习是AI的核心"
        ]

        # 第二部分：相似度计算
        calculate_similarity(vectors, test_texts)

        # 第三部分：语义搜索
        semantic_search_demo()

        # 第四部分：可视化
        visualize_embeddings_simple()

        print("\n" + "=" * 60)
        print("✅ Embedding学习完成！")
        print("=" * 60)
        print("\n📖 核心知识点总结：")
        print("  1. Embedding将文本转换为高维向量")
        print("  2. 语义相似的文本，向量距离更近")
        print("  3. 可以用余弦相似度衡量文本相关性")
        print("  4. 这是RAG系统中检索环节的核心技术")
        print("\n🎯 下一步：学习向量数据库（ChromaDB）存储这些向量")

    except Exception as e:
        print(f"\n❌ 发生错误:{e}")
        print(f"💡 请检查:")
        print(f"  1. .env文件中是否配置了DASHSCOPE_API_KEY")
        print(f"  2. 网络连接是否正常")
        print(f"  3. 是否安装了依赖包:pip install dashscope numpy")
        print(f"  4. 如果使用可视化功能:pip install scikit-learn")