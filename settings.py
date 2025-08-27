# 配置文件

import os

# 项目根目录
BASE_DIR =os.path.dirname(os.path.abspath(__file__))

# 项目的Host（开发环境）
PROJECT_HOST = 'https://gdw-dev2406s.gaojidata.com/api'

# 接口信息
INTERFACE = {
    'upload' : '/v1/detail/upload',
    'inspection' : '/v1/detail/check',
    'download' : '/v1/mergetal/download'
}

# 数据库配置(开发库)
DATABASE_CONFIG = {
    'host' : 'gj2302po.pg.rds.aliyuncs.com',
    'port' : '5432',
    'user' : 'gaojidev',
    'password' : 'GyqF3YSgvYQySMp5N3qn',
    'database' : 'gdw_0627',
}

# token
TEST_AUTH_TOKEN = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NjYwNzcxODMsImp0aSI6Imhla3VuLmZlbmcgMyBiMFRKaElFMDRYUUN1cnRVbldGTHRuN081OWpJblI3WUdNSzhFaFRYcEtZPSAyNDYgMiwzLDQiLCJpc3MiOiJoZWt1bi5mZW5nIn0.CP-lUoT4nbxfYKhPnoS9jRbRPbCyu0xhf-pr6XK0pL4'

AUTH_COOKIE = {
    'authToken': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NjYwNzcxODMsImp0aSI6Imhla3VuLmZlbmcgMyBiMFRKaElFMDRYUUN1cnRVbldGTHRuN081OWpJblI3WUdNSzhFaFRYcEtZPSAyNDYgMiwzLDQiLCJpc3MiOiJoZWt1bi5mZW5nIn0.CP-lUoT4nbxfYKhPnoS9jRbRPbCyu0xhf-pr6XK0pL4'  # 从原硬编码复制过来
}

# 接口返回的无异常sheet的描述文本
RESPONSE_NORMAL_SHEET_TEXT = '暂未发现异常'

# 接口返回的基础校验不通过的文本
RESPONSE_BASIC_VERIFICATION_FAILED_TEXT = '未通过基础校验'

# 测试数据配置
TEST_DATA_DIR =os.path.join(BASE_DIR, 'test_data', 'cases.xlsx')

# 测试文件路径
TEST_FILE_DIR = os.path.join(BASE_DIR, 'test_data', 'test_file')

# 测试用例（类）路径
TEST_CASES_DIR = os.path.join(BASE_DIR, 'test_cases')

# 异常文件保存路径
ERROR_FILE_SAVE_DIR = os.path.join(BASE_DIR, 'test_data', 'error_file')
print(ERROR_FILE_SAVE_DIR)
# 配置allure结果路径
ALLURE_RESULT_DIR = os.path.join(BASE_DIR, 'allure-result')


# 日志配置
LOG_CONFIG = {
    'name' : '数仓测试日志',
    'file' : os.path.join(BASE_DIR, 'log', 'SC.log'),
    'fmt' : "%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d | %(message)s",
    'debug' : True
}