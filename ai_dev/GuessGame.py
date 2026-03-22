#
# 让我们把 if、while、random（随机数）结合起来，做一个经典的猜数字游戏。
# 游戏规则：
# 电脑随机想一个 1 到 100 之间的数字。
# 你不断猜，电脑会提示“大了”还是“小了”。
# 直到猜中为止，并告诉你猜了多少次。
# 代码实现：
# (你需要先 import random)

import random
import json
import os


# --- 工具函数区 ---


def get_user_guess():
    while True:
        # 获取用户输入并转为整数
        user_input = input("请输入一个整数（或输入 'q' 退出）：")
        # 处理用户直接退出的情况
        if user_input.lower() == 'q':
            return 'q'
        try:
            return int(user_input)
        except ValueError:
            print("⚠️ 输入无效，请输入一个整数（或输入 'q' 退出）。")


def check_guess(guess, secret):
    if guess > secret:
        return "大了", False
    elif guess < secret:
        return "小了", False
    else:
        return "猜对了", True


# 主逻辑区
def play_game():
    # 1. 电脑生成随机数
    random_number = random.randint(1, 100)

    count = 0
    limit_the_number_of_times = 10

    print(f"我想了个1-100之间的数字，你来猜猜看；最多猜{limit_the_number_of_times} 次")

    while count < limit_the_number_of_times:
        guess = get_user_guess()
        if guess == 'q':
            print(f"游戏结束，正确答案是{random_number}")
            return False, count, random_number

        count += 1
        message, is_correct = check_guess(guess, random_number)
        print(message)
        if is_correct:
            print(f"恭喜你，猜对了，答案是{random_number}，你一共猜了{count}次")
            return True, count, random_number
    # 如果循环结束还没猜中
    print(f"游戏结束，正确答案是{random_number}")
    return False, count, random_number


#
# 你的练习任务
# 现在轮到你了！请尝试做以下修改，巩固对函数的理解：
# 任务：添加一个“评分函数”
# 定义一个新函数 get_rating(count)。
# 如果 count <= 3，返回 "🌟🌟🌟 神级玩家"
# 如果 count <= 5，返回 "🌟🌟 高手"
# 否则，返回 "🌟 新手村学员"
# 在 play_game 函数中，当用户猜对时，调用这个新函数，并把评级打印出来。
# 例如：print(f"评级：{get_rating(count)}")
# 你想试试写出这个 get_rating 函数并把它集成进去吗？
# 直接把修改后的代码片段发给我，或者告诉我你在哪一步卡住了！💻✨


def scores(count):
    if count <= 3:
        return "神级玩家"
    elif count <= 5:
        return "高手"
    else:
        return "新手村学员"


def record_game():
    #
    #
    # 📊 数据分析时间：让数据更有意义
    # 既然数据已经存下来了，我们能不能让它“说话”？
    # 现在的列表里躺着两局战绩，我们可以轻松算出：
    # 总共玩了几局？
    # 平均猜了多少次才赢？
    # 最好成绩（最少次数）是多少？
    # 让我们加最后一段代码，在游戏结束（用户输入 n）后，自动统计并打印一份“战绩报告”。
    # 假设 history 是你已经收集好的那个列表
    if len(history) > 0:
        print("\n" + "=" * 30)
        print("📊 本局游戏战绩报告")
        print("=" * 30)
        # 1. 总局数
        total_games = len(history)
        print(f"总局数：{total_games}")

        # 2. 提取所有获胜的局数（防止有输的局混进来拉低平均分，这里只算赢的）
        win_count = [game["count"] for game in history if game["result"] == "win"]
        print(f"win_count:{win_count}")

        if win_count:
            # 计算平均次数
            avg_cout = sum(win_count) / len(win_count)
            print(f"平均次数：{avg_cout:.2f}")
            # 找出最好成绩（次数最少）
            best_count = min(win_count)
            print(f"最好成绩：{best_count}")
            # 找出最差成绩
            bad_count = max(win_count)
            print(f"最差成绩：{bad_count}")
        else:
            print("可惜没有获胜记录")
        print("=" * 30)
        # 2. 【存档】程序退出前保存数据
        print("\n💾 正在保存战绩...")
        try:
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(history, f, ensure_ascii=False, indent=4)
                print("保存成功")
        except Exception as e:
            print(f"数据保存错误：{e}")
    else:
        print("没有游戏记录")


# --- 🚀 程序入口 ---
if __name__ == '__main__':
    # --- 📂 文件名定义 ---
    DATA_FILE = "game_history.json"

    # 1. 【读档】程序启动时加载历史数据
    print("欢迎来到猜数字游戏")
    history = []

    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                history = json.load(f)
                print("历史数据加载成功")
        except Exception as e:
            print(f"数据文件读取错误：{e}")
else:
    print("没有历史数据")

while True:
    is_win, count, random_number = play_game()
    if is_win:
        level = scores(count)
        print(f"太厉害了，评级为{level}」")
        result = {
            "result": "win",
            "count": count,
            "random_number": random_number,
        }
        history.append(result)

    else:
        print("下次再接再厉")
        result = {
            "result": "lose",
            "count": count,
            "random_number": random_number,
        }
        history.append(result)
    # 是否再来一局
    play_again = input("是否再来一局？(y/n)")
    if play_again.lower() != 'y':
        print(history)
        record_game()
        break
