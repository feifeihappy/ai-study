from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
from typing import List, Optional
import os
from dotenv import load_dotenv

# 简历优化助手
#
# 解析简历：把乱七八糟的文本变成结构化数据。
# 智能评分：根据STAR法则（情境、任务、行动、结果）给简历打分。
# 给出建议：把“负责了XX工作”改成“主导了XX项目，提升了30%效率”。

# 核心设计思路
# 咱们用 CoT（思维链） + 结构化输出 的组合拳：
# 先思考：让模型先分析简历的优缺点（内部思考，不输出）。
# 后打分：根据分析结果，给各个维度打分。
# 最后改写：针对薄弱项，给出具体的修改建议。

load_dotenv()

# 1. 定义输出结构（JSON Schema）
# 评分
class ResumeScore(BaseModel):
    total_score: int = Field(description="总分 0-100")
    clarity: int = Field(description="清晰度评分 0-10")
    impact: int = Field(description="影响力/成果量化评分 0-10")
    skills_match: int = Field(description="技能匹配度 0-10")

# 建议
class Suggestion(BaseModel):
    original_text: str = Field(description="原始文本片段")
    problem: str = Field(description="存在的问题")
    improved_text: str = Field(description="优化后的建议文本")

# 简历分析
class ResumeAnalysis(BaseModel):
    summary: str = Field(description="一句话评价")
    score:ResumeScore = Field(description="详细评分")
    strengths:list[str] = Field(description="简历亮点")
    suggestions:list[Suggestion] = Field(description="具体修改建议")

# 2. 初始化模型
llm = ChatOpenAI(
    model="qwen-plus",
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    temperature=0.3# 稍微有点创造性，但主要保持严谨
)
# 3. 绑定结构化输出
structured_llm = llm.with_structured_output(ResumeAnalysis)

# 4. 准备提示词（包含 CoT 指令）
prompt_template ="""
你是一位拥有10年经验的资深招聘专家和简历顾问。
请分析以下简历内容，并按照以下步骤进行思考（在内心完成，不要输出思考过程):
1.**扫描关键词**：识别候选人的核心技能和经验。
2.**评估STAR法则：检查经历是否包含情景、任务、行动、结果，特别是是否有量化数据。
3.**寻找废话**：找出“负责……”、“参与……”等缺乏力度的表达。
4.**打分与改写**：基于以上分析，给出评分和具体的润色建议。

请严格以json格式输出分析结果。
目标岗位：{target_job}
简历内容：{resume_text}

"""
# 5. 模拟一份“粗糙”的简历
raw_resume = """
---
赵鹏飞
10年Java开发经验 | 高级Java开发工程师 / 技术负责人
📞 156-0174-0602 | 📧 vim.zpf@gmail.com | 📍 上海/苏州/无锡
🔗 博客 | 🔗 GitHub
💰 期望薪资：16k-20k | 🎓 本科·计算机科学与技术·上海海洋大学

---
🔧 专业技能
- 核心基础：深入理解 JVM 原理（内存区域、内存模型、GC调优）、多线程并发（JUC、线程池）、集合框架；熟练掌握 Linux/Shell 服务器操作与部署。
- 主流框架：深入理解 Spring Framework (Boot, Core, AOP, IOC, MVC) 及源码；深入应用 MyBatis/MyBatis-Plus；熟悉 Spring Cloud (Eureka, Config, Feign, Gateway) 微服务生态。
- 分布式架构：熟练应用 Dubbo + Zookeeper 服务治理；深入实践 Spring Cloud Alibaba (Nacos)；掌握分布式事务解决方案 (Seata) 及配置中心 (Apollo)。
- 消息中间件：深入应用 RocketMQ (事务消息、顺序消息、延时消息)；熟悉 Kafka, RabbitMQ 的集群搭建、可靠性保障及解耦实践。
- 数据存储：
  - 关系型：精通 MySQL 索引优化、执行计划分析；深入应用 PostgreSQL (含 PostGIS 空间数据库)；熟悉 SelectDB (Doris) OLAP分析及 Oracle。
  - NoSQL：熟练 Redis (数据结构、持久化、集群、缓存策略、分布式锁)；熟练 MongoDB；熟悉 Elasticsearch (ELK/EFK日志栈)。
- DevOps & 云原生：熟练 Docker 容器化部署，了解Kubernetes (K8s) 基础编排；熟练 Nginx (负载均衡、反向代理)；熟悉 Jenkins CI/CD流水线。
- 设计与方法：熟练 UML 建模；深入理解并应用常用设计模式 (策略、工厂、模板、观察者等)；具备复杂系统 OOAD 分析与架构设计能力。
- 其他技能：熟练 Shiro/JWT 权限认证；具备 高并发处理、性能调优 及 系统重构 实战经验；拥有 技术团队管理 经验（需求分析、Code Review、任务拆解）。

---
💼 工作经历
2024.07 – 2026.02 | 波司登国际控股有限公司 (外包驻场：法本信息) | 高级Java开发工程师
- 项目一：全域CRM营销系统
  - 技术栈：Spring Boot, Spring Cloud Alibaba (Nacos), MyBatis-Plus, PostgreSQL, SelectDB, Redis, RocketMQ, SchedulerX, K8s
  - 核心职责：负责会员通接入、客户营销（事件营销、AI外呼、阅信、导购助手）、等核心模块设计与卡券管理开发。
  - 主要产出：
    - 架构重构：针对营销活动频繁变更痛点，基于策略模式+工厂模式+模板方法重构核心营销引擎，实现新活动规则配置化接入。
    - 性能提升：通过SQL深度优化调整，支撑大促期间 QPS峰值达1500+，核心接口平均响应时间控制在 200ms以内。
    - 效率成果：新供应商/新活动上线周期从 3天缩短至1天，代码重复率降低 40%，显著提升系统可维护性。
  - 三方集成：主导网易云商(AI外呼)、波司登导购助理(AI助手)、国都(阅信)等第三方服务的高效接入与稳定性保障。
- 项目二：渠道管理系统
  - 技术栈：Spring Boot, Spring Cloud Alibaba (Nacos), MyBatis-Plus, PostgreSQL, SelectDB, Redis, RocketMQ, SchedulerX, K8s
  - 核心职责：负责年度预算、渠道数据管理等核心模块。
  - 主要产出：
    - 动态解析引擎：设计基于 反射+POI 的动态Excel解析引擎，解决传统导入无提示及硬编码问题，导入效率提升 50%。
    - 全链路追踪：引入 AOP 实现导入任务全链路状态追踪与异常捕获，将批量数据导入效率提升50%，并提供可视化的错误数据报告。
2023.08 – 2024.06 | 上海焱豹科技有限公司 | 高级Java开发工程师 / 技术负责人
- 项目：焱豹全渠道租赁交易平台
  - 技术栈：Spring Boot, MyBatis-Plus, MySQL, Redis, Maven
  - 团队管理：带领 5人 团队，主导技术选型、方案评审、任务分解及Code Review；建立团队代码规范，推动部署自动化。
  - 核心重构：主导支付模块（微信/支付宝/代扣/芝麻免押）重构，优化支付路由与对账流程，显著提升交易成功率，客诉率降低30%。
  - 架构设计：在单体架构下通过划分高内聚，低耦合模块，支撑Web端、用户App、商户App多端业务高效迭代。
2021.11 – 2023.05 | 上海袋虎信息技术有限公司 | 高级Java开发工程师
- 项目：心理咨询服务平台
  - 技术栈：Spring Boot, Dubbo, Zookeeper, MySQL, MongoDB, Redis, Elasticsearch, Apollo, RocketMQ
  - 团队管理：团队内主导下单、商品、分销等核心服务开发，协调产品/前端/测试跨团队协作。
  - 业务重构：主导“代客下单”复杂流程重构，优化状态机流转逻辑，提升用户体验与下单转化效率；完成历史脏数据清洗修复。
  - 性能优化：设计基于策略+工厂模式的活动接入架构；优化开放平台（分销）接口，第三方接入响应速度提升 30%，吞吐量显著增加。
  - 高并发保障：利用Dubbo服务治理、RocketMQ异步削峰、Redis多级缓存，保障高并发场景下的系统稳定性。
2019.03 – 2021.10 | 新智道枢 (上海) 科技有限公司 | 中级Java开发工程师
- 昆明五华分局督察系统：基于 PostGIS 实现警情空间分析；设计递归算法处理多层级督察细项；基于Shiro构建精细化RBAC权限体系。
- 廊坊公安合成作战平台：主导海量警情数据表结构设计；利用 PostGIS (ST_Distance等) 实现高效的空间圈选与轨迹分析；通过 Kafka 实现预警指令异步解耦。
- 徐汇分局110处警指挥系统：主导全站 HTTPS 迁移；集成讯飞语音识别SDK实现语音指令调度；实施 Docker 容器化部署方案。
2018.02 – 2019.03 | 德邦快递 (瑞友科技) | 中级Java研发工程师
- 智慧车队数字化：在数据库中间件限制下，通过Java层复杂计算实现多维度组织指标（服务效率、投诉率等）关联展示；利用 Kafka 异步处理指标计算。
- 智能调度系统：采用 多线程+线程池 技术优化大数据量Excel导出功能，耗时从 5分钟缩减至30秒；对核心调度SQL进行深度调优。
2015.10 – 2018.02 | 天地华宇 | Java研发工程师
- Web华宇开放平台：设计基于Token的安全签名认证机制，保障外部系统接入安全；开发运单、订单、货物跟踪等核心API。
- OMS订单管理系统：实现多渠道订单定时分发与状态同步；开发自动异常处理流程，提升订单流转效率。
- Web易到家：应用 Redis 缓存热点数据减轻DB压力；利用 FTP+线程池 优化图片存储与后台任务处理效率。

"""


# 6. 目标岗位
target_job = "高级java开发工程师"

print(f"目标岗位：{target_job}")
print(f"待优化简历：\n{raw_resume}\n")
print("正在进行深度分析")

# 7. 调用模型
result = structured_llm.invoke(prompt_template.format(
    target_job= target_job,
    resume_text= raw_resume
))

# 8. 展示结果
print("简历诊断报告：")
print("-"*50)
print(f"【总体评价】{result.summary}")
print(f"【综合得分】{result.score.total_score/100}")
print(f"- 清晰度 {result.score.clarity}/10")
print(f"- 影响力 {result.score.impact}/10")
print(f"- 匹配度 {result.score.skills_match}/10")

print("\n【简历亮点】")
for s in result.strengths:
    print(f"- {s}")

print("\n【修改建议】")
for sug in result.suggestions:
    print("-"*30)
    print(f"原文{sug.original_text}" )
    print(f"问题{sug.problem}" )
    print(f"建议{sug.improved_text}" )








