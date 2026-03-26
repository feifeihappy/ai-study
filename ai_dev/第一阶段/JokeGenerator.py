class JokeGenerator:
    # __init__ 是创建对象时自动运行的第一个方法
    # self 代表“刚刚出生的这个对象实例”
    def __init__(self, model_name, api_key, temperature=0.7):
        print(f"🔧 正在初始化一个 {model_name} 助手...")

        # 将传入的参数保存为对象的“属性” (状态)
        self.model_name = model_name
        self.api_key = api_key
        self.temperature = temperature
        self.call_count = 0  # 内部状态：调用次数，外部不可见

    def generate(self, topic):
        # 方法内部可以直接使用 self.属性
        self.call_count += 1
        print(f"[{self.call_count}] 使用 {self.model_name} (温度:{self.temperature}) 生成关于 '{topic}' 的笑话...")
        # 模拟返回
        return f"这是一个关于 {topic} 的笑话。"


# --- 实战演示 ---
# 1. 实例化 (调用 __init__)
bot1 = JokeGenerator(model_name="deepseek-chat", api_key="sk-123")
bot2 = JokeGenerator(model_name="deepseek-reasoner", api_key="sk-456", temperature=0.2)

# 2. 使用方法
bot1.generate("程序员")  # 输出: [1] 使用 deepseek-chat ...
bot2.generate("数学")  # 输出: [1] 使用 deepseek-reasoner (温度:0.2) ...
bot1.generate("产品经理")  # 输出: [2] 使用 deepseek-chat ... (bot1 记得自己调用了2次)


