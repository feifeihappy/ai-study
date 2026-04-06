import os
import yaml
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv

load_dotenv()
# ==========================================
# 1. 路径修复与配置
# ==========================================
base_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.abspath(os.path.join(base_dir, '..', '..', 'prompts', 'templates.yaml'))

if not os.path.exists(file_path):
    raise FileNotFoundError(f"❌ 找不到配置文件: {file_path}")

# 加载 YAML
with open(file_path, 'r', encoding='utf-8') as f:
    templates = yaml.safe_load(f)

print("✅ 系统启动成功！提示词库已加载。")

# ==========================================
# 2. 初始化 LangChain 模型
# ==========================================
llm = ChatOpenAI(
    model="qwen-plus",
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    temperature=0.7,
)

# ==========================================
# 3. 主程序循环
# ==========================================
while True:
    print("\n" + "-" * 30 + " 🤖 AI 助手菜单 " + "-" * 30)
    # 动态显示可用的模板名称
    for i, key in enumerate(templates.keys()):
        print(f"{i + 1}. {key}")
    print("0. 退出")
    choice = input("\n请选择一个助手 (输入序号): ")
    if choice == "0":
        print("bye~")
        break
    # 获取选中的模板 Key (例如 'reading_supervisor')
    try:
        selected_key = list(templates.keys())[int(choice) - 1]
    except:
        print("无效的选择")
        continue
    template_config = templates[selected_key]

    # 构建 LangChain Prompt 对象
    # 这里自动识别 user 模板里的 {变量}
    prompt = ChatPromptTemplate.from_template(template_config['user'])
    # 构建 Chain: Prompt -> LLM
    chain = prompt | llm

    # ==========================================
    # 4. 根据模板收集用户输入
    # ==========================================

    print(f"\n--- 正在启动 [{selected_key}] ---")

    inputs = {}
    # 简单的逻辑：根据模板里的占位符询问用户
    # 比如 reading_supervisor 需要 reading_content
    if selected_key == 'reading_supervisor':
        content = input("📖 请输入你读的《资治通鉴》片段: ")
        inputs = {"reading_content": content}
    elif selected_key == 'study_plan':
        job = input("🎯 目标岗位: ")
        plan = input("📝 现有计划: ")
        inputs = {"target_job": job, "study_plan": plan}

    # 如果有其他模板，可以在这里加 elif...

    # ==========================================
    # 5. 调用并输出
    # ==========================================

    print(f"\n🤖 {selected_key} 正在思考...")

    try:
        response = chain.invoke(inputs)
        print("\n" + "=" * 30 + " 专家回复 " + "=" * 30)
        print(response.content)
        print("=" * 70)
    except Exception as e:
        print(f"❌ 错误: {e}")
