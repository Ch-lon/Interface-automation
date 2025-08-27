import psycopg2
import settings

class DB:
    """
    定义数据库类
    """
    def __init__(self, **kwargs):
        self.conn = psycopg2.connect(**kwargs)
        self.cursor = self.conn.cursor()

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
        self.cursor.close()
        self.conn.close()

db = DB(**settings.DATABASE_CONFIG)

if __name__ == '__main__':
    res =db.get_all("select * from details.v_var_detail_xp where ver_no = 2040 and x ->> 'elected_year' = '2040';")
    print(res[0][0])

