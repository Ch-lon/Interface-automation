import json
import unittest
import settings
from common.log_handler import logger
from common.db_handler import db
from common.test_data_handler import get_cases_from_excel
from concurrent.futures import ThreadPoolExecutor, wait
from common.db_handler_Optimization import DB  # 使用优化后的连接池版本


class BaseTestCase(unittest.TestCase):
    name = None  #接口名称
    logger = logger
    db = db
    settings = settings

    @classmethod
    def setUpClass(cls) -> None:
        # 类前置
        cls.logger.info(f"{cls.name}测试开始")

    @classmethod
    def tearDownClass(cls) -> None:
        # 类后置
        cls.logger.info(f"{cls.name}测试结束")

    @classmethod
    def load_cases(cls, sheet_name):
        """
        提取Excel文件中的用例数据
        :param sheet_name: 测试用例文件中的sheet
        :return:
        """
        return get_cases_from_excel(settings.TEST_DATA_DIR, sheet_name)

    @classmethod
    def split_fields(cls, id, st: str, symbol='；'):
        """
        分隔字符串
        :param id: 测试用例编号
        :param st: 指定字符串
        :param symbol: 指定分隔符
        :return: 分隔后的字符串列表
        """
        result = []
        try:
            # 检查字符串中是否包含分隔符
            if symbol in st:
                result = st.split(symbol)
            else:
                # 如果不包含分隔符，直接返回原字符串作为列表的唯一元素
                result = [st]
        except Exception as e:
            cls.logger.exception(f'测试用例{id}预期结果的【{st}】字符串分隔失败')
            raise e
        return result

    @classmethod
    def assert_log(cls, case, request_data, expect_data, response_data):
        """
        断言日志
        :param case: 测试用例字典
        :param request_data: 请求参数
        :param expect_data: 预期结果
        :param response_data: 实际结果
        :return: 不需要返回值
        """
        cls.logger.exception(f'{case["id"]}-{case["title"]}：：测试失败')
        cls.logger.exception(f'请求数据是{request_data}')
        cls.logger.exception(f'期望结果是{expect_data}')
        cls.logger.exception(f'实际结果是{response_data}')

    @classmethod
    def success_log(cls, case):
        """
        测试通过的日志描述
        :param case:
        :return:
        """
        cls.logger.info(f"✅ 测试用例{case['id']}【验证通过】-{case['title']}")

    @classmethod
    def execute_sqls_in_parallel(cls, sql_list, operation_func):
        """
        并行执行 SQL 列表
        :param sql_list: SQL 列表
        :param operation_func: 操作函数（如 db.get_all 或 db.del_data）
        """
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = []

            def task(sql1):
                with DB() as db1:
                    try:
                        return operation_func(db1, sql1)
                    except Exception as e:
                        logger.error(f"SQL 执行失败: {sql1}, 错误: {str(e)}")
                        raise e

            for sql in sql_list:
                if sql.strip():
                    futures.append(executor.submit(task, sql))

            wait(futures)  # 等待所有任务完成
            for future in futures:
                future.result()  # 触发异常抛出

if __name__ == '__main__':
    base = BaseTestCase
    res = base.load_cases('upload')
    print(res)
