import pandas as pd
from sqlalchemy import create_engine

# 数据库配置
DB_config = {'user': 'root', 'password': '', 'host': 'localhost',
             'port': 3306, 'database': 'stock'}

engine = create_engine(
    "mysql+pymysql://{user}:{password}@{host}:{port}/{database}?charset=utf8mb4".format(**DB_config))

# 检查是否成功与数据库连接
try:
    with engine.connect() as conn:
        print("successfully connected to the database")
except Exception as e:
    print(f"Error connecting to the database: {e}")