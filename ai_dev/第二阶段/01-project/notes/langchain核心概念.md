# LangChain 核心概念

## Chain（链）

Chain 是把多个步骤串联起来的组件。就像一个流水线，上一步的输出是下一步的输入。

最常用的是 LCEL（LangChain Expression Language），用 `|` 符号连接：

```python
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

prompt = ChatPromptTemplate.from_template("翻译成英文: {text}")
model = ChatOpenAI(model="qwen-plus")

chain = prompt | model
result = chain.invoke({"text": "你好世界"})
```

## Agent（智能体）

Agent 与 Chain 的最大区别：Agent 能**自主决策**下一步做什么，Chain 走的是固定流程。

Agent 工作原理：观察 → 思考 → 行动 → 观察 → ... 直到完成任务。这就是 ReAct 模式。

## Tool（工具）

Tool 是 Agent 的"手"。常用工具：
- 搜索引擎（获取实时信息）
- 代码解释器（执行计算）
- 数据库查询（访问私有数据）
- 自定义 API（订机票、发邮件等）
