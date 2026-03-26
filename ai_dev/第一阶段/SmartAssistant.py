class SmartAssistant:
    def __init__(self, name):
        self.name = name
        self.memory = []  # 每个助手有自己的记忆列表

    # 这是一个“方法”
    # 注意这里的 self，它让我们能访问到具体的 self.memory
    def remember(self, fact):
        print(f"🧠 {self.name} 记住了：{fact}")
        self.memory.append(fact)

    def speak(self):
        if not self.memory:
            return f"{self.name}: 我脑子一片空白。"

        # 使用 self 访问自己的数据
        last_thought = self.memory[-1]
        return f"{self.name}: 我记得最后一点是... {last_thought}"


# --- 演示 ---
alice = SmartAssistant("Alice")
bob = SmartAssistant("Bob")

alice.remember("Python 很有趣")
bob.remember("Java 很严谨")

alice.remember("LangChain 很强大")

print(alice.speak())
# 输出: Alice: 我记得最后一点是... LangChain 很强大
# (Alice 没记住 Bob 的事，因为 self.memory 是隔离的)

print(bob.speak())
# 输出: Bob: 我记得最后一点是... Java 很严谨