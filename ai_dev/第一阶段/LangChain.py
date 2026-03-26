import json


class MyModel:
    def __init__(self, model_name):
        self.model_name = model_name

    def invoke(self, input_text):
        print(f"[{self.model_name}] 正在思考：{input_text[:20]}...")
        # 模拟大模型返回一段 JSON 字符串
        return json.dumps({
            "setup":""+input_text+"不带伞？",
            "punchline":"因为他们自带云存储",
            "rating":8
        })

# 2. 模拟 Prompt 组件
class MyPrompt:
    def __init__(self, template):
        self.template = template # 保存模板字符串

    def format(self,**kwargs):
        result = self.template
        for key, value in kwargs.items():
            result = result.replace("{"+key+"}", str(value))
        return result


# 3. 模拟 Chain (串联组件)
class MyChain:
    def __init__(self, step1, step2):
        self.step1 = step1  # 第一步：Prompt
        self.step2 = step2  # 第二步：Model

    def invoke(self, inputs):
        # 流程：输入 -> Prompt格式化 -> Model推理
        prompt_result = self.step1.format(**inputs)
        final_result = self.step2.invoke(prompt_result)
        return final_result

# --- 🎬 开始演出 ---

# A. 初始化组件 (调用 __init__)
# 这就像你在写: prompt = ChatPromptTemplate.from_messages(...)
my_prompt = MyPrompt("请讲一个关于 {topic} 的笑话，返回 JSON。")

# 这就像你在写: llm = ChatOpenAI(model="deepseek-chat")
my_llm = MyModel(model_name="DeepSeek-V3")

# 这就像你在写: chain = prompt | llm
my_chain = MyChain(step1=my_prompt, step2=my_llm)

# B. 运行 (调用方法)
print("\n--- 运行迷你 LangChain ---")
response = my_chain.invoke({"topic": "架构师"})

# C. 解析结果
data = json.loads(response)
print(f"\n✅ 结构化结果:")
print(f"铺垫: {data['setup']}")
print(f"笑点: {data['punchline']}")