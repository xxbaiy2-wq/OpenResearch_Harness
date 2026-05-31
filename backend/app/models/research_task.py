from sqlalchemy import Column, Integer, String, Text, DateTime, func
from app.core.database import Base


class ResearchTask(Base):
    # 告诉 SQLAlchemy：这个类对应 MySQL 里叫 research_tasks 的表
    __tablename__ = "research_tasks"

    # 定义一列：整数类型，主键
    id = Column(Integer, primary_key=True, autoincrement=True)
    topic = Column(String(255), nullable=False)
    # text长文本，无长度限制
    description = Column(Text, nullable=True)
    status = Column(String(50), nullable=False, default="pending")
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
    # 用 MySQL 自己的 NOW() 函数设置默认时间，不是 Python 时间

'''
__tablename__ 是干什么的？
Column 和普通 Python 属性有什么区别？
普通变量，name=“人”，python管他，数据库不知道他；
topic = Column(String(255))，python管他，数据库也知道他，数据库里有个 topic 列，类型是 varchar(255)，这个列的值就是这个属性的值。
nullable=False，不允许为空
nullable=False 和 default="pending" 能同时存在吗？分别是什么意思？
status = Column(String(50), nullable=False, default="pending")
nullable=False：你插入一条记录时，必须给 status 一个值，不能传 None
default="pending"：如果你不传，自动设成 "pending"
'''