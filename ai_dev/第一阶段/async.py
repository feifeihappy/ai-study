import requests
import time


def fetch_data_sync(url):
    print(f"开始请求: {url}")
    # 模拟耗时操作（同步阻塞）
    response = requests.get(url)
    print(f"完成请求: {url}, 状态码: {response.status_code}")


# 模拟 3 个任务
# 修改后（正确的 - 使用真实的测试网址）
urls = [
    "https://httpbin.org/delay/1",
    "https://httpbin.org/delay/1",
    "https://httpbin.org/delay/1"
]

start_time = time.time()
for url in urls:
    # 这里会卡住，必须等上一个跑完才能跑下一个
    # 实际开发中这里会是真的 API 地址
    fetch_data_sync(url)
end_time = time.time()

print(f"同步总耗时: {end_time - start_time:.2f} 秒")

import asyncio
import httpx


# 定义一个异步函数（协程）
async def fetch_data_async(client, url):
    print(f"开始请求: {url}")
    # await 意思是：这里要等一会，但我把控制权交出去，别卡死程序
    response = await client.get(url)
    print(f"完成请求: {url}, 状态码: {response.status_code}")


# 主程序入口
async def main():
    urls = [
        "https://httpbin.org/delay/1",
        "https://httpbin.org/delay/1",
        "https://httpbin.org/delay/1"
    ]
    # 创建一个异步客户端
    async with httpx.AsyncClient() as client:
        # 创建任务列表
        tasks = [fetch_data_async(client, url) for url in urls]

        # 关键！gather 意思是：把这些任务打包，并发执行
        for task in tasks:
            # 添加任务
            await task
        # await asyncio.gather(*tasks)


start_time = time.time()
# 运行异步主程序
asyncio.run(main())
end_time = time.time()

print(f"异步总耗时: {end_time - start_time:.2f} 秒")
