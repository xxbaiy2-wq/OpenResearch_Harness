# 从env读配置
from pydantic_settings import BaseSettings
# pydantic_settings , 帮助从.env文件中读取配置
# BaseSettings 模板类，继承他自动读取环境变量

class Settings(BaseSettings):
    app_env: str = "dev" # 默认值是 "dev"（开发环境）
    database_url: str # 数据库地址，没有默认值 → 必须从 .env 文件读，不写就报错
    # 不给默认，因为：数据库地址每个环境都不同（你的电脑、服务器、测试环境），给默认值容易误连别人的数据库
    redis_url: str = "redis://localhost:6379/0" # 有默认值，env没写时候用这个
    mimo_api_key: str = ""
    mimo_base_url: str = "https://token-plan-sgp.xiaomimimo.com/v1"
    mimo_model: str = "mimo-v2.5-pro"



    class Config:
        env_file = ".env"  # 指定.env文件路径，去env找这些配置

# 全局实例
# 可以让别的使用，
# from core.config import settings
# print(settings.database_url)  # 直接拿到数据库地址

settings = Settings() # 从.env文件读取配置，创建全局实例

# 第一次写写错了，Config应该是Setting的内部类
# pydantic_settings 是靠查找 Settings 内部的 Config 类来知道去哪读 .env 的。