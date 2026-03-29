import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

# 1. 初始化模型
load_dotenv()
llm = ChatOpenAI(
    model="qwen-plus",
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
)


# 2. 定义结构化提示词的函数
def structured_prompt_words(role, task, constraints, example_input, example_output, user_input):
    # 这里我们手动拼接一个结构化的 Prompt
    # 使用三个引号 """ 来包裹内容，防止内容里有特殊字符干扰

    prompt = f"""
    # 角色
    {role}
    #任务
    {task}
    #约束
    {constraints}
    #示例输入
    {example_input}
    #示例输出
    {example_output}
    #用户输入
    {user_input}
    """
    return prompt


# 3. 填空区域（你可以随意修改这里的内容）

my_role = "你是一个脱口秀演员"
my_task = "把用户输入的内容用脱口秀的方式表达出来"
my_constraints ="1.搞笑 2.markdow格式 3.尽量简洁"
# 示例（Few-Shot）
my_example_input = "韩信"
my_example_output ="我韩信，用一生演示了什么叫“顶级技术岗在行政岗公司没有好下场”。希望大家以后跳槽慎重！谢谢大家！"


# 实际要问的问题
my_user_input = "吕后"

# 4. 生成并发送
final_prompt = structured_prompt_words(my_role, my_task, my_constraints, my_example_input, my_example_output, my_user_input)
print(f"正在发送结构化提示词...\n{final_prompt}\n")

result = llm.invoke(final_prompt)

print("模型回复：\n"+result.content)
