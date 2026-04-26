import chromadb

# 1. 连接到你的 Docker 容器
# 注意：这里用的是 HttpClient，不是默认的本地模式
client = chromadb.HttpClient(host="localhost", port=8000)

# 2. 创建一个集合（类似于 SQL 里的“建表”）
collection = client.create_collection(name="my_demo_collection")

# 3. 存入数据（向量化）
# 这里我们存入两段文本，ChromaDB 会自动把它们变成向量
collection.add(
    documents=["这是第一条测试数据", "ChromaDB 真的很强大"],
    metadatas=[{"source": "test_script"}, {"source": "test_script"}],
    ids=["id1", "id2"]
)
print("✅ 数据写入成功！")

# 4. 搜索数据（语义搜索）
# 我们搜“测试”，它应该能把第一条找出来
results = collection.query(
    query_texts=["我想找测试数据"],
    n_results=1
)

print("🔍 搜索结果：", results['documents'])