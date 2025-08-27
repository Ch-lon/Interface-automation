import psycopg2
from dbutils.pooled_db import PooledDB
import settings
import threading


# ==================== 数据库连接池类 ====================
class DBPool:
    def __init__(self, **kwargs):
        # 使用 dbutils 创建线程安全的连接池
        self.pool = PooledDB(
            creator=psycopg2,  # 使用 psycopg2 作为数据库驱动
            **kwargs
        )

    def connection(self):
        # 从连接池中获取一个连接
        return self.pool.connection()


# 实例化连接池（单例）
db_pool = DBPool(**settings.DATABASE_CONFIG)


# ==================== 数据库操作类 ====================
class DB:
    def __init__(self):
        # 从连接池获取一个数据库连接
        self.conn = db_pool.connection()
        self.cursor = self.conn.cursor()

    def __enter__(self):
        # 支持 with 语句进入时返回自身
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # 自动关闭游标和连接（归还连接到池）
        self.cursor.close()
        self.conn.close()
        self.cursor = None
        self.conn = None

    def get_all(self, sql):
        """
        获取全部的查询结果
        :return:
        """
        self.cursor.execute(sql)
        return self.cursor.fetchall()

    def del_data(self, sql):
        """
        执行删除操作
        :param sql:
        :return:
        """
        self.cursor.execute(sql)
        self.conn.commit()

    def __del__(self):
        """确保关闭游标和连接，避免重复关闭"""
        try:
            if self.cursor:
                self.cursor.close()
        except Exception as e:
            raise '游标关闭失败'
        try:
            if self.conn:
                self.conn.close()
        except Exception as e:
            raise '数据库连接关闭失败'


# ==================== 多线程并发查询函数 ====================
def run_query(query_id, sql):
    """
    线程执行函数：执行指定 SQL 查询并输出结果
    :param query_id: 查询 ID（用于区分不同线程）
    :param sql: 要执行的 SQL 语句
    """
    with DB() as db:
        result = db.get_all(sql)
        print(f"[线程 {threading.get_ident()}] 查询 {query_id} 结果: {result}")


# ==================== 主程序入口 ====================
if __name__ == '__main__':
    # 定义要并发执行的 SQL 查询
    queries = [
        ("Education", "SELECT * FROM details.talent_education LIMIT 1"),
        ("Talent", "SELECT * FROM details.talent LIMIT 1"),
        ("Resume", "SELECT * FROM details.talent_resume LIMIT 1")
    ]

    # 创建并启动线程
    threads = []
    for query_id, sql1 in queries:
        thread = threading.Thread(target=run_query, args=(query_id, sql1))
        threads.append(thread)
        thread.start()

    # 等待所有线程完成
    for thread in threads:
        thread.join()

    print("所有查询已完成")