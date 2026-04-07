from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv
import os
import yaml
from pydantic import BaseModel, Field
from typing import List
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser

load_dotenv()


# 1. 初始化模型
llm = ChatOpenAI(
    model="qwen-plus",
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    temperature=0.7,
)

# 定义我们想要的数据结构

class HistoryAnalysis(BaseModel):
    event_type: str  = Field(description="事件类型,例如‘政变’，‘赏赐’，‘改革’")
    key_figure: str = Field(description="关键历史人物")
    summary: str = Field(description="对事件的学术性摘要")
    keywords:List[str] = Field(description="提取出的3-5个核心关键词")
    is_usurpation:bool = Field(description="是否属于篡位行为（True/False）")

# 1. 初始化 Parser
parser = PydanticOutputParser(pydantic_object=HistoryAnalysis)

# 2. 构建 Prompt
# 注意：我们在 user 模板里加入了 {format_instructions}
prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个专业的历史学家，擅长分析古代政治事件。"),
    ("user",
     """
         请分析以下历史片段：
         {input_text}

         {format_instructions}
         """
     ),
])

# 3. 把格式指令注入到 Prompt 中
# 这一步非常重要，它会自动生成一段提示词，告诉模型怎么输出 JSON
final_prompt = prompt.partial(format_instructions=parser.get_format_instructions())

# 第三步：组装链条
chain = final_prompt | llm | parser

# 第四步：运行并获取对象
input_text = "五月，策命￼安汉公莽以九锡，莽稽首再拜，受绿韨￼，衮冕￼、衣裳￼，玚琫￼、玚珌￼，句履￼，鸾路￼、乘马￼，龙旂九旒￼，皮弁￼、素积￼，戎路￼、乘马￼，彤￼弓矢、卢￼弓矢，左建朱钺￼，右建金戚￼，甲、胄￼一具，秬鬯￼二卣￼，圭瓒￼二，九命￼青玉珪二，朱户￼，纳陛￼，署￼宗官￼、祝官￼、卜官￼、史官￼，虎贲￼三百人。"

# 调用
result= chain.invoke({"input_text": input_text})

# 验证结果
print(type(result))  # 输出：<class '__main__.HistoryAnalysis'>
print(result)        # 输出：HistoryAnalysis(event_type='政变', ...)


# 直接访问属性（就像操作字典一样）
print(f"事件类型：{result.event_type}")
print(f"是否篡位：{result.is_usurpation}")
print(f"关键词：{result.keywords}")

