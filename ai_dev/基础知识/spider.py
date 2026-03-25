import requests
from bs4 import BeautifulSoup
import json

url = "https://movie.douban.com/top250"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

print(f"🕷️ 正在爬取：{url} ...")

response = requests.get(url, headers=headers)

if response.status_code == 200:
    print("✅ 网页获取成功！")

    soup = BeautifulSoup(response.text, 'html.parser')

    # --- 🔍 调试开始：打印前 500 个字符的 HTML，看看结构 ---
    # 我们尝试找一下包含 "ol" 标签的内容，因为列表通常在 ol 里
    ol_tag = soup.find('ol', class_='grid_view')

    if ol_tag:
        print("✅ 找到了 <ol class='grid_view'> 标签！")
        # 打印这个标签下的前 200 个字符，看看里面有没有电影信息
        print("👀 标签内容预览:", str(ol_tag)[:200])

        # 尝试直接在这个 ol 标签下找 li
        movie_list = ol_tag.find_all('li')
        print(f"🎬 在 ol 标签下找到了 {len(movie_list)} 个 li 标签")

        # 如果找到了，我们就用这个 list 继续后续逻辑
        target_items = movie_list
    else:
        print("❌ 没找到 <ol class='grid_view'> 标签，尝试全局搜索 li...")
        # 备用方案：直接找所有 li，看看能不能蒙对
        target_items = soup.find_all('li')
        print(f"全局找到了 {len(target_items)} 个 li 标签")

        # 打印第一个 li 看看长啥样
        if target_items:
            print("👀 第一个 li 内容预览:", str(target_items[0])[:300])
    # --- 🔍 调试结束 ---

    # 使用我们刚才找到的 target_items 进行提取
    movies_data = []

    # 为了防止报错，我们加个判断
    for item in target_items[:10]:
        # 尝试更稳健的提取方式
        title_span = item.find('span', class_='title')
        rating_span = item.find('span', class_='rating_num')

        # 只有当标题和评分都存在时，才认为是有效电影条目
        if title_span and rating_span:
            title = title_span.text.strip()
            rating = rating_span.text.strip()
            link = item.find('a')['href']

            movie_info = {
                "title": title,
                "rating": rating,
                "link": link
            }
            movies_data.append(movie_info)
            print(f"🎬 提取成功：{title} | {rating}")
        else:
            # 跳过不符合条件的 li (比如广告或其他列表项)
            continue

    filename = "top10_movies.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(movies_data, f, ensure_ascii=False, indent=4)

    print(f"\n💾 最终保存 {len(movies_data)} 部电影数据到 {filename}！")

else:
    print(f"❌ 请求失败：{response.status_code}")