# 📦 创建变量
name = "Iron Man"       # 字符串 (str)
age = 45                # 整数 (int)
height = 1.85           # 浮点数 (float)
is_hero = True          # 布尔值 (bool)

# 🔄 修改变量
age = 46                # 过了生日，年龄变了

# 🖨️ 使用变量
print(f"名字: {name}, 年龄: {age}")
# 输出: 名字: Iron Man, 年龄: 46

# 🧮 变量运算
next_age = age + 1
print(f"明年年龄: {next_age}")


# 🛒 创建列表 (用方括号 [])
fruits = ["苹果", "香蕉", "橙子"]
numbers = [1, 2, 3, 4, 5]
mixed = ["Hello", 100, True, [1, 2]] # 甚至可以嵌套列表

# 🔍 访问元素 (索引从 0 开始！)
print(fruits[0])  # 输出: 苹果 (第1个)
print(fruits[1])  # 输出: 香蕉 (第2个)
print(fruits[-1]) # 输出: 橙子 (最后一个，负数表示倒数)

# ✏️ 修改元素
fruits[1] = "葡萄"  # 把香蕉换成葡萄
# 现在 fruits 是 ["苹果", "葡萄", "橙子"]

# ➕ 添加元素
fruits.append("西瓜")      # 加到末尾
fruits.insert(0, "草莓")   # 插到第1个位置

# ❌ 删除元素
fruits.remove("苹果")      # 移除指定内容
last_one = fruits.pop()    # 移除并返回最后一个

# 🔢 常用操作
print(len(fruits))         # 列表长度 (有多少个元素)
print("西瓜" in fruits)    # 判断是否存在 (返回 True/False)

# 🔄 遍历列表 (循环)
for fruit in fruits:
    print(f"我喜欢吃 {fruit}")







# 🗄️ 创建字典 (用花括号 {}，格式是 "键": 值)
user = {
    "name": "Tony Stark",
    "age": 45,
    "city": "New York",
    "skills": ["Engineering", "Fighting"] # 值也可以是列表！
}

# 🔑 访问值 (通过键)
print(user["name"])   # 输出: Tony Stark
print(user["city"])   # 输出: New York

# ⚠️ 安全访问 (如果键不存在，不会报错，而是返回 None 或默认值)
print(user.get("email"))           # 输出: None
print(user.get("email", "无邮箱")) # 输出: 无邮箱 (提供了默认值)

# ✏️ 修改或添加
user["age"] = 46                   # 修改已有的
user["email"] = "tony@stark.com"   # 添加新的键值对

# ❌ 删除
del user["city"]                   # 删除 "city" 这一项

# 🔑 获取所有键或值
print(user.keys())   #  dict_keys(['name', 'age', 'skills', 'email'])
print(user.values()) #  dict_values(['Tony Stark', 46, ...])

# 🔄 遍历字典
for key, value in user.items():
    print(f"{key}: {value}")






