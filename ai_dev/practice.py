# 熟悉列表的增删改查

# 场景：正在超市购物，手里有一个初始清单

# 1、创建一个 shopping_list 列表，包含【“牛奶”、“鸡蛋”、“面包”】
shopping_list = ["牛奶", "鸡蛋", "面包"]

# 2 你发现忘了买“苹果”，请把它添加到列表末尾。
shopping_list.append("苹果")
print(shopping_list)
# 你决定不买“面包”了，请把它从列表中删除。
shopping_list.remove("面包")
print(shopping_list)

# 把“鸡蛋”换成“土鸡蛋”（修改第2个元素）。
shopping_list[1] = "土鸡蛋"
print(shopping_list)
print(f"一共买了{len(shopping_list)}样东西")

#
# 练习 2：投票统计员 (字典基础)
# 目标：熟悉字典的键值对操作和计数逻辑。
# 场景：班级里正在评选“最受欢迎的水果”，大家投出了很多票。

# 任务：
# 创建一个空字典 votes。
votes = {}
# 模拟收到以下投票（手动写代码更新字典）：
candidates = ["苹果", "香蕉", "苹果", "橙子", "苹果"]
for fruits in candidates:
    # 如果包含就+1
    if fruits in votes:
        votes[fruits] += 1
    else:
        votes[fruits] = 1

print("投票结果",votes)

# 投给 "苹果" 一票
votes["苹果"] = votes.get("苹果", 1)
# votes.get("苹果", 1)
print(votes)
# 投给 "香蕉" 一票
votes["香蕉"] = votes.get("香蕉", 1)
print(votes)
# 又投给 "苹果" 一票
votes["苹果"] = votes.get("苹果", 1) + 1
print(votes)
# 投给 "橙子" 一票
votes["橙子"] = votes.get("橙子", 1)
# 再投给 "苹果" 一票
votes["苹果"] = votes.get("苹果", 1) + 1
print(votes)
# 挑战：不要直接写 {"苹果": 3, ...}，试着模仿程序逻辑：

winner = max(votes, key=votes.get)
print(f"最受欢迎的水果是{winner}")

# 如果字典里已经有这个水果，票数 +1。
# 如果字典里没有这个水果，初始化为 1。
# (提示：使用 if key in dict 或 dict.get())
# 打印出最终的统计结果。
