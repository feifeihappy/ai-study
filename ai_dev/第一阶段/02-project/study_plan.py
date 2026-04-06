import yaml
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
import os
from dotenv import load_dotenv
import json

import os
import yaml

# 1. 获取当前脚本所在的目录
# 结果：.../ai_dev/第一阶段/02-project
current_dir = os.path.dirname(os.path.abspath(__file__))

# 2. 构建目标文件路径
# os.path.pardir 代表上一级目录 (..)
# 我们需要退两级：02-project -> 第一阶段 -> ai_dev
# 然后再进入 prompts 文件夹
file_path = os.path.join(
    current_dir,
    os.path.pardir,  # 退一级：到 "第一阶段"
    os.path.pardir,  # 再退一级：到 "ai_dev"
    'prompts',  # 进入 "prompts"
    'templates.yaml'  # 目标文件
)

# 3. 规范化路径（把 .. 这种符号变成真实的绝对路径，方便排查）
file_path = os.path.abspath(file_path)

print(f"🔍 正在尝试读取：{file_path}")

# 4. 读取文件
try:
    with open(file_path, 'r', encoding='utf-8') as f:
        templates = yaml.safe_load(f)
    print("✅ 成功加载提示词库！")
    print(templates)  # 打印看看内容
except FileNotFoundError:
    print("❌ 错误：文件未找到！")
    print("请检查路径是否正确，或者文件是否存在。")

# 1. 加载提示词库
with open(file_path, 'r', encoding='utf-8') as f:
    prompts = yaml.safe_load(f)
    # 2. 获取模板
template = prompts['study_supervisor']['system']

raw_resume = """
1. 3 个月转 AI 应用开发工程师可执行每日计划

这是一个为你量身定制的3个月（12周）转行AI应用开发工程师的每日执行计划。
核心策略：
1. 不造轮子：不深究数学公式和底层算法，专注于调用API、使用框架、构建Agent。
2. 项目驱动：每周都有产出，从简单的对话机器人到复杂的RAG系统，最后是一个完整的商业级Demo。
3. 技术栈锁定：Python + LangChain/LlamaIndex + 向量数据库 (Chroma/Milvus) + 主流大模型API (国内可用模型) + 前端简易展示 (Streamlit)。

---
📅 第一阶段：基础夯实与工具链熟悉（第1-4周）
目标：掌握Python基础，理解Prompt工程，能调用大模型API，跑通第一个Hello World应用。
第1周：Python速成与环境搭建
- 重点：只学AI开发需要的Python语法（函数、类、装饰器、异步编程、JSON处理）。
- 每日计划：
  - 周一：安装Anaconda/Miniconda，配置VS Code。学习Python基础变量、列表、字典。
  - 周二：学习函数、模块导入、异常处理。练习读取本地文件（txt, json, csv）。
  - 周三：学习面向对象（Class），理解__init__和方法。这是理解LangChain组件的基础。
  - 周四：关键！ 学习asyncio（异步编程）和requests库。大模型调用通常是异步的。
  - 周五：学习虚拟环境管理 (venv/conda) 和 pip 包管理。安装 openai (或兼容库), langchain。
  - 周六：实战小项目：写一个脚本，读取本地文本文件，调用大模型API进行摘要，并保存结果。
  - 周日：复习本周内容，整理笔记，解决环境报错问题。
第2周：Prompt Engineering（提示词工程）精通
- 重点：学会如何“指挥”模型，这是应用开发的核心能力。
- 每日计划：
  - 周一：学习Prompt基本结构（角色、任务、约束、示例）。测试不同模型的反应。
  - 周二：学习Few-Shot Prompting（少样本提示）。通过给例子让模型模仿格式。
  - 周三：学习CoT (Chain of Thought) 思维链。让模型展示推理过程，提高准确率。
  - 周四：学习结构化输出。强制模型输出JSON格式，以便代码解析。
  - 周五：学习提示词优化技巧（如：自我反思、分步拆解）。
  - 周六：实战小项目：构建一个“简历优化助手”。输入粗糙简历，输出符合JSON格式的优化建议，并自动评分。
  - 周日：研究市面上优秀的Prompt案例（如Awesome Prompts），建立自己的Prompt库。
第3周：LangChain框架入门（核心）
- 重点：掌握业界最火的编排框架，理解Model, Prompt, Chain, OutputParser。
- 每日计划：
  - 周一：理解LangChain核心概念。安装langchain, langchain-community。
  - 周二：学习ChatModel和PromptTemplate。将上周的Prompt模板化。
  - 周三：学习LLMChain和SequentialChain。串联多个步骤（如：翻译->润色->格式化）。
  - 周四：学习OutputParser。自动将模型输出的字符串转为Python对象。
  - 周五：学习Memory（记忆机制）。让对话机器人能记住上下文。
  - 周六：实战小项目：做一个“多轮对话心理咨询师”。具备人设、记忆功能，能根据用户情绪调整回复。
  - 周日：阅读LangChain官方文档中关于“Concepts”的部分，查漏补缺。
第4周：第一个完整应用上线
- 重点：结合前端，把脚本变成可交互的应用。
- 每日计划：
  - 周一：学习Streamlit基础。快速构建网页界面（输入框、按钮、聊天窗口）。
  - 周二：将第3周的“心理咨询师”接入Streamlit，实现网页版对话。
  - 周三：学习部署基础。了解如何在本地运行，尝试使用streamlit cloud或简单的Docker容器。
  - 周四：优化用户体验。增加加载动画、错误处理、侧边栏设置（如调节Temperature）。
  - 周五：代码重构。将逻辑分层（UI层、逻辑层、数据层），符合工程规范。
  - 周六：阶段里程碑项目：发布你的第一个AI应用——“智能周报生成器”（输入工作流水账，生成周报）。
  - 周日：复盘前四周，整理GitHub仓库，写好README文档。

---
📅 第二阶段：进阶技能与RAG实战（第5-8周）
目标：掌握检索增强生成（RAG），让AI能利用私有数据回答问题，解决幻觉问题。
第5周：向量数据库与Embedding
- 重点：理解“语义搜索”，让机器读懂文字的含义。
- 每日计划：
  - 周一：理解Embedding原理（文字变向量）。调用Embedding API。
  - 周二：学习向量数据库概念。安装并使用ChromaDB（轻量级，适合本地）。
  - 周三：学习数据加载器 (Document Loaders)。读取PDF, Word, Markdown文件。
  - 周四：学习文本分割 (Text Splitters)。按字符、递归方式切分长文档。
  - 周五：实战：构建一个简单的知识库索引流程（加载->分割->向量化->存储）。
  - 周六：实战小项目：做一个“个人笔记问答机器人”。上传你的Markdown笔记，问它关于笔记的内容。
  - 周日：尝试其他向量库（如FAISS或国内的Milvus轻量版），对比差异。
第6周：RAG（检索增强生成）深度实践
- 重点：将检索到的内容作为上下文喂给大模型。
- 每日计划：
  - 周一：学习LangChain的RetrievalQA链。最简单的RAG实现。
  - 周二：优化检索策略。学习Similarity Search vs MMR (最大边际相关性)。
  - 周三：解决“查不准”问题。学习元数据过滤（按日期、标签筛选文档）。
  - 周四：解决“答不好”问题。优化Prompt，让模型基于检索内容回答，不知道就说不知道。
  - 周五：学习多路召回（混合搜索：关键词+向量）。
  - 周六：实战小项目：构建“企业制度问答助手”。上传公司员工手册，员工可查询休假、报销政策。
  - 周日：调试RAG效果，记录Bad Case（回答错误的案例）并分析原因。
第7周：高级RAG与数据处理
- 重点：处理复杂文档（表格、图片），提升回答精度。
- 每日计划：
  - 周一：处理表格数据。学习如何将Excel/PDF表格转换为模型易懂的格式。
  - 周二：学习父子索引（Parent-Child Retrieval）。检索小块，送入大块上下文。
  - 周三：学习重排序（Rerank）。引入BGE-Reranker等模型优化检索结果顺序。
  - 周四：处理长文档总结。使用Map-Reduce或Refine策略处理超长文本。
  - 周五：整合所有优化技巧，重构第6周的项目。
  - 周六：实战小项目：构建“法律/医疗合同审查助手”（模拟）。上传合同，自动提取风险条款并解释。
  - 周日：深入研究一个开源RAG项目（如LangChain Chat with Your Data），看源码。
第8周：中期大作——知识库系统
- 重点：打造一个功能完备、界面友好的RAG系统。
- 每日计划：
  - 周一：需求分析与架构设计。确定功能：文件上传、多轮对话、引用来源显示、历史记录。
  - 周二：后端逻辑开发。封装RAG链，处理文件上传和清洗逻辑。
  - 周三：前端交互开发。使用Streamlit实现文件上传组件、对话气泡、引用跳转。
  - 周四：增加高级功能。支持多种文件格式，增加“清除上下文”按钮。
  - 周五：性能优化与测试。测试大文件加载速度，优化响应时间。
  - 周六：里程碑项目：完成“智能文档分析平台”V1.0，并录制演示视频。
  - 周日：将代码上传GitHub，撰写详细的技术博客（这是面试加分项）。

---
📅 第三阶段：Agent智能体与工程化落地（第9-12周）
目标：让AI具备“手”和“脑”，能调用工具、规划任务，并完成一个商业级项目。
第9周：Function Calling 与工具调用
- 重点：让大模型能联网、查天气、查数据库。
- 每日计划：
  - 周一：理解Function Calling原理。定义工具描述（Name, Description, Parameters）。
  - 周二：学习LangChain Tools。使用内置工具（搜索、计算器、终端）。
  - 周三：自定义工具。写一个Python函数（如查数据库、调内部API），封装成Tool给AI用。
  - 周四：学习AgentExecutor。让模型自主决定调用哪个工具。
  - 周五：调试Agent。解决模型乱调用工具或死循环的问题。
  - 周六：实战小项目：做一个“股票/天气查询助手”。用户问“北京明天天气如何？”，AI自动调用天气API回答。
  - 周日：研究国内大模型（如通义千问、文心一言）的Function Calling特性。
第10周：多Agent协作与复杂任务规划
- 重点：模拟团队工作，让多个AI角色协作完成任务。
- 每日计划：
  - 周一：学习ReAct范式（Reasoning + Acting）。
  - 周二：学习Plan-and-Solve。让AI先制定计划，再一步步执行。
  - 周三：了解多Agent框架（如LangGraph或AutoGen概念）。
  - 周四：实战：构建一个“研究员Agent”和一个“写作员Agent”，协作写文章。
  - 周五：引入人类反馈（Human-in-the-loop）。在关键步骤让真人确认。
  - 周六：实战小项目：构建“自动化新闻简报生成器”。自动搜索新闻->筛选->总结->发邮件（模拟）。
  - 周日：思考业务场景，构思最终毕业项目的功能。
第11周：毕业项目开发（全栈实战）
- 重点：从零打造一个解决实际问题的商业级Demo。
- 选题建议：智能客服系统、个性化学习导师、自动化数据分析报告生成器。
- 每日计划：
  - 周一：立项与原型设计。画出流程图，确定技术栈。
  - 周二：搭建后端骨架。数据库设计、API接口定义、核心Agent逻辑。
  - 周三：核心功能开发。实现RAG检索、工具调用、多轮对话管理。
  - 周四：前端开发与联调。美化界面，确保交互流畅。
  - 周五：边缘情况处理。网络超时、敏感词过滤、错误提示。
  - 周六：全天冲刺。完善功能，修复Bug，准备演示数据。
  - 周日：内部测试。找朋友试用，收集反馈并快速迭代。
第12周：部署、优化与求职准备
- 重点：将项目推向生产环境，准备简历和面试。
- 每日计划：
  - 周一：容器化。编写Dockerfile，确保环境一致性。
  - 周二：云部署。尝试部署到阿里云/腾讯云/华为云的轻量服务器，或使用Vercel/Streamlit Cloud。
  - 周三：监控与日志。添加简单的日志记录，观察用户使用情况。
  - 周四：简历优化。将这三个项目（特别是毕业项目）详细描述在简历上，突出技术难点和解决方案。
  - 周五：面试模拟。准备常见问题（RAG原理、Agent流程、如何处理幻觉、Token成本优化）。
  - 周六：作品集整理。确保GitHub代码整洁，有README，有演示视频链接。
  - 周日：毕业典礼。投递简历，开始在招聘软件上联系猎头/HR，正式开启求职之路。

---
💡 每日时间表建议（全职学习版）
- 09:00 - 11:00：理论学习。阅读文档、观看教程视频、理解概念。
- 11:00 - 12:00：代码复现。跟着教程敲一遍代码，确保跑通。
- 14:00 - 17:00：独立实战。脱离教程，自己尝试修改功能、增加特性，或者做当天的“实战小项目”。这是最重要的环节！
- 17:00 - 18:00：调试与排错。解决下午遇到的Bug，利用StackOverflow、官方文档、AI助手解决问题。
- 20:00 - 21:00：复盘与记录。写技术博客或笔记，记录今天学到了什么，遇到了什么坑。
🛠️ 必备资源清单
1. 文档：LangChain官方文档 (必读), LlamaIndex文档。
2. 模型：注册国内大模型开放平台账号（阿里百炼/通义、百度千帆、智谱AI、月之暗面），获取API Key。
3. 社区：知乎（关注黄佳、李沐等）、GitHub（搜LangChain projects）、Hugging Face。
4. 工具：VS Code, Git, Postman (测API), Draw.io (画架构图)。
⚠️ 避坑指南
- 不要陷入环境配置的泥潭：遇到报错直接复制去搜，不要在一个环境问题上卡超过2小时，必要时重装或换方案。
- 不要追求完美：第一版代码很烂没关系，能跑就行。先完成，再完美。
- 不要只看不练：看懂了不代表会写了。代码必须亲手敲。
- 关注成本：调用API是要花钱的（虽然很少），注意控制频率，本地测试尽量用免费额度或小模型。
这份计划强度较大，但只要你坚持下来，3个月后你将拥有3个可展示的项目和一套完整的AI应用开发技能树，足以胜任初级到中级AI应用开发工程师的岗位。加油！
"""
# 3. 填入参数
final_prompt = template.format(target_job='ai应用开发工程师', study_plan=raw_resume)

# 4. 初始化模型
load_dotenv()
llm = ChatOpenAI(
    model="qwen-plus",
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
)
# 5. 发送给模型
result = llm.invoke(final_prompt)
print(result.content)
