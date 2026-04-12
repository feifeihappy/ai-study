"""
logic/models.py
逻辑层：定义业务数据模型 (Schema)
"""
from typing import List
from pydantic import BaseModel, Field


class HistoricalAnalysis(BaseModel):
    """资治通鉴片段的结构化分析结果"""
    
    event_title: str = Field(description="事件标题，简练概括")
    event_type: str = Field(description="事件类型，如'政变', '战争'")
    summary: str = Field(description="事件摘要，100字以内")
    key_figures: List[str] = Field(description="涉及的关键历史人物列表")
    locations: List[str] = Field(description="涉及的地理位置列表")
    moral_lesson: str = Field(description="核心启示或司马光的评价观点")
    is_critical: bool = Field(description="是否为关键转折点")