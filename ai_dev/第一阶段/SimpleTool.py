class SimpleTool:
    # __init__ 是构造方法，创建对象时自动调用
    def __init__(self, tool_name, api_key):
        # self.name 代表“我自己的名字”
        self.name = tool_name
        self.key = api_key
        print(f"🔧 工具 {self.name} 已初始化完成！")

# 这是一个方法，定义了工具的行为
    def run(self, query):
        # 使用 self.name 访问对象自己的属性
        print(f"正在使用 [{self.name}] 处理: {query}")
        return f"这是 {query} 的结果"

# 创建对象（实例化）
# 这行代码会自动触发 __init__，把 "天气查询" 和 "12345" 传进去
my_tool = SimpleTool("天气查询", "12345")

# 调用方法
result = my_tool.run("北京天气")
# 输出: 正在使用 [天气查询] 处理: 北京天气



import requests
import time

def fetch_data_sync(url):
    print(f"开始请求: {url}")
    # 模拟耗时操作（同步阻塞）
    response = requests.get(url)
    print(f"完成请求: {url}, 状态码: {response.status_code}")

# 模拟 3 个任务
urls = ["url1", "url2", "url3"]

start_time = time.time()
for url in urls:
    # 这里会卡住，必须等上一个跑完才能跑下一个
    # 实际开发中这里会是真的 API 地址
    fetch_data_sync(url)
end_time = time.time()

print(f"同步总耗时: {end_time - start_time:.2f} 秒")