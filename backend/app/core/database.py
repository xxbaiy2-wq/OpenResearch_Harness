# 链接mysql，提供session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app.core.config import settings


class Base(DeclarativeBase): # ORM基类，所有ORM模型都要继承这个类,orm，python操作数据库而不用sql语句
    pass
# Base = 所有表的"爸爸"，它自己不对应任何表，但给了所有子类操作数据库的能力。

'''
连接池-底层 TCP 连接
每次操作数据库都要建立 TCP 连接 → 验证身份 → 执行SQL → 关闭连接
如果 100 个请求同时进来：
每次新建连接 → 很慢，数据库也扛不住
连接池 = 提前维护一批连接，用的时候拿一个，用完归还
'''
engine = create_engine(settings.database_url)

'''
会话工厂，代码不直接操作tcp链接-需要一个操作界面Session，界面上操作
像饼干模具，你调用它一次就得到一个新的 session：
db = SessionLocal()   # 拿到一个新 session
db.query(...)          # 用它操作数据库
db.close()             # 用完关掉
'''
SessionLocal = sessionmaker(bind=engine)

# 依赖注入函数，不用手动创建/关闭 session
# 给 FastAPI 的路由用的
# return:  函数把值交出去，函数就结束了
# yield:   函数把值交出去，但函数还"活着"，等调用方用完了才继续执行后面的代码
# 请求处理期间 db 一直可用，请求结束后 finally 自动关闭。

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
