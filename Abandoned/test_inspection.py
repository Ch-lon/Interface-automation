import json
import os
import re
import unittest
from urllib.parse import unquote  # 解码URL编码的文件名（如%E5%90%8D%E7%A7%B0.xlsx -> 名称.xlsx）

import settings
from common.request_handler import send_request
from libs.my_ddt import ddt, data
from common.base_test_case import BaseTestCase
from common.log_handler import logger
from common.test_data_handler import get_row_all_comments


@ddt
class TestInspection(BaseTestCase):
    name = '质检接口'
    cases = BaseTestCase.load_cases('Inspection')

    @data(*cases)
    def test_inspection_method(self, case):
        """
        质检接口测试
        :param case:
        :return:
        """
        # 1. 测试数据
        request_data = json.loads(case['request_data']) # 字典
        expect_data = json.loads(case['expect_data']) # 字典

        # 2. 测试步骤
        url = settings.PROJECT_HOST + settings.INTERFACE['inspection']
        test_file_name = request_data['excelFile']
        file_path = os.path.join(settings.TEST_FILE_DIR, test_file_name)
        save_path = r"/test_data/error_file"
        with open(file_path, 'rb') as f:
            files = {'excelFile': f}
            cookies = {
                'authToken': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NjYwNzcxODMsImp0aSI6Imhla3VuLmZlbmcgMyBiMFRKaElFMDRYUUN1cnRVbldGTHRuN081OWpJblI3WUdNSzhFaFRYcEtZPSAyNDYgMiwzLDQiLCJpc3MiOiJoZWt1bi5mZW5nIn0.CP-lUoT4nbxfYKhPnoS9jRbRPbCyu0xhf-pr6XK0pL4'
            }
            response = send_request(url, method='POST', files=files, cookies=cookies)
            if 'application/json' in response.headers['Content-Type']:
                # 3. 断言
                response_json = response.json()  # 获取 JSON 数据
                response_data = {'code': response_json.get('code'), 'msg': response_json.get('msg')}
                # expect_data = json.loads(case['expect_data'])  # 字典
                try:
                    self.assertEqual(response_data, expect_data)
                except Exception as e:
                    logger.exception(f'{case['title']}：：测试失败')
                    logger.exception(f'请求数据是{request_data}')
                    logger.exception(f'期望结果是{expect_data}')
                    logger.exception(f'实际结果是{response_data}')
                    raise e
                logger.info(f"文件{test_file_name}响应结果为{response.json()}")
            else:
                # a. 解析Content-Disposition
                content_disposition = response.headers.get('Content-Disposition', '')
                # expect_data = case['expect_data']
                if 'filename=' not in content_disposition:
                    filename = '未命名文件.xlsx'
                else:
                    # 提取URL编码的JSON字符串
                    encoded_json = content_disposition.split('filename=')[-1].strip('"')
                    try:
                        # 解码并解析JSON
                        json_data = json.loads(unquote(encoded_json))
                        raw_filename = json_data.get('name', '未命名文件.xlsx')
                    except Exception as e:
                        logger.warning(f"{test_file_name}解析文件名失败: {e}，使用原始值")
                        raw_filename = unquote(encoded_json)  # 备用方案

                # b. 清洗文件名（Windows非法字符处理）
                invalid_chars = r'[\\/*?:"<>|]'  # Windows禁止的字符
                sanitized_name = re.sub(invalid_chars, '_', raw_filename)

                # c. 安全拼接路径（自动补全斜杠）
                save_path = os.path.join(save_path, sanitized_name)  # 自动处理路径分隔符

                # d. 保存文件（增加异常处理）
                save_success = False
                try:
                    with open(save_path, 'wb') as g:
                        g.write(response.content)
                    save_success = True
                    logger.info(f"{filename}返回的异常文件已保存，保存路径为：{save_path}")
                except Exception as e:
                    logger.warning(f"保存文件失败: {str(e)}")
                    raise f"保存异常文件失败"
                if save_success:
                    # 3. 断言
                    abnormal_sheet_name = case['abnormal_sheet_name']
                    abnormal_row_index = int(case['abnormal_row_index'])
                    comment_data = get_row_all_comments(save_path, abnormal_sheet_name, abnormal_row_index)
                    try:
                        self.assertIn(expect_data, comment_data.values())
                    except Exception as e:
                        logger.exception(f'{case['title']}：：测试失败')
                        logger.exception(f'请求数据是{request_data}')
                        logger.exception(f'期望结果是{abnormal_row_index}行有批注：{expect_data}')
                        logger.exception(f'实际结果是{comment_data}')
                        raise e




if __name__ == '__main__':
    unittest.main(testRunner=unittest.TextTestRunner())  # 显式指定测试运行器